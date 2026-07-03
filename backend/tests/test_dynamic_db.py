import pytest
import os
import uuid
import sqlite3
import dynamic_db

@pytest.fixture
def temp_db():
    filename = f"test_{uuid.uuid4().hex}.db"
    filepath = dynamic_db.get_db_path(filename)
    # Ensure dir exists
    os.makedirs(dynamic_db.USER_DB_DIR, exist_ok=True)
    yield filename
    if os.path.exists(filepath):
        os.remove(filepath)

def test_create_and_get_tables(temp_db):
    columns = [
        {"name": "name", "type": "TEXT"}
    ]
    dynamic_db.create_table(temp_db, "users", columns)
    
    tables = dynamic_db.get_tables(temp_db)
    assert "users" in tables
    assert "sqlite_sequence" not in tables

def test_add_and_get_columns(temp_db):
    columns = []
    dynamic_db.create_table(temp_db, "items", columns)
    
    dynamic_db.add_column(temp_db, "items", "description", "TEXT")
    
    cols = dynamic_db.get_columns(temp_db, "items")
    col_names = [c["name"] for c in cols]
    assert "id" in col_names
    assert "description" in col_names

def test_crud_rows(temp_db):
    columns = [
        {"name": "name", "type": "TEXT"},
        {"name": "price", "type": "REAL"}
    ]
    dynamic_db.create_table(temp_db, "products", columns)
    
    # Create
    row_data = {"name": "Apple", "price": 1.99}
    row_id = dynamic_db.add_row(temp_db, "products", row_data)
    assert row_id is not None
    
    # Read
    rows = dynamic_db.get_rows(temp_db, "products")
    assert len(rows) == 1
    assert rows[0]["name"] == "Apple"
    assert rows[0]["price"] == 1.99
    
    # Update
    dynamic_db.update_row(temp_db, "products", row_id, {"price": 2.50})
    rows = dynamic_db.get_rows(temp_db, "products")
    assert rows[0]["price"] == 2.50
    
    # Delete
    dynamic_db.delete_row(temp_db, "products", row_id)
    rows = dynamic_db.get_rows(temp_db, "products")
    assert len(rows) == 0

def test_drop_table(temp_db):
    dynamic_db.create_table(temp_db, "temp_table", [])
    assert "temp_table" in dynamic_db.get_tables(temp_db)
    
    dynamic_db.drop_table(temp_db, "temp_table")
    assert "temp_table" not in dynamic_db.get_tables(temp_db)
