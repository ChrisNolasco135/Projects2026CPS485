import pytest
import sqlite3
import ai_agent
import dynamic_db
from test_dynamic_db import temp_db # reuse the fixture

@pytest.mark.asyncio
async def test_generate_sql(temp_db):
    # Setup some basic schema
    dynamic_db.create_table(temp_db, "employees", [
        {"name": "name", "type": "TEXT"},
        {"name": "salary", "type": "REAL"}
    ])
    
    schema = ai_agent.get_database_schema(temp_db)
    assert "employees" in schema
    assert "salary" in schema
    
    # Real API call
    sql = await ai_agent.generate_sql(schema, "What is the average salary of all employees?")
    assert "SELECT" in sql.upper()
    assert "AVG(salary)" in sql.upper() or "AVG(" in sql.upper()
    
def test_execute_read_only_sql(temp_db):
    dynamic_db.create_table(temp_db, "dummy", [
        {"name": "val", "type": "INTEGER"}
    ])
    dynamic_db.add_row(temp_db, "dummy", {"val": 42})
    
    # Should work
    results = ai_agent.execute_read_only_sql(temp_db, "SELECT * FROM dummy")
    assert len(results) == 1
    assert results[0]["val"] == 42
    
    # App level block
    with pytest.raises(ValueError, match="Security Violation"):
        ai_agent.execute_read_only_sql(temp_db, "UPDATE dummy SET val = 100")
        
    # Test DB level readonly 
    filepath = dynamic_db.get_db_path(temp_db)
    conn = sqlite3.connect(f"file:{filepath}?mode=ro", uri=True)
    with pytest.raises(sqlite3.OperationalError, match="attempt to write a readonly database"):
        conn.execute("UPDATE dummy SET val = 100")
    conn.close()
