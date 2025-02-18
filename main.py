from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends, Query
from database import SessionLocal, User, TodoItem, add_user_with_routine, initialize_workout_routine, replace_testuser_routines
from pydantic import BaseModel
from typing import List
import bcrypt

app = FastAPI()

# 允許的來源 (前端運行的網址)
origins = [
    "http://localhost:5173",  # 允許 Vite (React) 訪問
    "http://localhost:3000",  # 允許 CRA (Create React App) 訪問
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允許的來源
    allow_credentials=True,
    allow_methods=["*"],  # 允許所有請求方法 (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # 允許所有標頭
)

# 依賴：獲取資料庫會話
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TodoResponse(BaseModel):
    id: int
    part: str
    content: str
    isCompleted: bool

    class Config:
        orm_mode = True

# 新增: 用於新增 Todo 的模型
class TodoCreate(BaseModel):
    user_id: int
    part: str
    content: str
    isCompleted: bool = False

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    userId: int
    username: str

# 獲取用戶的 todos
@app.get("/todos/", response_model=List[TodoResponse])
def get_todos(user_id: int = Query(...), db: Session = Depends(get_db)):
    # 過濾符合 user_id 的 todos
    todos = db.query(TodoItem).filter(TodoItem.user_id == user_id).all()
    return todos

# 新增 todos
@app.post("/todos/", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    new_todo = TodoItem(
        user_id=todo.user_id,
        part=todo.part,
        content=todo.content,
        isCompleted=todo.isCompleted
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo

# 刪除 todos
@app.delete("/todos/{todo_id}", response_model=TodoResponse)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return todo

# 更新 todos
@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    existing_todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    existing_todo.part = todo.part
    existing_todo.content = todo.content
    existing_todo.isCompleted = todo.isCompleted
    db.commit()
    db.refresh(existing_todo)
    return existing_todo

# 更新 todos 的完成狀態
@app.patch("/todos/{todo_id}/toggle", response_model=TodoResponse)
def toggle_todo(todo_id: int, db: Session = Depends(get_db)):
    existing_todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not existing_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # 切換 isCompleted 狀態
    existing_todo.isCompleted = not existing_todo.isCompleted
    db.commit()
    db.refresh(existing_todo)
    return existing_todo


# 登入 & 註冊 API
@app.post("/api/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    username = login_data.username
    password = login_data.password

    # 檢查用戶是否存在
    user = db.query(User).filter(User.username == username).first()

    if user:
        # 用戶存在，驗證密碼
        if bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8")):
            return {"message": "Login successful", "userId": user.id, "username": user.username}
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    else:
        # 新增用戶並初始化 Workout Routine
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        new_user = add_user_with_routine(username, hashed_password, db)

        if new_user:
            return {"message": "User registered and routines initialized", "userId": new_user.id, "username": new_user.username}
        else:
            raise HTTPException(status_code=400, detail="Username already exists")
        
# 初始化用戶的 Workout Routine
@app.post("/api/init_workout/")
def init_workout(user_id: int, db: Session = Depends(get_db)):
    # 檢查是否已經初始化
    existing_routines = db.query(TodoItem).filter(TodoItem.user_id == user_id).first()
    if existing_routines:
        return {"message": f"Workout routines already exist for user_id {user_id}"}

    # 如果不存在，初始化 Workout Routine
    initialize_workout_routine(db, user_id)
    return {"message": f"Workout routines initialized for user_id {user_id}"}

