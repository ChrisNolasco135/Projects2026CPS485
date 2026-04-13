import sqlite3
import re
from openai import AsyncOpenAI
import dynamic_db
import os
from dotenv import load_dotenv

load_dotenv() 

AI_BASE_URL = "https://gpt.hydra.newpaltz.edu/api/v1" 
AI_MODEL = "deepseek-coder-v2:16b"
API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = AsyncOpenAI(base_url=AI_BASE_URL, api_key=API_KEY)

def get_database_schema(filename: str) -> str:
    """Introspects the user's DB to build a context string for the AI."""
    tables = dynamic_db.get_tables(filename)
    schema_str = "Database Schema:\n"
    
    for table in tables:
        columns = dynamic_db.get_columns(filename, table)
        col_defs = [f"{col['name']} ({col['type']})" for col in columns]
        schema_str += f"Table '{table}': {', '.join(col_defs)}\n"
        
    return schema_str

async def generate_sql(schema: str, user_question: str) -> str:
    """Sends the schema and question to DeepSeek to get SQL."""
    system_prompt = f"""
    You are an expert SQLite database assistant.
    Given the following database schema, write a SQL query to answer the user's question.
    {schema}
    
    RULES:
    1. Return ONLY the raw SQL query.
    2. Do NOT wrap the SQL in markdown formatting (like ```sql).
    3. ONLY generate SELECT statements. Never UPDATE, INSERT, or DROP.
    """
    
    response = await client.chat.completions.create(
        model=AI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0.1 # Low temperature for logical precision
    )
    
    raw_sql = response.choices[0].message.content.strip()
    
    # Clean up markdown if the model disobeys the rule
    raw_sql = re.sub(r"^```sql\n|```$", "", raw_sql).strip()
    return raw_sql

def execute_read_only_sql(filename: str, sql: str) -> list[dict]:
    """Safely executes the AI-generated SQL."""
    if not sql.upper().strip().startswith("SELECT"):
        raise ValueError("Security Violation: AI generated a non-SELECT query.")
        
    filepath = dynamic_db.get_db_path(filename)
    conn = sqlite3.connect(filepath)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    finally:
        conn.close()