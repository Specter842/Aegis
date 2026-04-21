from app.services.normalizer import NormalizerService
from app.schemas.scan import ScanRequest
from app.schemas.common import HistoryMessage

def test_normalize_basic_prompt():
    svc = NormalizerService()
    req = ScanRequest(
        request_id="1", tenant_id="t", app_id="a", user_id="u",
        prompt="hello \x00world"
    )
    channels = svc.normalize_request(req)
    assert len(channels) == 1
    assert channels[0].channel_id == "prompt"
    assert channels[0].source_type == "user"
    assert channels[0].text == "hello world" # null byte stripped
    assert not channels[0].is_trusted
    
def test_normalize_history_trust():
    svc = NormalizerService()
    req = ScanRequest(
        request_id="1", tenant_id="t", app_id="a", user_id="u",
        prompt="do it",
        history=[
            HistoryMessage(role="user", content="something"),
            HistoryMessage(role="system", content="you are helpful")
        ]
    )
    channels = svc.normalize_request(req)
    assert len(channels) == 3
    assert not channels[1].is_trusted # user
    assert channels[2].is_trusted # system
