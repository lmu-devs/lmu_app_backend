from sqlalchemy.orm import Session
from shared.src.core.logging import get_food_logger

logger = get_food_logger(__name__)

class HomeService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_home_data(self):
        # Hardcoded data for now
        return {
            "submissionFee": "10€",
            "lectureFreeTime": "12.10 - 12.02",
            "lectureTime": "12.02 - 13.03",
            "links": [
                {"title": "LMU", "url": "https://www.lmu.de"},
                {"title": "LMU", "url": "https://www.lmu.de"},
                {"title": "LMU", "url": "https://www.lmu.de"},
            ]
        }