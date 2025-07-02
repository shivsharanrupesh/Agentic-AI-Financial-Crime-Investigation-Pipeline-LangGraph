import logging
from monitor import casemanager_called, casemanager_latency, cases_closed, cases_escalated

class CaseManagerAgent:
    """Manages case creation, closure, and escalation."""

    def __init__(self):
        self.logger = logging.getLogger("CaseManagerAgent")

    def __call__(self, context):
        casemanager_called.inc()
        with casemanager_latency.time():
            risk_score = context.get("risk_score", 0)
            if risk_score < 0.5:
                context["case_status"] = "closed"
                cases_closed.inc()
                self.logger.info(f"Case auto-closed for transaction {context['txn']['id']}")
            else:
                context["case_status"] = "escalated"
                cases_escalated.inc()
                self.logger.warning(f"Case escalated for transaction {context['txn']['id']}")
        return context
