import cv2,numpy,yaml

class Detector():
    def __init__(self, file_path: str):
        self.hsv_list = self.get_hsv(file_path)
        self.numpy_hsv = self.get_numpy(self.hsv_list)

    #numpy形式のhsvファイルを取得
    def get_hsv(self, file_path):

        # yamlファイルを読み込んで色範囲設定
        with open(file_path,"r",encoding="utf-8") as f:
            hsv_list = yaml.safe_load(f)
            return hsv_list

    def get_numpy(self, hsv_list):
        # 色範囲をnumpy配列に変換
        numpy_hsv = {
            color_name: 
                (
                    numpy.array(lower, dtype=numpy.uint8), 
                    numpy.array(upper, dtype=numpy.uint8)
                )
            for color_name, (lower, upper) in hsv_list.items()
        }
    
        return numpy_hsv

    def detect(self, ball_data, frame):

        # 判定しやすいように取得した1frame画像加工
        gfram = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gfram = cv2.GaussianBlur(gfram ,(9,9) ,2)
        hsvfram = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # 円を検出
        circles = cv2.HoughCircles(
            gfram,                 # 入力画像(加工済み)
            cv2.HOUGH_GRADIENT,    
            dp=1,                  
            minDist=20,            # 検出する円同士の最小距離
            param1=28,             # どのくらいの変化で線と認識するか 検知 : 易<———>難
            param2=28,             # どのくらいの線を円と認識するか   検知 : 易<———>難
            minRadius=20,          # 検出する円の最小半径
            maxRadius=35      # 検出する円の最大半径
        )

        if circles is not None:
            circles = numpy.uint16(numpy.around(circles))

            # 検出した円すべてに処理を行う
            for i in circles[0, :]: # i=[x,y,r]
                # 円の座標取得
                c_x, c_y, c_r = i

                # 円の色判定用マスク作成
                mask = numpy.zeros(frame.shape[:2], dtype=numpy.uint8)
                cv2.circle(mask, (c_x, c_y), c_r, 255, -1)

                # 円のhsv取得
                circles_hsv = cv2.mean(hsvfram, mask=mask)  # (H, S, V, A)
                c_h, c_s, c_v = circles_hsv[:3]

                
                # 円の色判定
                c_color = None
                for color_name, (lower_hsv, upper_hsv) in self.numpy_hsv.items():
                    if lower_hsv[0] <= c_h <= upper_hsv[0] and lower_hsv[1] <= c_s <= upper_hsv[1] and lower_hsv[2] <= c_v <= upper_hsv[2]:
                        c_color = color_name
                        break

                # ボールのデータを抽出
                if c_color is not None: 
                    ball_data["pink" if "pink" in c_color else "cyan"] = {
                            "x": int(c_x),
                            "y": int(c_y),
                            "radius": int(c_r)
                    }

        return ball_data