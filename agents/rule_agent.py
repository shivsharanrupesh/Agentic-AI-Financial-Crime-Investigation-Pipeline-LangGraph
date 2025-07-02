import logging
from monitor import rule_agent_called, rule_agent_flagged, rule_agent_latency

class RuleAgent:
    """Applies business rules to flag suspicious transactions."""

    def __init__(self, config):
        self.rules = config.get("rules", {})
        self.logger = logging.getLogger("RuleAgent")

    def __call__(self, context):
        rule_agent_called.inc()
        with rule_agent_latency.time():
            txn = context["txn"]
            reasons = []

            amount_threshold = self.rules.get("amount_threshold", 10000)
            if txn.get("amount", 0) >= amount_threshold:
                reasons.append(f"Amount exceeds threshold: {txn['amount']} >= {amount_threshold}")

            high_risk_countries = self.rules.get("high_risk_countries", [])
            if txn.get("country") in high_risk_countries:
                reasons.append(f"Transaction from high-risk country: {txn['country']}")

            blacklisted_customers = self.rules.get("blacklisted_customers", [])
            if txn.get("customer_id") in blacklisted_customers:
                reasons.append(f"Blacklisted customer ID: {txn['customer_id']}")

            context["flagged"] = bool(reasons)
            context["flag_reasons"] = reasons
            if context["flagged"]:
                rule_agent_flagged.inc()
            self.logger.info(f"RuleAgent flagged: {context['flagged']} | reasons: {reasons}")
        return context
