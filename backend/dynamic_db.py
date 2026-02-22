import sqlite3
import os
from typing import List, Dict, Any

USER_DB_DIR = "user_databases"

def get_db_path(filename: str) -> str:
    """Returns the full path to the user's database file."""
    return os.path.join(USER_DB_DIR, filename)

def create_db_file(filename: str):
    """Creates an empty SQLite database file."""
    filepath = get_db_path(filename)
    # Just connecting creates the file
    conn = sqlite3.connect(filepath)
    conn.close()

def delete_db_file(filename: str):
    """Deletes the SQLite database file."""
    filepath = get_db_path(filename)
    if os.path.exists(filepath):
        os.remove(filepath)

def get_tables(filename: str) -> List[str]:
    """Returns a list of table names in the database."""
    filepath = get_db_path(filename)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

def create_table(filename: str, table_name: str, columns: List[Dict[str, str]]):
    """
    Creates a new table.
    columns: List of dicts with 'name' and 'type'.
    """
    filepath = get_db_path(filename)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    
    # Basic sanitization for table name (alphanumeric + underscore)
    if not table_name.isidentifier():
        raise ValueError("Invalid table name")

    col_defs = []
    for col in columns:
        c_name = col['name']
        c_type = col['type'].upper()
        if not c_name.isidentifier():
             raise ValueError(f"Invalid column name: {c_name}")
        # Allow only basic types for safety
        if c_type not in ['TEXT', 'INTEGER', 'REAL', 'BLOB', 'NULL']:
             # Default to TEXT if unknown or use as is if we want flexibility?
             # Let's enforce SQLite types.
             c_type = 'TEXT' 
        col_defs.append(f"{c_name} {c_type}")
    
    # Always add a primary key ID
    col_defs.insert(0, "id INTEGER PRIMARY KEY AUTOINCREMENT")
    
    create_stmt = f"CREATE TABLE {table_name} ({', '.join(col_defs)});"
    cursor.execute(create_stmt)
    conn.commit()
    conn.close()

def drop_table(filename: str, table_name: str):
    """Drops a table."""
    filepath = get_db_path(filename)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    if not table_name.isidentifier():
        raise ValueError("Invalid table name")
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    conn.commit()
    conn.close()

def get_columns(filename: str, table_name: str) -> List[Dict[str, str]]:
    """Returns columns of a table."""
    filepath = get_db_path(filename)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    if not table_name.isidentifier():
        raise ValueError("Invalid table name")
    
    # PRAGMA table_info returns: cid, name, type, notnull, dflt_value, pk
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = []
    for col in cursor.fetchall():
        columns.append({"name": col[1], "type": col[2], "pk": bool(col[5])})
    conn.close()
    return columns

def add_column(filename: str, table_name: str, column_name: str, column_type: str):
    """Adds a column to a table."""
    filepath = get_db_path(filename)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    
    if not table_name.isidentifier() or not column_name.isidentifier():
        raise ValueError("Invalid names")
    
    if column_type.upper() not in ['TEXT', 'INTEGER', 'REAL', 'BLOB', 'NULL']:
         column_type = 'TEXT'

    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type};")
    conn.commit()
    conn.close()

def drop_column(filename: str, table_name: str, column_name: str):
    """Drops a column from a table."""
    filepath = get_db_path(filename)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    
    if not table_name.isidentifier() or not column_name.isidentifier():
        raise ValueError("Invalid names")
        
    # SQLite support for DROP COLUMN varies, but assuming modern version
    try:
        cursor.execute(f"ALTER TABLE {table_name} DROP COLUMN {column_name};")
        conn.commit()
    except sqlite3.OperationalError as e:
        conn.close()
        raise ValueError(f"Could not drop column (SQLite version might be old): {e}")
    
    conn.close()

def get_rows(filename: str, table_name: str) -> List[Dict[str, Any]]:
    """Returns all rows from a table."""
    filepath = get_db_path(filename)
    conn = sqlite3.connect(filepath)
    # Return rows as dicts
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if not table_name.isidentifier():
        raise ValueError("Invalid table name")
        
    try:
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError as e:
        conn.close()
        if "no such table" in str(e):
             raise ValueError(f"Table '{table_name}' not found")
        raise e
        
    conn.close()
    return rows

def add_row(filename: str, table_name: str, data: Dict[str, Any]):
    """Adds a row to a table."""
    filepath = get_db_path(filename)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    
    if not table_name.isidentifier():
        raise ValueError("Invalid table name")
    
    # Filter data to only valid columns
    try:
        cursor.execute(f"PRAGMA table_info({table_name});")
    except sqlite3.OperationalError as e:
        conn.close()
        raise e # PRAGMA shouldn't fail even if table missing (returns empty), but just in case
        
    # Check if table exists by seeing if we got any columns (or check master)
    # PRAGMA table_info returns empty list if table doesn't exist
    columns_info = cursor.fetchall()
    if not columns_info:
         conn.close()
         raise ValueError(f"Table '{table_name}' not found")

    valid_columns = {row[1] for row in columns_info}
    
    filtered_data = {k: v for k, v in data.items() if k in valid_columns}
    
    if not filtered_data:
        # If filtered_data is empty but data was not, it means all keys were invalid.
        if data and not filtered_data:
             raise ValueError("No valid columns provided")
        
    columns = list(filtered_data.keys())
    placeholders = ["?"] * len(columns)
    values = list(filtered_data.values())

    if not columns:
        # If no columns to insert (e.g. all defaults), use DEFAULT VALUES
        query = f"INSERT INTO {table_name} DEFAULT VALUES;"
        cursor.execute(query)
    else:
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)});"
        cursor.execute(query, values)
        
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id

def delete_row(filename: str, table_name: str, row_id: int):
    """Deletes a row by ID."""
    filepath = get_db_path(filename)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()
    
    if not table_name.isidentifier():
        raise ValueError("Invalid table name")
        
    try:
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?;", (row_id,))
        conn.commit()
    except sqlite3.OperationalError as e:
        conn.close()
        if "no such table" in str(e):
             raise ValueError(f"Table '{table_name}' not found")
        raise e
        
    conn.close()

def update_row(filename: str, table_name: str, row_id: int, data: Dict[str, Any]):
    """Updates a row."""
    filepath = get_db_path(filename)
    conn = sqlite3.connect(filepath)
    cursor = conn.cursor()

    if not table_name.isidentifier():
        raise ValueError("Invalid table name")

    # Filter data to only valid columns
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns_info = cursor.fetchall()
    if not columns_info:
         conn.close()
         raise ValueError(f"Table '{table_name}' not found")

    valid_columns = {row[1] for row in columns_info}
    
    filtered_data = {k: v for k, v in data.items() if k in valid_columns}
    
    if not filtered_data:
         # Nothing to update
         conn.close()
         return

    set_clauses = []
    values = []
    for col, val in filtered_data.items():
        set_clauses.append(f"{col} = ?")
        values.append(val)
    
    values.append(row_id)
    query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = ?;"
    cursor.execute(query, values)
    conn.commit()
    conn.close()
