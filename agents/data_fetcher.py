import logging
from monitor import datafetcher_called, datafetcher_latency, datafetcher_errors

class DataFetcherAgent:
    """Fetches KYC documents from Oracle DB for a given customer."""

    def __init__(self, oracle_client):
        self.oracle_client = oracle_client
        self.logger = logging.getLogger("DataFetcherAgent")

    def __call__(self, context):
        datafetcher_called.inc()
        with datafetcher_latency.time():
            try:
                customer_id = context["txn"]["customer_id"]
                docs = self.oracle_client.get_kyc_docs(customer_id)
                context["kyc_docs"] = docs
                self.logger.info(f"KYC docs for {customer_id}: {docs}")
            except Exception as e:
                datafetcher_errors.inc()
                self.logger.error(f"DataFetcher error: {e}")
                context["data_fetch_error"] = str(e)
                context["error"] = True
        return context
