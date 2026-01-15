
#E:\MAWDSLEYS-AGENTE\backend\core\events\event_logger.py

from core.events.activity_log import ActivityEvent


class EventLogger:
    def __init__(self, repository):
        self.repository = repository

    async def log(self, event: ActivityEvent):
        await self.repository.save(event)
        return event
