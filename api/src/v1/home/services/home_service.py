from sqlalchemy.orm import Session
from shared.src.core.logging import get_food_logger

logger = get_food_logger(__name__)

class HomeService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_home_data(self):
        # Hardcoded data for now
        return {
            "submissionFee": "8.02.25: 85,00€",
            "lectureFreeTime": "14.10.24 - 7.02.25",
            "lectureTime": "7.02.25 - 23.04.25",
            "links": [
                {"title": "LMU-Portal", "url": "https://www.lmu.de/lmu-intern/"},
                {"title": "Moodle", "url": "https://moodle.lmu.de/"},
                {"title": "Raumfinder", "url": "https://www.lmu.de/raumfinder/#/"},
                {"title": "Immatrikulation", "url": "https://qissos.verwaltung.uni-muenchen.de/qisserversos/rds?state=change&type=1&moduleParameter=studentReportsMenu&nextdir=change&next=menu.vm&xml=menu&purge=y&subdir=qissos/reports&menuid=qissosreportsPublish&breadcrumb=qissosreports&breadCrumbSource=menu"},
                {"title": "LMU-Mail", "url": "https://mailbox.portal.uni-muenchen.de/webmail/webmail/ui/MainPage.html"},
                {"title": "Beitragskonto", "url": "https://qissos.verwaltung.uni-muenchen.de/qisserversos/rds?state=gebkonto&asi=a$Lx1jxFA$kMP5tPiuVP"},
                {"title": "Benutzerkonto", "url": "https://www.portal.uni-muenchen.de/benutzerkonto/#!/"},
            ]
        }