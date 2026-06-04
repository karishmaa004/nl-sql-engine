import requests
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

def call_api(prompt):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "openrouter/free",
            "messages": [{"role": "user", "content": prompt}]
        }),
        timeout=30
    )
    result = response.json()
    if "choices" not in result:
        err = result.get("error", {})
        raise ValueError(err.get("message", json.dumps(result)))
    return result["choices"][0]["message"]["content"].strip()

def clean_sql(sql):
    sql = sql.replace("```sql", "").replace("```", "").strip()

    for line in sql.splitlines():
        line = line.strip()
        if re.match(r"^SELECT\b", line, re.IGNORECASE):
            sql = line
            break

    sql = re.sub(r'\bSELECT(\w)', r'SELECT \1', sql)

    for kw in ["FROM", "WHERE", "JOIN", "GROUP", "ORDER", "HAVING", "LIMIT"]:
        sql = re.sub(r'([a-zA-Z_0-9()])(' + kw + r')\b', r'\1 \2', sql)
    for kw in ["SELECT", "FROM", "WHERE", "AND", "OR"]:
        sql = re.sub(r'\b(' + kw + r')(\w)', r'\1 \2', sql)

    def lower_where(m):
        return f"WHERE LOWER({m.group(1)}) = LOWER('{m.group(2)}')"
    def lower_cond(m):
        return f"{m.group(1)} LOWER({m.group(2)}) = LOWER('{m.group(3)}')"

    sql = re.sub(r"WHERE\s+(\w+)\s*=\s*'([^']+)'", lower_where, sql, flags=re.IGNORECASE)
    sql = re.sub(r"(AND|OR)\s+(\w+)\s*=\s*'([^']+)'", lower_cond, sql, flags=re.IGNORECASE)

    return sql.strip().rstrip(";") + ";"

def generate_sql(question, table_name="uploaded_data", columns=None):
    cols_str = ", ".join(columns) if columns else "*"

    prompt = f"""You are an expert SQLite query writer.

Table: {table_name}
Columns: {cols_str}

Write a single valid SQLite SELECT query to answer: "{question}"

Rules:
- Use ONLY table: {table_name} and columns: {cols_str}
- Always put spaces between all SQL keywords and identifiers
- Use LOWER() for string comparisons: WHERE LOWER(name) = LOWER('value')
- Return ONLY the raw SQL query. No explanation. No markdown. No backticks."""

    try:
        raw = call_api(prompt)
        return clean_sql(raw)
    except Exception as e:
        raise ValueError(str(e))