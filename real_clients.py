import os
import oracledb  # pip install oracledb
import joblib    # pip install joblib
import requests
import openai    # pip install openai
import cohere    # pip install cohere

class OracleClient:
    """Production Oracle DB client for fetching KYC documents."""
    def __init__(self, host, port, service, user, password):
        dsn = oracledb.makedsn(host, port, service_name=service)
        self.conn = oracledb.connect(user=user, password=password, dsn=dsn)

    def get_kyc_docs(self, customer_id):
        cur = self.conn.cursor()
        cur.execute("SELECT doc_name FROM kyc_documents WHERE customer_id = :id", id=customer_id)
        docs = [row[0] for row in cur.fetchall()]
        cur.close()
        return docs

class MLModel:
    """Loads and uses a trained scikit-learn model for risk scoring."""
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def predict_proba(self, X):
        return self.model.predict_proba(X)

class MLAPIModel:
    """Calls an ML model endpoint (REST API) for risk scoring."""
    def __init__(self, endpoint, api_key):
        self.endpoint = endpoint
        self.api_key = api_key

    def predict_proba(self, X):
        payload = {"instances": X}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = requests.post(self.endpoint, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()["predictions"]

class OpenAIClient:
    """Uses OpenAI API (GPT-4) for case summarization."""
    def __init__(self, api_key, model="gpt-4-turbo"):
        openai.api_key = api_key
        self.model = model

    def summarize(self, prompt):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a compliance analyst. Write concise, audit-ready summaries."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=512,
            temperature=0.2,
        )
        return response.choices[0].message["content"].strip()

class CohereClient:
    """Uses Cohere LLM for case summarization."""
    def __init__(self, api_key, model="command"):
        self.co = cohere.Client(api_key)
        self.model = model

    def summarize(self, prompt):
        response = self.co.generate(
            model=self.model,
            prompt=prompt,
            max_tokens=400,
            temperature=0.3,
        )
        return response.generations[0].text.strip()
