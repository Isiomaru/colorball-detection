import cv2,threading,json

class Capture(threading.Thread):
    def __init__(self, detector, ball_queue, frame_queue, file_path):
        super().__init__()
        self.index, self.width, self.height = self.get_setting(file_path)
        self.detector = detector
        self.ball_data = self.reset_ball_data()
        self.ball_queue = ball_queue
        self.frame_queue = frame_queue
        self.camera = self.setup(self.index, self.width, self.height)
        self.running = True

    def get_setting(self, file_path):
        with open(file_path,"r",encoding="utf-8") as f:
            settings= json.load(f)
            return settings["index"], settings["width"], settings["height"]


    # カメラ設定
    def setup(self, index: int, width: int, height: int):
        camera=cv2.VideoCapture(index)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        return camera

    def update_ball_queue(self,ball_data):
        if self.ball_queue.full():
            self.ball_queue.get()
        self.ball_queue.put(ball_data)

    def update_frame_queue(self,frame):
        if self.frame_queue.full():
            self.frame_queue.get()
        self.frame_queue.put(frame)

    def reset_ball_data(self):
        self.ball_data = {
            color_name: 
                {
                    "x"     : 0, 
                    "y"     : 0, 
                    "radius": 0
                }
            for color_name in ["pink" , "cyan"]
        }

    def run(self):
        self.reset_ball_data()

        while self.running:
            ok, frame = self.camera.read()
            if not ok:
                break

            if not self.ball_queue.empty():
                self.ball_data = self.ball_queue.get()

            self.ball_data = self.detector.detect(self.ball_data, frame)

            self.update_ball_queue(self.ball_data)
            self.update_frame_queue(frame.copy())

    def stop(self):
        self.running = False
        self.camera.release()
