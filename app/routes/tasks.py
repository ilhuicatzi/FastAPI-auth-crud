"""
This file contains the routes and handlers for the task crud.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from models import Task, User
from schemas import TaskCreate, TaskDB
from deps import db_dependency, user_dependency

router = APIRouter(
    prefix='/api/tasks',
    tags=['tasks']
)


# Create a task
@router.post("/", response_model=TaskCreate)
async def create_task(task: TaskCreate, db: db_dependency, current_user: user_dependency):
    user_auth = db.query(User).filter(User.id == current_user.id).first()
    if not user_auth:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not authorized")

    db_task = Task(
        title=task.title,
        description=task.description,
        owner_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

# Get all tasks
@router.get("/", response_model=list[TaskDB])
async def read_tasks(db: db_dependency, current_user: user_dependency):
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
    return tasks

# Get a task by id
@router.get("/{task_id}", response_model=TaskDB)
async def read_task(task_id: int, db: db_dependency, current_user: user_dependency):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task

# Update a task by id
@router.put("/{task_id}", response_model=TaskDB)
async def update_task(task_id: int, task: TaskCreate, db: db_dependency, current_user: user_dependency):
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db_task.title = task.title
    db_task.description = task.description
    db_task.owner_id = current_user.id
    db.commit()
    db.refresh(db_task)
    return db_task

# Delete a task by id
@router.delete("/{task_id}", response_model=TaskDB)
async def delete_task(task_id: int, db: db_dependency, current_user: user_dependency):
    db_task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return db_task


