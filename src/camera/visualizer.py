import cv2, threading, json

class Visualizer(threading.Thread):
    def __init__(self, ball_queue, frame_queue, file_path):
        super().__init__()
        self.ball_queue = ball_queue
        self.frame_queue = frame_queue
        self.map_data = self.get_map_data(file_path)
        self.running = True
    
    def get_map_data(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            map_data = json.load(f)
            return map_data["map_data"]

    def draw_balls(self, ball_data, frame):
        """ボールの状態を描画"""
        for color_name, data in ball_data.items():
            b_x = data["x"]
            b_y = data["y"]
            b_r = data["radius"]

            # 検出されたことがあるボールのみ描画する
            if b_r:
                # 色を設定
                if color_name == "cyan":
                    color = (255, 255, 0)  # シアン
                else:
                    color = (255, 105, 180)  # ピンク
                
                # 円の外周と中心を描画
                cv2.circle(frame, (b_x, b_y), b_r, color, 3)
                cv2.circle(frame, (b_x, b_y), 3, (0, 0, 255), -1)

                # 色情報をテキストで表示
                cv2.putText(
                    frame, color_name.upper(),
                    (b_x - b_r, b_y - b_r - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2
                )

        return frame

    def draw_grid(self, frame):
        """map_dataに基づいてグリッド描画"""
        for i, row in enumerate(self.map_data):
            for j, cell in enumerate(row):
                x, y = int(cell["x"]), int(cell["y"])
                
                # 枠を描画（60x60ピクセル）
                cv2.rectangle(
                    frame,
                    (x - 60, y - 60),
                    (x + 60, y + 60),
                    (100, 100, 255),  # オレンジ色
                    2
                )
                
                # 中心点
                cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)
                
                # 座標ラベル
                label = f"[{i},{j}]"
                cv2.putText(
                    frame, label, (x - 30, y - 65),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
                )
        
        return frame

    def run(self):
        ball_data = {
            "pink": {"x": 0, "y": 0, "radius": 0},
            "cyan": {"x": 0, "y": 0, "radius": 0}
        }
        frame = None

        while self.running:
            if not self.ball_queue.empty():
                ball_data = self.ball_queue.get()

            if not self.frame_queue.empty():
                frame = self.frame_queue.get()

            if frame is not None:
                # グリッド描画
                frame = self.draw_grid(frame)
                # ボール描画
                frame = self.draw_balls(ball_data, frame)
                
                cv2.imshow("Camera", frame)
                cv2.waitKey(1)

        cv2.destroyAllWindows()

    def stop(self):
        self.running = False