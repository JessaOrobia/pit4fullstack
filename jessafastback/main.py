from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine, Base
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TodoJessa API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/todojessa/", response_model=list[schemas.TodoResponse])
def read_todos(db: Session = Depends(get_db)):
    return db.query(models.Todo).all()

@app.post("/todojessa/", response_model=schemas.TodoResponse)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    db_todo = models.Todo(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todojessa/{todo_id}", response_model=schemas.TodoResponse)
def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="To-Do not found")
    return todo

@app.put("/todojessa/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).get(todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="To-Do not found")
    db_todo.title = todo.title
    db_todo.completed = todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todojessa/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="To-Do not found")
    db.delete(todo)
    db.commit()
    return {"detail": "Deleted"}
