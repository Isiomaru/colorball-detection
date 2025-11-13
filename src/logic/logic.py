import threading, json, random, time

class Logic(threading.Thread):
    def __init__(self, camera, ball_queue, state_queue, key_queue, file_path1, file_path2):
        super().__init__()

        self.camera = camera
        self.state_queue = state_queue
        self.ball_queue = ball_queue
        self.key_queue = key_queue
        self.map_data = self.get_setting(file_path1)
        self.score_list = self.get_score_list(file_path2)

        # ゲーム状態
        self.game_state = "waiting"
        self.hit_positions = []
        self.total_score = 0
        self.revealed_scores = []
        self.ball_data = {
                                "pink": 
                                    {
                                        "x": 0, 
                                        "y": 0, 
                                        "radius": 0
                                    }, 
                                "cyan": 
                                    {
                                        "x": 0, 
                                        "y": 0, 
                                        "radius": 0
                                    }
        }

        self.running = True
    
    def get_setting(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            map_data = json.load(f)
            return map_data["map_data"]
    
    def get_score_list(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            score_list = json.load(f)
            return score_list

    def set_score_data(self, score_data, score_list):
        # 固定スコア
        score_data[0]["score"] = 500
        score_data[0]["fixed"] = True
        
        score_data[1]["score"] = 200
        score_data[1]["fixed"] = True
        
        score_data[2]["score"] = 500
        score_data[2]["fixed"] = True

        score_data[3]["score"] = 300
        score_data[3]["fixed"] = True
        
        # ランダムスコア（中央）
        score_data[4]["score"] = random.choice(score_list)
        score_data[4]["fixed"] = False
        
        score_data[5]["score"] = 300
        score_data[5]["fixed"] = True

        score_data[6]["score"] = 400
        score_data[6]["fixed"] = True
        
        score_data[7]["score"] = 200
        score_data[7]["fixed"] = True
        
        score_data[8]["score"] = 400
        score_data[8]["fixed"] = True
        
        return score_data

    def set_map_data_score(self, map_data, score_data):
        idx = 0
        for i in range(len(map_data)):
            for j in range(len(map_data[i])):
                map_data[i][j]["score"] = score_data[idx]["score"]
                map_data[i][j]["fixed"] = score_data[idx]["fixed"]
                idx += 1
        return map_data

    def randomize_scores(self):
        score_data = [{"score": 0, "fixed": False} for _ in range(9)]
        score_data = self.set_score_data(score_data, self.score_list)
        self.map_data = self.set_map_data_score(self.map_data, score_data)

    def check_ball_positions(self, ball_data):
        """ボールがどのマスに入っているかチェック"""
        hit_positions = []
        
        for i, row in enumerate(self.map_data):
            for j, cell in enumerate(row):
                px, py = cell["x"], cell["y"]
                
                # 各ボールをチェック
                for color_name in ["pink", "cyan"]:
                    bx, by = ball_data[color_name]["x"], ball_data[color_name]["y"]
                    br = ball_data[color_name]["radius"]
                    
                    # ボールが検出されている場合のみ
                    if br > 0:
                        # マスの範囲内かチェック（±60ピクセル）
                        if abs(px - bx) < 60 and abs(py - by) < 60:
                            hit_positions.append({
                                "row": i,
                                "col": j,
                                "color": color_name,
                                "score": cell["score"],
                                "fixed": cell.get("fixed", False)
                            })
        
        return hit_positions
    
    def start_calculation(self):
        """集計開始"""
        if self.game_state != "waiting":
            return
        
        self.game_state = "calculating"
        self.hit_positions = self.check_ball_positions(self.ball_data)
        self.total_score = 0
        self.revealed_scores = []
        
        # 固定スコアのヒットを即座に加算
        for hit in self.hit_positions:
            if hit.get("fixed", False):
                self.total_score += hit["score"]
        
        # 状態を送信
        self.send_state()
    
    def reveal_scores(self):
        """ランダムスコアを開示（演出）"""
        if self.game_state != "calculating":
            return
        
        self.game_state = "showing"
        
        # ランダムスコアのヒットのみ開示
        random_hits = [h for h in self.hit_positions if not h.get("fixed", False)]
        
        for hit in random_hits:
            time.sleep(1)  # 1秒間隔
            self.revealed_scores.append(hit)
            self.total_score += hit["score"]
            self.send_state()
        
        # 最終結果
        time.sleep(1)
        self.game_state = "result"
        self.send_state()
    
    def reset_game(self):
        """ゲームリセット"""
        self.randomize_scores()
        self.game_state = "waiting"
        self.hit_positions = []
        self.total_score = 0
        self.revealed_scores = []

        # ボール位置を初期化
        self.ball_data = {
            "pink": {"x": 0, "y": 0, "radius": 0},
            "cyan": {"x": 0, "y": 0, "radius": 0}
        }
        self.camera.reset_ball_data()

        if self.ball_queue.full():
            self.ball_queue.get()
        self.ball_queue.put(self.ball_data)

        self.send_state()
    
    def send_state(self):
        """現在の状態をWebSocketキューに送信"""
        state = {
            "game_state": self.game_state,
            "ball_positions": self.ball_data,
            "map_data": self.map_data,
            "hit_positions": self.hit_positions,
            "revealed_scores": self.revealed_scores,
            "total_score": self.total_score
        }
        
        if self.state_queue.full():
            self.state_queue.get()
        self.state_queue.put(state)


    def run(self):
        self.randomize_scores()
        self.send_state()

        while self.running:
            # ボール位置を常に更新
            if not self.ball_queue.empty():
                self.ball_data = self.ball_queue.get()

                # waiting状態のみリアルタイム送信
                if self.game_state == "waiting":
                    self.send_state()

            # キー入力処理
            if not self.key_queue.empty():
                key_state = self.key_queue.get()

                # 's'で集計開始
                if key_state.get("s", False):
                    print("📊 集計開始！")
                    self.start_calculation()
                    threading.Thread(
                        target=self.reveal_scores,
                        daemon=True
                    ).start()

                # 'r'でリセット
                if key_state.get("r", False):
                    print("🔄 リセット")
                    self.reset_game()

            time.sleep(0.01)

    def stop(self):
        self.running = False