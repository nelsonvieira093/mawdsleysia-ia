"""
ICS Generator — PRODUÇÃO
Compatível com Google / Outlook / Apple
"""

from datetime import datetime
from uuid import uuid4


def generate_meeting_ics(
    *,
    meeting_id: int,
    title: str,
    description: str,
    start_at: datetime,
    end_at: datetime,
    organizer_email: str,
    attendees_emails: list[str],
) -> bytes:

    uid = f"{meeting_id}-{uuid4()}@mawdsleys.ai"

    def fmt(dt: datetime) -> str:
        return dt.strftime("%Y%m%dT%H%M%SZ")

    attendees = "\n".join(
        f"ATTENDEE;CN={email};RSVP=TRUE:MAILTO:{email}"
        for email in attendees_emails
    )

    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//MAWDSLEYS IA//EN
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{fmt(datetime.utcnow())}
DTSTART:{fmt(start_at)}
DTEND:{fmt(end_at)}
SUMMARY:{title}
DESCRIPTION:{description}
ORGANIZER:MAILTO:{organizer_email}
{attendees}
END:VEVENT
END:VCALENDAR
"""
    return ics.encode("utf-8")
