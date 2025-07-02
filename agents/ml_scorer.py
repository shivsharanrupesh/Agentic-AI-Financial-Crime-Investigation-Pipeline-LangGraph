import logging
from monitor import mlscorer_called, mlscorer_latency, mlscorer_errors

class MLScorerAgent:
    """Assigns a risk score to a transaction using an ML model."""

    def __init__(self, model):
        self.model = model
        self.logger = logging.getLogger("MLScorerAgent")

    def __call__(self, context):
        mlscorer_called.inc()
        with mlscorer_latency.time():
            try:
                txn = context["txn"]
                features = [txn["amount"]]
                score = self.model.predict_proba([features])[0][1]
                context["risk_score"] = score
                self.logger.info(f"ML risk score: {score}")
            except Exception as e:
                mlscorer_errors.inc()
                self.logger.error(f"ML scoring failed: {e}")
                context["ml_score_error"] = str(e)
                context["error"] = True
        return context
