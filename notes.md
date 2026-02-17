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
### Christopher Nolasco
- Created NavBar component in upper part of the webpage for easy access to login and register prompts
    - Added Login prompt and submit button for pre-existing users (none for now)
    - Added Register prompt and submit button to add users to database
- Used Axios for 'application/x-www-form-urlencoded' posts to the backend for OAuth2 authorization tokens for Login
    - Changed auth.js to now use application/x-www-form-urlencoded as the content-type rather than json responses for authentication requests

    
### Nathan Polarski
- implemented the backend functionality for user accounts
    - Added user account database model for MVC architecture using SQLAlchemy and SQLite
    - Created User account creation endpoint (`/register`) allowing username, email, and password
    - Created Login endpoint (`/token`) using OAuth2 with Password Flow and JWT tokens
        - user's username and password exchanged directly for a JWT access token that lasts 30 minutes
    - Created User information endpoint (`/users/me`) to retrieve logged-in account details
    - Added comprehensive comments and documentation to all backend code
