import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.exc import IntegrityError

# 讀取環境變數 DATABASE_URL（如果不存在則回退到 SQLite，方便本地測試）
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./workout.db")

# 如果使用 SQLite，才需要 `check_same_thread`
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)  # 移除 `check_same_thread`
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TodoItem(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    part = Column(String, index=True)  # Body part (e.g., Glute1, Breast)
    content = Column(String, index=True)  # Action content
    is_completed = Column(Boolean, default=False)  # Completion status
    user_id = Column(Integer, ForeignKey("users.id"))  # 新增 user_id 欄位，設置外鍵

    # 定義關聯
    user = relationship("User", back_populates="todos")

# 新增 Users 資料表
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)  # 確保用戶名唯一
    password = Column(String, nullable=False)  # 儲存哈希過的密碼

    # 定義關聯
    todos = relationship("TodoItem", back_populates="user")

Base.metadata.create_all(bind=engine)



def add_user_with_routine(username: str, password: str, db: Session):
    """
    新增用戶並初始化該用戶的預設 Workout Routine
    如果存在 "testuser" 的記錄，將其 user_id 替換為新用戶的 user_id
    """
    try:
        # 新增用戶
        new_user = User(username=username, password=password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)  # 獲取新用戶的 user_id

        # 如果存在 testuser 的記錄，將其 user_id 更新為新用戶的 user_id
        replace_testuser_routines(db, old_user_id=1, new_user_id=new_user.id)

        print(f"User {username} created and routines updated.")
        return new_user
    except IntegrityError:
        db.rollback()
        print(f"Failed to create user {username}: username already exists.")
        return None

def replace_testuser_routines(db: Session, old_user_id: int, new_user_id: int):
    """
    將 testuser (user_id=1) 的記錄更新為新用戶的 user_id
    """
    db.query(TodoItem).filter(TodoItem.user_id == old_user_id).update(
        {TodoItem.user_id: new_user_id}
    )
    db.commit()
    print(f"Replaced routines of user_id {old_user_id} with new user_id {new_user_id}")

def initialize_workout_routine(db: Session, user_id: int):
    """
    初始化指定用戶的預設 Workout Routine
    """
    print(f"🔍 正在初始化 user_id: {user_id} 的 Workout Routine")

    # 確保 user_id 存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"❌ user_id {user_id} 不存在於 users 表")
        return {"error": f"user_id {user_id} 不存在"}

    routines = [
        {"part": "Glute1", "content": "Bulgarian Split Squats", "is_completed": False},
        {"part": "Glute1", "content": "Dumbbell RDLs", "is_completed": False},
        {"part": "Glute2", "content": "Lunges", "is_completed": False},
        {"part": "Glute2", "content": "Hip Thrust", "is_completed": False},
        {"part": "Chest", "content": "Push-ups", "is_completed": False},
        {"part": "Chest", "content": "Bench Press", "is_completed": False},
        {"part": "Back", "content": "Lat Pulldown", "is_completed": False},
        {"part": "Back", "content": "Pull-Ups", "is_completed": False},
    ]

    for routine in routines:
        routine["user_id"] = user_id
        print(f"✅ 插入 todo: {routine}")  # 🔍 Debug
        db.add(TodoItem(**routine))

    db.commit()
    print(f"🎉 成功初始化 user_id: {user_id} 的 Workout Routine")


def seed_database():
    """
    測試用：初始化資料庫，新增測試用戶及其對應的 Workout Routine
    """
    db = SessionLocal()
    try:
        # 確認是否已有用戶
        if not db.query(User).first():
            add_user_with_routine(username="testuser", password="hashedpassword", db=db)
    finally:
        db.close()

seed_database()  # 初始化資料
