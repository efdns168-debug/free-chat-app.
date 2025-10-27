from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Form, HTTPException
from fastapi.responses import HTMLResponse
import sqlite3
import bcrypt

app = FastAPI()
connections = []

# SQLite veritabanı
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)")
conn.commit()

# Client HTML
with open("client.html", "r", encoding="utf-8") as f:
    html = f.read()

@app.get("/")
def get():
    return HTMLResponse(html)

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users VALUES (?, ?)", (username, hashed))
        conn.commit()
        return {"status": "Kayıt başarılı"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Kullanıcı zaten var")

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    c.execute("SELECT password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    if row and bcrypt.checkpw(password.encode(), row[0]):
        return {"status": "Giriş başarılı"}
    raise HTTPException(status_code=400, detail="Kullanıcı adı veya şifre hatalı")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    username = websocket.query_params.get("user")
    if not username:
        await websocket.close()
        return

    await websocket.accept()
    connections.append((username, websocket))
    try:
        while True:
            msg = await websocket.receive_text()
            for user, conn_ws in connections:
                # Basit renkli mesaj: kullanıcı adı yeşil
                await conn_ws.send_text(f"<b style='color:#4CAF50'>{username}</b>: {msg}")
    except WebSocketDisconnect:
        connections.remove((username, websocket))
