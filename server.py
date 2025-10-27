from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

app = FastAPI()
connections = []

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

@app.get("/")
def home():
    return {"message": "Chat server çalışıyor!"}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
