# E:\MAWDSLEYS-AGENTE\backend\core\memory\insight_engine.py

from collections import Counter


class InsightEngine:
    def __init__(self, events):
        self.events = events

    def followup_pressure(self):
        followups = [
            e for e in self.events
            if e.entity == "followup"
        ]

        owners = [
            e.payload.get("responsible")
            for e in followups
            if e.payload.get("responsible")
        ]

        counter = Counter(owners)
        critical = {
            k: v for k, v in counter.items() if v >= 3
        }

        return critical

    def regulatory_risks(self):
        return [
            e for e in self.events
            if "regulator" in str(e.payload).lower()
            or "anvisa" in str(e.payload).lower()
        ]

    def meeting_overload(self):
        meetings = [
            e for e in self.events
            if e.type == "meeting.created"
        ]

        return len(meetings)
