from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
import threading
import os

app = FastAPI()

# グローバル変数
state_queue = None
logic_instance = None
connected_clients = []

def set_queues(queue, logic):
    """main.pyから呼ばれる初期化関数"""
    global state_queue, logic_instance
    state_queue = queue
    logic_instance = logic

# 静的ファイルの提供
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
frontend_dir = os.path.join(current_dir, "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def read_root():
    """ルートページ"""
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket接続"""
    await websocket.accept()
    connected_clients.append(websocket)
    
    try:
        # 初期状態を送信
        if not state_queue.empty():
            state = state_queue.get()
            await websocket.send_json(state)
        
        while True:
            # クライアントからのメッセージを受信
            try:
                message = await asyncio.wait_for(
                    websocket.receive_json(), 
                    timeout=0.1
                )
                
                # コマンド処理
                if message.get("command") == "start_calculation":
                    logic_instance.start_calculation()
                    # 別スレッドでスコア開示を実行
                    threading.Thread(
                        target=logic_instance.reveal_scores,
                        daemon=True
                    ).start()
                
                elif message.get("command") == "reset":
                    logic_instance.reset_game()
                
            except asyncio.TimeoutError:
                pass
            
            # 状態更新を送信
            if not state_queue.empty():
                state = state_queue.get()
                # 全クライアントに送信
                for client in connected_clients:
                    try:
                        await client.send_json(state)
                    except:
                        pass
            
            await asyncio.sleep(0.03)  # 30FPS
    
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        if websocket in connected_clients:
            connected_clients.remove(websocket)

def start_server(queue, logic):
    """サーバー起動"""
    set_queues(queue, logic)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)