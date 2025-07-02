import logging
import os
import pandas as pd
from langgraph.graph import StateGraph
from config import CONFIG
from real_clients import OracleClient, MLModel, OpenAIClient
from monitor import setup_logging, start_metrics_server, transactions_processed, transactions_flagged, pipeline_latency

from agents.rule_agent import RuleAgent
from agents.data_fetcher import DataFetcherAgent
from agents.ml_scorer import MLScorerAgent
from agents.summarizer import SummarizerAgent
from agents.case_manager import CaseManagerAgent
from agents.escalate_agent import EscalateAgent

def build_workflow(oracle_client, ml_model, llm_client):
    rule_agent = RuleAgent(CONFIG)
    data_fetcher = DataFetcherAgent(oracle_client)
    ml_scorer = MLScorerAgent(ml_model)
    summarizer = SummarizerAgent(llm_client)
    case_manager = CaseManagerAgent()
    escalate_agent = EscalateAgent()

    workflow = StateGraph(name="FinancialCrimeInvestigation")

    workflow.add_node("rule_agent", rule_agent)
    workflow.add_node("data_fetcher_agent", data_fetcher)
    workflow.add_node("ml_scorer_agent", ml_scorer)
    workflow.add_node("summarizer_agent", summarizer)
    workflow.add_node("case_manager_agent", case_manager)
    workflow.add_node("escalate_agent", escalate_agent)

    workflow.add_edge("rule_agent", "data_fetcher_agent", condition=lambda ctx: ctx.get("flagged", False))
    workflow.add_edge("rule_agent", "case_manager_agent", condition=lambda ctx: not ctx.get("flagged", False))
    workflow.add_edge("data_fetcher_agent", "ml_scorer_agent", condition=lambda ctx: not ctx.get("error", False))
    workflow.add_edge("data_fetcher_agent", "escalate_agent", condition=lambda ctx: ctx.get("error", False))
    workflow.add_edge("ml_scorer_agent", "summarizer_agent", condition=lambda ctx: not ctx.get("error", False))
    workflow.add_edge("ml_scorer_agent", "escalate_agent", condition=lambda ctx: ctx.get("error", False))
    workflow.add_edge("summarizer_agent", "case_manager_agent", condition=lambda ctx: not ctx.get("error", False))
    workflow.add_edge("summarizer_agent", "escalate_agent", condition=lambda ctx: ctx.get("error", False))
    workflow.add_edge("case_manager_agent", "END")
    workflow.add_edge("escalate_agent", "END")

    workflow.set_entry("rule_agent")
    return workflow

if __name__ == "__main__":
    setup_logging()
    start_metrics_server(port=8000)

    oracle_client = OracleClient(
        host=os.environ.get("ORACLE_HOST"),
        port=os.environ.get("ORACLE_PORT"),
        service=os.environ.get("ORACLE_SERVICE"),
        user=os.environ.get("ORACLE_USER"),
        password=os.environ.get("ORACLE_PASSWORD")
    )
    ml_model = MLModel(model_path="model.joblib")
    llm_client = OpenAIClient(api_key=os.environ.get("OPENAI_API_KEY"))
    workflow = build_workflow(oracle_client, ml_model, llm_client)

    # Updated path to CSV inside the test_data folder
    df = pd.read_csv("test_data/transactions.csv")
    for _, row in df.iterrows():
        txn = row.to_dict()
        context = {"txn": txn}
        with pipeline_latency.time():
            result = workflow.run(context)
        transactions_processed.inc()
        if result.get("flagged"):
            transactions_flagged.inc()
        print("Final result:", result)
