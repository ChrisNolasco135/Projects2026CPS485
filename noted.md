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
