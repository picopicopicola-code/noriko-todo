from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import database
import httpx
import os
import json
from datetime import date

app = FastAPI(title="のりこ Todo App")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup():
    database.init_db()

@app.get("/")
async def root():
    return FileResponse("static/index.html")

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

class TodoCreate(BaseModel):
    title: str
    category_id: Optional[int] = None
    priority: Optional[str] = "medium"
    due_date: Optional[str] = None
    tags: Optional[str] = ""
    notes: Optional[str] = ""
    urgency: Optional[str] = "someday"

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    priority: Optional[str] = None
    due_date: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    completed: Optional[bool] = None
    urgency: Optional[str] = None

@app.get("/api/todos")
async def get_todos(category_id: Optional[int] = None, completed: Optional[bool] = None, urgency: Optional[str] = None):
    return database.get_todos(category_id=category_id, completed=completed, urgency=urgency)

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

class AIParseRequest(BaseModel):
    text: str

@app.post("/api/ai/parse")
async def ai_parse(req: AIParseRequest):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not set")
    categories = database.get_categories()
    cat_list = "\n".join([f"- id:{c['id']} name:{c['name']} emoji:{c['emoji']}" for c in categories])
    today = date.today().isoformat()
    system_prompt = f"""あなたはTodoアプリのタスク解析AIです。ユーザーの自由入力テキストからタスクのリストを抽出してJSON形式で返してください。
今日の日付: {today}
利用可能なカテゴリ:
{cat_list}
urgencyの選択肢: today(今日やる) / free_time(時間ある時) / someday(いつか)
各タスク: title, category_id(不明はnull), category_uncertain(bool), priority(high/medium/low), due_date(YYYY-MM-DDまたはnull), urgency, tags(配列), notes
必ずJSON配列のみ返してください。例: [{{"title":"添削","category_id":1,"category_uncertain":false,"priority":"high","due_date":null,"urgency":"today","tags":[],"notes":""}}]"""
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 2000, "messages": [{"role": "user", "content": req.text}], "system": system_prompt},
            timeout=30,
        )
    if res.status_code != 200:
        raise HTTPException(status_code=500, detail=f"AI error: {res.text}")
    data = res.json()
    text = data["content"][0]["text"].strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    tasks = json.loads(text.strip())
    return {"tasks": tasks, "categories": categories}
