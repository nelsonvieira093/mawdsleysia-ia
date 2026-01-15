from sqlalchemy.orm import Session
from db.models.sla_config import SLAConfig


class SLAEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_sla(self, client_id: int, alert_type: str) -> int:
        sla = (
            self.db.query(SLAConfig)
            .filter(
                SLAConfig.client_id == client_id,
                SLAConfig.alert_type == alert_type
            )
            .first()
        )

        # fallback seguro (nunca quebra automação)
        return sla.max_minutes if sla else 15
