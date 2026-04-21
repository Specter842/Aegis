from typing import Union
from app.schemas.proxy import ProxyChatRequest, ProxyChatResponse, ProviderErrorResponse
from app.schemas.output import OutputScanResult
from app.services.scan_orchestrator import ScanOrchestrator
from app.services.canary_service import CanaryService
from app.services.output_scan_service import OutputScanService
from app.services.event_service import EventService
from app.providers.base import ProviderException
from app.providers.openai_provider import OpenAIProvider
from app.db.repositories.output_repo import OutputRepo
from app.db.repositories.requests_repo import RequestsRepo
from app.db.models import OutputScanModel
from app.schemas.scan import ScanRequest

class RoutingService:
    def __init__(self, 
                 scan_orchestrator: ScanOrchestrator, 
                 canary_service: CanaryService,
                 output_scan_service: OutputScanService,
                 output_repo: OutputRepo,
                 requests_repo: RequestsRepo,
                 event_service: EventService):
        self.scan_orchestrator = scan_orchestrator
        self.canary_service = canary_service
        self.output_scan_service = output_scan_service
        self.output_repo = output_repo
        self.requests_repo = requests_repo
        self.event_service = event_service

    async def _get_provider(self, target_provider: str):
        if target_provider == "openai":
            return OpenAIProvider()
        raise ProviderException("config_failure", f"Unknown provider: {target_provider}")

    async def _get_request_fk(self, trace_id: str) -> int:
        req = await self.requests_repo.get_by_trace_id(trace_id)
        if req:
            return req.id
        return None

    async def proxy_chat(self, req: ProxyChatRequest) -> Union[ProxyChatResponse, ProviderErrorResponse]:
        # 1. Pre-LLM scan
        scan_req = ScanRequest(
            request_id=req.request_id,
            tenant_id=req.tenant_id,
            app_id=req.app_id,
            user_id=req.user_id,
            prompt=req.prompt,
            history=req.history
        )
        pre_result = await self.scan_orchestrator.process_scan(scan_req)

        if pre_result.decision in ["block", "challenge"]:
            return ProxyChatResponse(
                request_id=req.request_id,
                decision=pre_result.decision,
                risk_score=pre_result.risk_score,
                llm_called=False,
                reason="Pre-LLM security policy violation" 
            )

        # Get DB FK manually since persistence handles its own session briefly
        request_fk = await self._get_request_fk(pre_result.trace_id)

        # 2. Canary Injection
        token, modified_history = self.canary_service.inject_canary(req.history, req.prompt)
        
        # 3. Provider Call
        messages = modified_history + [{"role": "user", "content": req.prompt}]
        
        try:
            provider = await self._get_provider(req.target.provider)
            model_response = await provider.chat_completion(req.target.model, messages)
        except ProviderException as e:
            return ProviderErrorResponse(
                request_id=req.request_id,
                error_type=e.error_type,
                message=e.message,
                llm_called=True
            )

        raw_output = model_response.get("content", "")

        # 4. Post-LLM Scan
        out_result, detections, safe_excerpt, output_hash = await self.output_scan_service.process_output(
            pre_result.trace_id, raw_output, token
        )

        # 5. Record Canary
        await self.canary_service.record_canary_event(
            trace_id=pre_result.trace_id,
            request_fk=request_fk,
            token=token,
            provider=req.target.provider,
            model=req.target.model,
            leaked=out_result.canary_leaked,
            excerpt=safe_excerpt if out_result.canary_leaked else None
        )

        # 6. Record Output Scan
        await self.output_repo.create(OutputScanModel(
            trace_id=pre_result.trace_id,
            request_fk=request_fk,
            provider=req.target.provider,
            model=req.target.model,
            llm_called=True,
            output_action=out_result.action,
            block_reason="Output policy threshold exceeded" if out_result.blocked else None,
            safe_excerpt=safe_excerpt,
            output_hash=output_hash,
            risk_score=out_result.risk_score,
            blocked=out_result.blocked,
            canary_leaked=out_result.canary_leaked,
            secret_detected=out_result.secret_detected,
            pii_detected=out_result.pii_detected
        ))

        # 7. WebSockets
        if out_result.blocked:
            await self.event_service.emit_output_blocked(
                request_id=req.request_id,
                trace_id=pre_result.trace_id,
                detections=detections,
                action=out_result.action,
                provider=req.target.provider,
                model=req.target.model,
                safe_excerpt=safe_excerpt
            )

        # 8. Return
        if out_result.blocked:
            return ProxyChatResponse(
                request_id=req.request_id,
                decision="block",
                risk_score=max(pre_result.risk_score, out_result.risk_score),
                llm_called=True,
                model_response=None,
                output_scan=out_result,
                reason="Blocked by output policy"
            )

        # mutate safe output if truncated/redacted
        if out_result.action in ("truncate", "redact"):
            model_response["content"] = safe_excerpt

        return ProxyChatResponse(
            request_id=req.request_id,
            decision="allow",
            risk_score=max(pre_result.risk_score, out_result.risk_score),
            llm_called=True,
            model_response=model_response,
            output_scan=out_result
        )
