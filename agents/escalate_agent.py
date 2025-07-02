import logging
from monitor import escalate_called, escalate_latency

class EscalateAgent:
    """Handles errors, logs issues, and escalates for manual review."""

    def __init__(self):
        self.logger = logging.getLogger("EscalateAgent")

    def __call__(self, context):
        escalate_called.inc()
        with escalate_latency.time():
            self.logger.error(f"Escalating for manual review: {context}")
            context["case_status"] = "escalated_due_to_error"
        return context
