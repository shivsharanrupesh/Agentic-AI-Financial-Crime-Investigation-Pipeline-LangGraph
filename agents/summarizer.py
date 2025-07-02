import logging
from monitor import summarizer_called, summarizer_latency, summarizer_errors

class SummarizerAgent:
    """Uses an LLM API to generate a compliance-ready summary."""

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.logger = logging.getLogger("SummarizerAgent")

    def __call__(self, context):
        summarizer_called.inc()
        with summarizer_latency.time():
            try:
                prompt = self._build_prompt(context)
                summary = self.llm_client.summarize(prompt)
                context["summary"] = summary
                self.logger.info("LLM summary generated.")
            except Exception as e:
                summarizer_errors.inc()
                self.logger.error(f"LLM summarization failed: {e}")
                context["summarize_error"] = str(e)
                context["error"] = True
        return context

    def _build_prompt(self, context):
        txn = context["txn"]
        flag_reasons = context.get("flag_reasons", [])
        kyc_docs = context.get("kyc_docs", [])
        risk_score = context.get("risk_score", "N/A")
        prompt = (
            f"Transaction: {txn}\n"
            f"Flagged Reasons: {flag_reasons}\n"
            f"KYC Docs: {kyc_docs}\n"
            f"Risk Score: {risk_score}\n"
            "Write a case summary for compliance review."
        )
        return prompt
