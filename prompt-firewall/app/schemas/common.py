from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, Field

class HistoryMessage(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    
class TargetModel(BaseModel):
    provider: str
    model: str
    
class ChannelText(BaseModel):
    channel_id: str = Field(description="Unique identifier for the channel (e.g. 'prompt', 'history_0')")
    source_type: str = Field(description="USER, SYSTEM, etc.")
    text: str = Field(description="The actual text content to be scanned")
    source_ref: Optional[str] = None
    trust_level: int = Field(default=0, description="0=untrusted, 2=trusted")
    
    @property
    def is_trusted(self) -> bool:
        return self.trust_level >= 2
