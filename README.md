# 2025festival-ball

OpenCV で検出した 2 色のボール位置をリアルタイムに取得し、FastAPI + WebSocket + ブラウザ UI でスコア可視化す  
 るお祭り向けゲームです。カメラ入力・ゲームロジック・UI をそれぞれ独立スレッド/プロセスで動かし、開始・集計・リ
セットをキーボードまたはブラウザから操作できます。

## 特徴

- 🎥 **カメラ検出**: HSV しきい値 (`config/colors.yaml`) を使ってシアン/ピンクのボールを追跡。
- 🧠 **ゲームロジック**: `Logic` スレッドが 3x3 マス (`config/map_data.json`) とスコア (`config/score.json`) を
  管理。固定スコアとランダム枠を組み合わせて演出。
- 🌐 **FastAPI + WebSocket**: `/` で UI、`/ws` でリアルタイム状態を配信。複数端末を同時表示可。
- 🕹️ **操作方法**: キーボード `s`/`r`/`q` に加え、UI ボタンからも計算開始・リセットを実行。
- 🧩 **カスタマイズ容易**: カメラ解像度 (`config/setting.json`)、マップ座標、スコアテーブルを JSON/YAML で  
  調整。

## 必要環境

- Python 3.11+
- OpenCV を利用できるカメラデバイス
- (推奨) [uv](https://github.com/astral-sh/uv) での依存管理

## セットアップ

```bash
# 仮想環境を作成（任意）
uv venv   # もしくは python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# 依存関係をインストール
uv pip sync        # uv.lock を利用
# または
uv pip install -r requirements.txt
```

## 使い方

python -m src.main

- 起動後に以下のスレッド/サービスが並列実行されます:
  - camera.Capture: カメラからフレーム取得 → Detector へ渡してボール座標を推定
  - camera.Visualizer: キャプチャ映像 + マップを描画（デバッグ用途）
  - keymanager.Inputer: keyboard で s(start) / r(reset) / q(quit) を監視
  - logic.Logic: スコア計算、キューを通じて WebSocket に状態送信
  - server.start_server: FastAPI + Uvicorn で http://localhost:8000 を公開
- ブラウザで http://localhost:8000 を開くと UI が表示されます。
  - 「📊 計算開始」→ 現在のボール位置を基にヒットマスを算出
  - 「🔄 リセット」→ ランダムマス再生成 + ボール情報初期化
  - スコア開示は 1 秒ずつ演出され、トータルスコアが更新されます。

## 設定ファイル

| ファイル             | 内容                                          |
| -------------------- | --------------------------------------------- |
| config/colors.yaml   | HSV の lower/upper 値。照明環境に合わせて調整 |
| config/setting.json  | カメラデバイス index / 解像度                 |
| config/map_data.json | 3x3 グリッドそれぞれの中心座標                |
| config/score.json    | ランダム枠で使用する候補スコア（整数配列）    |

## ディレクトリ構成

src/
main.py # エントリーポイント
camera/ # Detector / Capture / Visualizer
logic/ # スコア計算と状態管理
keymanager/ # キーボード入力収集
server/ # FastAPI + WebSocket サーバー
frontend/
index.html # Web UI
app.js # WebSocket クライアント, Canvas 描画
style.css # UI スタイル
config/ # JSON/YAML 設定

## トラブルシュート

- カメラが映らない: config/setting.json の index を 0/1/... に変更。
- 色が取れない: colors.yaml の HSV を現場の照明でキャリブレーション。
- UI が更新されない: コンソールに WebSocket エラーが出ていないか確認、ポート 8000 が空いているか確認。
