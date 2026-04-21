from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ScanChannelModel

class ChannelsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    def add(self, channel_data: dict) -> ScanChannelModel:
        model = ScanChannelModel(**channel_data)
        self.session.add(model)
        return model
