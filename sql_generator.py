import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_sql(question):

    schema = """
    Table: employees

    Columns:
    id
    name
    department
    salary
    """

    prompt = f"""
    You are an SQL expert.

    Convert the user's question into SQL.

    Database Schema:
    {schema}

    User Question:
    {question}

    Return ONLY the SQL query.
    """

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    )

    result = response.json()

    sql = result["choices"][0]["message"]["content"]

    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    return sql