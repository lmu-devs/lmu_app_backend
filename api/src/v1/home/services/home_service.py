from datetime import datetime
from sqlalchemy.orm import Session
from api.src.v1.home.models.home_model import Home, Link, SemesterFee, TimePeriod
from shared.src.core.logging import get_food_logger

logger = get_food_logger(__name__)

class HomeService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_semester_fee(self):
        return SemesterFee(
            fee=85.00,
            receiver="LMU München",
            iban="DE54 7005 0000 3701 1903 15",
            bic="BYLADEMM",
            reference="Matrikelnr/20251/LMU Rueckmeldung SoSe 2025",
            time_period=TimePeriod(
                start_date=datetime(2024, 12, 4), 
                end_date=datetime(2025, 2, 8)
                )
            )
        
    
    async def get_home_data(self):
        # Hardcoded data for now
        return Home(
            semester_fee=self.get_semester_fee(),
            lecture_free_time=TimePeriod(
                start_date=datetime(2024, 10, 14), 
                end_date=datetime(2025, 2, 7)
            ),
            lecture_time=TimePeriod(
                start_date=datetime(2025, 2, 7), 
                end_date=datetime(2025, 4, 23)
            ),
            links=[
                Link(title="LMU-Portal", url="https://www.lmu.de/lmu-intern/"),
                Link(title="Moodle", url="https://moodle.lmu.de/"),
                Link(title="Raumfinder", url="https://www.lmu.de/raumfinder/#/"),
                Link(title="Immatrikulation", url="https://qissos.verwaltung.uni-muenchen.de/qisserversos/rds?state=change&type=1&moduleParameter=studentReportsMenu&nextdir=change&next=menu.vm&xml=menu&purge=y&subdir=qissos/reports&menuid=qissosreportsPublish&breadcrumb=qissosreports&breadCrumbSource=menu"),
                Link(title="LMU-Mail", url="https://mailbox.portal.uni-muenchen.de/webmail/webmail/ui/MainPage.html"),
                Link(title="Beitragskonto", url="https://qissos.verwaltung.uni-muenchen.de/qisserversos/rds?state=gebkonto&asi=a$Lx1jxFA$kMP5tPiuVP"),
                Link(title="Benutzerkonto", url="https://www.portal.uni-muenchen.de/benutzerkonto/#!/"),
            ]
        )