from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import Base, SessionLocal, engine
from models import Todo
from schemas import TodoCreate, TodoResponse, TodoUpdate
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Dockerized To-Do API")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@app.get("/")
def root():
    return {"message": "To-Do API is running"}
@app.get("/health")
def health_check():
    return {"status": "healthy"}
@app.post("/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    new_todo = Todo(
        title=todo.title,
        description=todo.description,
        completed=False
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo
@app.get("/todos", response_model=list[TodoResponse])
def get_todos(db: Session = Depends(get_db)):
    return db.query(Todo).all()
@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo
@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, updated_todo: TodoUpdate, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    if updated_todo.title is not None:
        todo.title = updated_todo.title
    if updated_todo.description is not None:
        todo.description = updated_todo.description
    if updated_todo.completed is not None:
        todo.completed = updated_todo.completed
    db.commit()
    db.refresh(todo)
    return todo
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return {"message": f"Todo {todo_id} deleted successfully"}