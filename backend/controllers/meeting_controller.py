from sqlalchemy.orm import Session

from db.models.meeting import Meeting
from services.email_service import EmailService
from services.calendar_ics import generate_meeting_ics
from db.repositories.activity_log_repository import ActivityLogRepository
from core.events.activity_log import ActivityEvent


class MeetingController:

    @staticmethod
    def send_invite(
        *,
        db: Session,
        meeting_id: int,
        user_id: int,
    ):
        meeting = db.get(Meeting, meeting_id)
        if not meeting:
            return None

        ics = generate_meeting_ics(
            meeting_id=meeting.id,
            title=meeting.title,
            description=meeting.description or "",
            start_at=meeting.start_at,
            end_at=meeting.end_at,
            organizer_email=meeting.organizer_email,
            attendees_emails=meeting.attendees,
        )

        EmailService.send_email(
            subject=f"Convite: {meeting.title}",
            body="Você foi convidado para uma reunião.",
            to=meeting.attendees,
            attachments=[("convite.ics", ics, "text/calendar")],
        )

        ActivityLogRepository.log(
            db,
            ActivityEvent(
                type="meeting",
                action="invite_sent",
                entity=f"meeting:{meeting.id}",
                user_id=user_id,
                details="Convite de reunião enviado",
            ),
        )

        return {"status": "sent", "meeting_id": meeting.id}
