# How to setup backend

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```

## Running the server

From `/backend` directory, run:

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.
You can access the automatic documentation at `http://127.0.0.1:8000/docs`.
