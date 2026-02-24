# Notes
## 3/3 - 3/10
### Christopher Nolasco
In order to work on the MVC architecture we need a model, view and a controller to communicate between the two components. The technologies we will be working with are Vue3 and javascript for the view component as well as flask with python for the model and controller

* Vue3 (View) + Flask/FastAPI (Controller + Model) + JSON API

### Nathan Polarski
- Decided on using FastAPI for backend as it has
    - Native JSON serialization
        - Making communication between Vue frontend and Python backend easy
    - Automatic API documentation in `/docs`
        - No guesswork about what JSON structure frontend will receive
    - Native Python `async` support 
        - Handles long-running AI requests without blocking the server
    - Built-in data validation
        - If Vue frontend sends malformed data, FastAPI rejects it with a clear 422 error detailing exactly which field failed.
- Implemented inital basic FastAPI backend

## 3/10-3/17
### Nathan Polarski
- implemented the backend functionality for user accounts
    - Added user account database model for MVC architecture using SQLAlchemy and SQLite
    - Created User account creation endpoint (`/register`) allowing username, email, and password
    - Created Login endpoint (`/token`) using OAuth2 with Password Flow and JWT tokens
        - user's username and password exchanged directly for a JWT access token that lasts 30 minutes
    - Created User information endpoint (`/users/me`) to retrieve logged-in account details
    - Added comprehensive comments and documentation to all backend code

## 3/17-3/24
### Christopher Nolasco
- Added the DatabaseView view for database and table management
    - Implemented appropriate display of database/tables based on currently logged in user
    - Added database/table view, creation, modification and deletion feature
    - Utilized `backend/dynamic_db.py` for file modifications based on user inputs through UI modals
- Modified webpage UI and visuals
    - Added simple gradient
    - Changed button styling
    - Removed Vue assets

### Nathan Polarski
- Implemented backend functionality for user-managed databases
    - Created `Database` model to track user-owned SQLite databases
    - Implemented file-based storage for user databases in `backend/user_databases/`
    - Created `backend/dynamic_db.py` to handle direct SQLite file operations
    - Added CRUD endpoints for:
        - Databases (`/databases/`)
        - Tables (`/databases/{id}/tables`)
        - Columns (`/databases/{id}/tables/{name}/columns`)
        - Rows (`/databases/{id}/tables/{name}/rows`)
    - Implemented robust error handling:
        - Catches `sqlite3.OperationalError` for missing tables and returns clear 400/404 errors
        - Filters input data to prevent crashes from extra fields
    - Updated API schemas to support dynamic table structures
