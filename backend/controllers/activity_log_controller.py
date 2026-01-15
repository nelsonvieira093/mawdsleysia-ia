# E:\MAWDSLEYS-AGENTE\backend\controllers\activity_log_controller.py

from sqlalchemy.orm import Session
from db.repositories.activity_log_repository import ActivityLogRepository


class ActivityLogController:

    @staticmethod
    def list_user_logs(db: Session, user_id: int):
        return ActivityLogRepository.list_by_user(db, user_id)

    @staticmethod
    def get_log(db: Session, log_id: int, user_id: int):
        log = ActivityLogRepository.get_by_id(db, log_id)
        if not log or log.user_id != user_id:
            return None
        return log
