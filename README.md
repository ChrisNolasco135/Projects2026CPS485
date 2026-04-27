# SQL Smart Database Manager

A modern, full-stack web application that allows users to manage multiple SQL databases through a simple interface. Built with an MVC architecture, it provides secure user authentication, dynamic database schema management, and AI-driven database interactions (Natural Language to SQL). This app is primarily designed for users with little to no knowledge of SQL.

## 🚀 Features

### User Authentication
- **Secure Registration & Login**: OAuth2 Password Flow with JWT-based authentication (30-minute expiration).
- **Persistent Sessions**: Automatic token management and session restoration via LocalStorage.
- **User Isolation**: Each user has their own private workspace and databases.

### Database Management
- **Multi-Database Support**: Create, name, and manage multiple separate SQLite databases.
- **Physical Isolation**: Each database is stored as a unique file on the server in `backend/user_databases/`, obfuscated with UUIDs for security.
- **Full CRUD for Databases**: Create and delete entire database instances.

### Schema & Data Control
- **Dynamic Table Management**: Create and drop tables within any database.
- **Live Column Modification**: Add or remove columns from existing tables.
- **Data CRUD Operations**: Full interface to view, add, update, and delete rows.
- **Robust Error Handling**: Real-time feedback catching `sqlite3.OperationalError` for missing tables and validation failures.

### 🤖 AI Database Assistant
- **Natural Language to SQL**: Ask questions in plain English about your database.
- **Safe Execution**: The AI extracts the schema context, generates the appropriate SQL, and executes it as a safe read-only query without blocking the server.

## 🛠 Tech Stack

### Frontend (View)
- **Framework**: [Vue 3](https://vuejs.org/) (Composition API) + Vue Router
- **Build Tool**: [Vite](https://vitejs.dev/)
- **State Management**: [Pinia](https://pinia.vuejs.org/)
- **Styling**: [Bootstrap 5](https://getbootstrap.com/)
- **HTTP Client**: [Axios](https://axios-http.com/)

### Backend (Controller + Model)
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Chosen for native JSON serialization, async AI requests, and built-in data validation).
- **Data Validation**: [Pydantic](https://docs.pydantic.dev/)
- **ORM / DB**: [SQLAlchemy](https://www.sqlalchemy.org/) & [SQLite](https://sqlite.org/) (Main user DB is `users.db`).
- **Security**: OAuth2 with Password flow, `python-jose` for JWT tokens, and `bcrypt` password hashing.
- **AI Integration**: [OpenAI API](https://openai.com/)

---

## ⚙️ Getting Started

### Prerequisites
- Node.js (v20.19.0+ or >=22.12.0)
- Python (3.10+)
- OpenAI API Key

### Recommended IDE Setup
- [VS Code](https://code.visualstudio.com/) + [Vue (Official) Extension](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (disable Vetur).
- Browser extensions: [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd).

### 1. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Environment Variables:**
Create a `.env` file in the `backend/` directory and add your OpenAI API key for the AI query features:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Run the Server:**
```bash
uvicorn main:app --reload
```
- The API will be available at `http://127.0.0.1:8000`.
- Automatic API documentation can be viewed at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup

Open a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```
- The frontend UI will be available at `http://localhost:5173`.

---

## 👥 Contributors
- **Nathan Polarski** - Backend Architecture, Authentication, Dynamic DB Logic, AI Agent Integration.
- **Christopher Nolasco** - Frontend Architecture, UI/UX, Vue Routing, Database Views.