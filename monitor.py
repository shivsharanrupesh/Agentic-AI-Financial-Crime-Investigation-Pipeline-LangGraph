from prometheus_client import Counter, Histogram, start_http_server

# Global pipeline metrics
transactions_processed = Counter('transactions_processed', 'Total transactions processed')
transactions_flagged = Counter('transactions_flagged', 'Total transactions flagged')
pipeline_latency = Histogram('pipeline_latency_seconds', 'Time taken for each pipeline run')

# RuleAgent
rule_agent_called = Counter('rule_agent_called', 'Times RuleAgent executed')
rule_agent_flagged = Counter('rule_agent_flagged', 'Times RuleAgent flagged a transaction')
rule_agent_latency = Histogram('rule_agent_latency_seconds', 'Time RuleAgent takes per execution')

# DataFetcherAgent
datafetcher_called = Counter('datafetcher_called', 'Times DataFetcherAgent executed')
datafetcher_latency = Histogram('datafetcher_latency_seconds', 'Time DataFetcherAgent takes per execution')
datafetcher_errors = Counter('datafetcher_errors', 'DataFetcherAgent error count')

# MLScorerAgent
mlscorer_called = Counter('mlscorer_called', 'Times MLScorerAgent executed')
mlscorer_latency = Histogram('mlscorer_latency_seconds', 'Time MLScorerAgent takes per execution')
mlscorer_errors = Counter('mlscorer_errors', 'MLScorerAgent error count')

# SummarizerAgent
summarizer_called = Counter('summarizer_called', 'Times SummarizerAgent executed')
summarizer_latency = Histogram('summarizer_latency_seconds', 'Time SummarizerAgent takes per execution')
summarizer_errors = Counter('summarizer_errors', 'SummarizerAgent error count')

# CaseManagerAgent
casemanager_called = Counter('casemanager_called', 'Times CaseManagerAgent executed')
cases_closed = Counter('cases_closed', 'Number of cases auto-closed')
cases_escalated = Counter('cases_escalated', 'Number of cases escalated')
casemanager_latency = Histogram('casemanager_latency_seconds', 'Time CaseManagerAgent takes per execution')

# EscalateAgent
escalate_called = Counter('escalate_called', 'Times EscalateAgent executed')
escalate_latency = Histogram('escalate_latency_seconds', 'Time EscalateAgent takes per execution')

def setup_logging():
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')

def start_metrics_server(port=8000):
    start_http_server(port)
    print(f"Prometheus metrics available on http://localhost:{port}/")
