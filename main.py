from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, User, TodoItem, add_user_with_routine, initialize_workout_routine
from pydantic import BaseModel
from typing import List
import bcrypt

app = FastAPI()

# 允許的 CORS 來源
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://main.d3gan2pj2zpx9m.amplifyapp.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依賴：取得資料庫會話
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# **更新 Pydantic 模型**
class TodoResponse(BaseModel):
    id: int
    part: str
    content: str
    is_completed: bool  # ✅ 這裡改為符合 PostgreSQL 欄位名稱

    class Config:
        orm_mode = True

# 用於新增 Todo 的模型
class TodoCreate(BaseModel):
    user_id: int
    part: str
    content: str
    is_completed: bool = False  # ✅ 這裡改為符合 PostgreSQL 欄位名稱

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    userId: int
    username: str

@app.get("/")
async def root():
    return {"message": "fastapi - workout tracker"}

# 測試資料庫連線
@app.get("/debug/db-connection")
def test_db_connection(db: Session = Depends(get_db)):
    try:
        users_count = db.query(User).count()
        todos_count = db.query(TodoItem).count()
        return {
            "status": "✅ Database connected successfully!",
            "users_count": users_count,
            "todos_count": todos_count,
        }
    except Exception as e:
        return {"status": "❌ Failed to connect to database", "error": str(e)}

# **獲取 todos**
@app.get("/todos/", response_model=List[TodoResponse])
def get_todos(user_id: int = Query(...), db: Session = Depends(get_db)):
    todos = db.query(TodoItem).filter(TodoItem.user_id == user_id).all()
    return todos

# **新增 todos**
@app.post("/todos/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    new_todo = TodoItem(
        user_id=todo.user_id,
        part=todo.part,
        content=todo.content,
        is_completed=todo.is_completed 
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# **刪除 todos**
@app.delete("/todos/{todo_id}", response_model=TodoResponse)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return todo

# **更新 todos**
@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    existing_todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    existing_todo.part = todo.part
    existing_todo.content = todo.content
    existing_todo.is_completed = todo.is_completed  # ✅ 修正變數名稱
    db.commit()
    db.refresh(existing_todo)
    return existing_todo

# **更新 todos 的完成狀態**
@app.patch("/todos/{todo_id}/toggle", response_model=TodoResponse)
def toggle_todo(todo_id: int, db: Session = Depends(get_db)):
    existing_todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    existing_todo.is_completed = not existing_todo.is_completed  # ✅ 修正變數名稱
    db.commit()
    db.refresh(existing_todo)
    return existing_todo

# **登入 & 註冊 API**
@app.post("/api/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    username = login_data.username
    password = login_data.password

    user = db.query(User).filter(User.username == username).first()

    if user:
        if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            return {"message": "Login successful", "userId": user.id, "username": user.username}
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    else:
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        new_user = add_user_with_routine(username, hashed_password, db)

        if new_user:
            return {"message": "User registered and routines initialized", "userId": new_user.id, "username": new_user.username}
        else:
            raise HTTPException(status_code=400, detail="Username already exists")

# **初始化用戶的 Workout Routine**
@app.post("/api/init_workout/")
def init_workout(user_id: int, db: Session = Depends(get_db)):
    existing_routines = db.query(TodoItem).filter(TodoItem.user_id == user_id).first()
    if existing_routines:
        return {"message": f"Workout routines already exist for user_id {user_id}"}

    initialize_workout_routine(db, user_id)
    return {"message": f"Workout routines initialized for user_id {user_id}"}
