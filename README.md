# **🏋️ Workout Tracker Backend (FastAPI)**  
This is the **backend** for the **Workout Tracker**, a RESTful API built with **FastAPI**. It allows users to **log in, manage their workout routines**, and persist their data in a SQLite database.

## **🚀 Features**
- **User Authentication:** Sign up and login functionality with password hashing.
- **Workout Routine Management:** Users can add, edit, delete, and mark workouts as completed.
- **User-Specific Data:** Each user has a unique set of workout routines stored separately.
- **Database Support:** Uses **SQLite** with SQLAlchemy ORM.
- **CORS Support:** Allows frontend to communicate with the backend.

---

## **📌 Tech Stack**
- **Backend Framework:** FastAPI
- **Database:** SQLite with SQLAlchemy ORM
- **Authentication:** bcrypt (for password hashing)
- **Middleware:** CORS (for frontend communication)

---

## **📥 Installation**
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/Workout-Tracker.git
cd Workout-Tracker/backend
```

### **2️⃣ Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

> If `requirements.txt` does not exist, install manually:
```bash
pip install fastapi uvicorn sqlalchemy sqlite3 bcrypt
```

### **4️⃣ Start the API Server**
```bash
uvicorn main:app --reload
```
By default, the backend runs at **`http://127.0.0.1:8000/`**.

---

## **📌 Project Structure**
```
backend/
├── database.py      # Database models and initialization
├── main.py          # FastAPI application entry point
├── workout.db       # SQLite database file
├── __init__.py      # Marks backend as a Python module
└── venv/            # Virtual environment (ignored in .gitignore)
```

---

## **🛠 API Endpoints**
### **🔹 User Authentication**
#### **Login or Register**
- **Endpoint:** `POST /api/login`
- **Request Body:**
  ```json
  {
    "username": "testuser",
    "password": "password123"
  }
  ```
- **Response (New User Registered)**
  ```json
  {
    "message": "User registered and routines initialized",
    "userId": 1,
    "username": "testuser"
  }
  ```
- **Response (Login Successful)**
  ```json
  {
    "message": "Login successful",
    "userId": 1,
    "username": "testuser"
  }
  ```

---

### **🔹 Workout Routine Management**
#### **Get Todos for a User**
- **Endpoint:** `GET /todos/?user_id={userId}`
- **Response Example:**
  ```json
  [
    {"id": 1, "part": "Glute1", "content": "Squats", "isCompleted": false},
    {"id": 2, "part": "Chest", "content": "Bench Press", "isCompleted": false}
  ]
  ```

#### **Add a New Todo**
- **Endpoint:** `POST /todos/`
- **Request Body:**
  ```json
  {
    "user_id": 1,
    "part": "Glute1",
    "content": "Lunges",
    "isCompleted": false
  }
  ```
- **Response:**
  ```json
  {
    "id": 3,
    "part": "Glute1",
    "content": "Lunges",
    "isCompleted": false
  }
  ```

#### **Edit an Existing Todo**
- **Endpoint:** `PUT /todos/{id}`
- **Request Body:**
  ```json
  {
    "user_id": 1,
    "part": "Glute1",
    "content": "Jump Squats",
    "isCompleted": false
  }
  ```
- **Response:**
  ```json
  {
    "id": 1,
    "part": "Glute1",
    "content": "Jump Squats",
    "isCompleted": false
  }
  ```

#### **Delete a Todo**
- **Endpoint:** `DELETE /todos/{id}`
- **Response:**
  ```json
  {
    "id": 1,
    "part": "Glute1",
    "content": "Jump Squats",
    "isCompleted": false
  }
  ```

#### **Toggle Todo Completion**
- **Endpoint:** `PATCH /todos/{id}/toggle`
- **Response:**
  ```json
  {
    "id": 1,
    "part": "Glute1",
    "content": "Squats",
    "isCompleted": true
  }
  ```

---

## **🔑 Database Schema**
### **Users Table**
| Column   | Type   | Description             |
|----------|--------|-------------------------|
| `id`     | int    | Primary key             |
| `username` | str  | Unique user identifier  |
| `password` | str  | Hashed password        |

### **Todos Table**
| Column      | Type   | Description                        |
|------------|--------|------------------------------------|
| `id`       | int    | Primary key                        |
| `user_id`  | int    | Foreign key referencing `users.id` |
| `part`     | str    | Body part category (e.g., Chest)  |
| `content`  | str    | Workout description               |
| `isCompleted` | bool | Task completion status          |

---

## **📌 Deployment**
### **1️⃣ Run Locally**
To run locally, use:
```bash
uvicorn main:app --reload
```
Visit `http://127.0.0.1:8000/docs` to test API using Swagger UI.

### **2️⃣ Deploy to Cloud**
For production, use:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## **✅ Next Steps**
- Implement **JWT Authentication** instead of basic login.
- Add **unit tests** for API endpoints.
- Deploy to **AWS, GCP, or Heroku**.

---

## **📜 License**
This project is open-source and available under the [MIT License](LICENSE).

---

## **🚀 Contributing**
Feel free to **fork, modify, and submit pull requests**! 😊
