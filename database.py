import sqlite3
import json
from datetime import datetime

DB_PATH = "todo.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            emoji TEXT DEFAULT '📋',
            color TEXT DEFAULT '#888888',
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category_id INTEGER REFERENCES categories(id),
            priority TEXT DEFAULT 'medium',
            due_date TEXT,
            tags TEXT DEFAULT '',
            notes TEXT DEFAULT '',
            completed INTEGER DEFAULT 0,
            completed_at TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Insert default categories if empty
    count = c.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    if count == 0:
        defaults = [
            ("Niere", "🏫", "#6C8EBF"),
            ("Misfits", "💼", "#82B366"),
            ("ウェブフリ", "🎯", "#F0A30A"),
            ("Threads（自分）", "📱", "#E84393"),
            ("自動化", "🤖", "#9673A6"),
            ("JIKUU", "🌀", "#23A6D5"),
            ("あいたん講座", "💫", "#FF6B9D"),
            ("プライベート", "🏠", "#D85C5C"),
            ("その他", "📋", "#888888"),
        ]
        c.executemany("INSERT INTO categories (name, emoji, color) VALUES (?,?,?)", defaults)
    
    conn.commit()
    conn.close()

def row_to_dict(row):
    return dict(row) if row else None

# --- Categories ---
def get_categories():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_category(name, emoji, color):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO categories (name, emoji, color) VALUES (?,?,?)", (name, emoji, color))
    conn.commit()
    row = conn.execute("SELECT * FROM categories WHERE id=?", (c.lastrowid,)).fetchone()
    conn.close()
    return dict(row)

def update_category(cat_id, data):
    conn = get_conn()
    fields = []
    values = []
    for k in ["name", "emoji", "color"]:
        if k in data:
            fields.append(f"{k}=?")
            values.append(data[k])
    if fields:
        values.append(cat_id)
        conn.execute(f"UPDATE categories SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
    row = conn.execute("SELECT * FROM categories WHERE id=?", (cat_id,)).fetchone()
    conn.close()
    return dict(row)

def delete_category(cat_id):
    conn = get_conn()
    conn.execute("UPDATE todos SET category_id=NULL WHERE category_id=?", (cat_id,))
    conn.execute("DELETE FROM categories WHERE id=?", (cat_id,))
    conn.commit()
    conn.close()

# --- Todos ---
def get_todos(category_id=None, completed=None):
    conn = get_conn()
    query = """
        SELECT t.*, c.name as category_name, c.emoji as category_emoji, c.color as category_color
        FROM todos t
        LEFT JOIN categories c ON t.category_id = c.id
        WHERE 1=1
    """
    params = []
    if category_id is not None:
        query += " AND t.category_id=?"
        params.append(category_id)
    if completed is not None:
        query += " AND t.completed=?"
        params.append(1 if completed else 0)
    query += " ORDER BY t.completed ASC, CASE t.priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, t.due_date ASC NULLS LAST, t.created_at DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_todo(data):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO todos (title, category_id, priority, due_date, tags, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["title"],
        data.get("category_id"),
        data.get("priority", "medium"),
        data.get("due_date"),
        data.get("tags", ""),
        data.get("notes", ""),
    ))
    conn.commit()
    row = conn.execute("""
        SELECT t.*, c.name as category_name, c.emoji as category_emoji, c.color as category_color
        FROM todos t LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id=?
    """, (c.lastrowid,)).fetchone()
    conn.close()
    return dict(row)

def update_todo(todo_id, data):
    conn = get_conn()
    fields = []
    values = []
    allowed = ["title", "category_id", "priority", "due_date", "tags", "notes", "completed"]
    for k in allowed:
        if k in data:
            fields.append(f"{k}=?")
            values.append(data[k])
    if "completed" in data and data["completed"]:
        fields.append("completed_at=?")
        values.append(datetime.now().isoformat())
    if fields:
        values.append(todo_id)
        conn.execute(f"UPDATE todos SET {', '.join(fields)} WHERE id=?", values)
        conn.commit()
    row = conn.execute("""
        SELECT t.*, c.name as category_name, c.emoji as category_emoji, c.color as category_color
        FROM todos t LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id=?
    """, (todo_id,)).fetchone()
    conn.close()
    return dict(row)

def delete_todo(todo_id):
    conn = get_conn()
    conn.execute("DELETE FROM todos WHERE id=?", (todo_id,))
    conn.commit()
    conn.close()

def toggle_complete(todo_id):
    conn = get_conn()
    current = conn.execute("SELECT completed FROM todos WHERE id=?", (todo_id,)).fetchone()
    if not current:
        conn.close()
        return None
    new_val = 0 if current["completed"] else 1
    completed_at = datetime.now().isoformat() if new_val else None
    conn.execute("UPDATE todos SET completed=?, completed_at=? WHERE id=?", (new_val, completed_at, todo_id))
    conn.commit()
    row = conn.execute("""
        SELECT t.*, c.name as category_name, c.emoji as category_emoji, c.color as category_color
        FROM todos t LEFT JOIN categories c ON t.category_id = c.id
        WHERE t.id=?
    """, (todo_id,)).fetchone()
    conn.close()
    return dict(row)
