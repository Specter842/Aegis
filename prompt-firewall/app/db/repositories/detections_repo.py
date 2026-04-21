from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import ScanDetectionModel

class DetectionsRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    def add_many(self, detections_data: list[dict]):
        for row in detections_data:
            model = ScanDetectionModel(**row)
            self.session.add(model)
