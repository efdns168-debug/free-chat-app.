from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
connections = []

html = open("client.html", "r").read()

@app.get("/")
def get():
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            msg = await websocket.receive_text()
            for conn in connections:
                await conn.send_text(msg)
    except WebSocketDisconnect:
        connections.remove(websocket)

