# SQL Smart Database Manager

A modern, full-stack web-app that allows users to manage multiple SQL databases through a simple interface. Built with an MVC architecture, it provides secure user authentication and dynamic database schema management, serving as the foundation for future AI-driven database interactions. This app is primarily designed for users to manage databases who have little to no knowledge of SQL.

## 🚀 Current Functionality

### User Authentication
- **Secure Registration & Login**: JWT-based authentication system.
- **Persistent Sessions**: Automatic token management and session restoration via LocalStorage.
- **User Isolation**: Each user has their own private workspace and databases.

### Database Management
- **Multi-Database Support**: Create, name, and manage multiple separate SQLite databases.
- **Physical Isolation**: Each database is stored as a unique file on the server, obfuscated with UUIDs for security.
- **Full CRUD for Databases**: Create and delete entire database instances.

### Schema & Data Control
- **Dynamic Table Management**: Create and drop tables within any database.
- **Live Column Modification**: Add or remove columns from existing tables.
- **Data CRUD Operations**: Full interface to view, add, update, and delete rows in any table.
- **Robust Error Handling**: Real-time feedback for SQL errors and validation failures.

## 🛠 Tech Stack

### Frontend
- **Framework**: [Vue 3](https://vuejs.org/) (Composition API)
- **Build Tool**: [Vite](https://vitejs.dev/)
- **State Management**: [Pinia](https://pinia.vuejs.org/)
- **Styling**: [Bootstrap 5](https://getbootstrap.com/)
- **HTTP Client**: [Axios](https://axios-http.com/)

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database**: [SQLite](https://sqlite.org/)
- **Security**: OAuth2 with Password flow, JWT tokens (python-jose), and BCrypt password hashing.

## ⚙️ Getting Started

### Prerequisites
- Node.js (v20+)
- Python (3.10+)

### 1. Backend Setup
```bash
cd backend
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```
The backend will be available at `http://localhost:8000`. Documentation can be viewed at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
# Install dependencies
npm install

# Run the development server
npm run dev
```
The frontend will be available at `http://localhost:5173`.

---

## 👥 Contributors
- **Nathan Polarski** - Backend Architecture, Authentication, Dynamic DB Logic.
- **Christopher Nolasco** - Frontend Architecture, UI/UX, Database Views.
