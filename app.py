from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import database
from datetime import date

app = FastAPI(title="のりこ Todo App")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    database.init_db()

@app.get("/")
async def root():
    return FileResponse("static/index.html")

# --- Categories ---
@app.get("/api/categories")
async def get_categories():
    return database.get_categories()

@app.post("/api/categories")
async def create_category(data: dict):
    return database.create_category(data["name"], data.get("emoji", "📋"), data.get("color", "#888888"))

@app.put("/api/categories/{cat_id}")
async def update_category(cat_id: int, data: dict):
    return database.update_category(cat_id, data)

@app.delete("/api/categories/{cat_id}")
async def delete_category(cat_id: int):
    database.delete_category(cat_id)
    return {"ok": True}

# --- Todos ---
class TodoCreate(BaseModel):
    title: str
    category_id: Optional[int] = None
    priority: Optional[str] = "medium"  # low, medium, high
    due_date: Optional[str] = None
    tags: Optional[str] = ""
    notes: Optional[str] = ""

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    completed: Optional[bool] = None

@app.get("/api/todos")
async def get_todos(category_id: Optional[int] = None, completed: Optional[bool] = None):
    return database.get_todos(category_id=category_id, completed=completed)

@app.post("/api/todos")
async def create_todo(todo: TodoCreate):
    return database.create_todo(todo.dict())

@app.put("/api/todos/{todo_id}")
async def update_todo(todo_id: int, todo: TodoUpdate):
    return database.update_todo(todo_id, todo.dict(exclude_none=True))

@app.delete("/api/todos/{todo_id}")
async def delete_todo(todo_id: int):
    database.delete_todo(todo_id)
    return {"ok": True}

@app.patch("/api/todos/{todo_id}/complete")
async def toggle_complete(todo_id: int):
    return database.toggle_complete(todo_id)
