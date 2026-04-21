import pytest
from app.scanners.static.unicode_scanner import UnicodeScanner
from app.schemas.common import ChannelText

@pytest.mark.asyncio
async def test_zero_width_chars():
    scanner = UnicodeScanner()
    # \u200b is zero-width space
    channel = ChannelText(channel_id="c1", source_type="user", text="hello\u200bworld")
    detections = await scanner.scan(channel)
    assert len(detections) == 1
    assert detections[0].attack_type == "unicode_obfuscation"
    assert detections[0].sanitized_text == "helloworld"
