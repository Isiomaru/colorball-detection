import camera
import keymanager
import logic
import server
import queue
import os
import time
import threading

def main():

    ball_queue=queue.Queue(maxsize=1)
    frame_queue=queue.Queue(maxsize=1)
    key_queue=queue.Queue(maxsize=1)
    state_queue = queue.Queue(maxsize=1)  # WebSocket用

    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path1 = os.path.join(current_dir,"config","colors.yaml")
    file_path2 = os.path.join(current_dir,"config","setting.json")
    file_path3 = os.path.join(current_dir,"config","map_data.json")
    file_path4 = os.path.join(current_dir,"config","score.json")


    dtc=camera.Detector(file_path1)
    vis=camera.Visualizer(ball_queue,frame_queue,file_path3)
    cam=camera.Capture(dtc,ball_queue,frame_queue,file_path2)
    kym=keymanager.Inputer(key_queue)
    log=logic.Logic(cam, ball_queue,state_queue,key_queue,file_path3,file_path4)


    cam.start()
    vis.start()
    kym.start()
    log.start()


    # WebSocketサーバー起動（別スレッド）
    server_thread = threading.Thread(
        target=server.start_server,
        args=(state_queue, log),
        daemon=True
    )
    server_thread.start()

    print("=" * 50)
    print("🎮 ボールゲーム起動")
    print("=" * 50)
    print("📹 カメラ: 起動")
    print("🌐 WebSocket: http://localhost:8000")
    print("🎨 UI: ブラウザで http://localhost:8000 を開く")
    print("=" * 50)
    print("キー操作:")
    print("  q: 終了")
    print("  s: 集計開始")
    print("  r: リセット")
    print("=" * 50)

    while True:
        if not key_queue.empty():
            key_state = key_queue.get()

            # 'q'で終了
            if key_state.get("q", False):
                print("\n終了中...")
                cam.stop()
                vis.stop()
                kym.stop()
                log.stop()
                break

        time.sleep(0.01)


    cam.join()
    vis.join()
    kym.join()
    log.join()


if __name__ == "__main__":
    main()