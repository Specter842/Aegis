from fastapi import APIRouter, Depends
from app.schemas.proxy import ProxyChatRequest, ProxyChatResponse, ProviderErrorResponse
from app.services.routing_service import RoutingService
from app.api.deps import get_routing_service
from typing import Union

router = APIRouter(prefix="/v1/proxy", tags=["Proxy"])

@router.post("/chat", response_model=Union[ProxyChatResponse, ProviderErrorResponse])
async def proxy_chat_endpoint(req: ProxyChatRequest, orchestrator: RoutingService = Depends(get_routing_service)):
    return await orchestrator.proxy_chat(req)
