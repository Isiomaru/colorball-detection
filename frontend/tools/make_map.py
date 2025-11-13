#!/usr/bin/env python3
"""
map_data.json自動生成スクリプト
カメラ解像度とグリッド数から座標を計算
"""

import json
import os

def generate_map_data(width, height, rows, cols):
    """
    グリッド座標を生成
    
    Args:
        width: カメラ横幅（ピクセル）
        height: カメラ縦幅（ピクセル）
        rows: グリッド行数
        cols: グリッド列数
    """
    cell_width = width / cols
    cell_height = height / rows
    
    map_data = []
    
    for row in range(rows):
        row_data = []
        for col in range(cols):
            # 各マスの中心座標
            x = int((col + 0.5) * cell_width)
            y = int((row + 0.5) * cell_height)
            
            row_data.append({
                "x": x,
                "y": y,
                "score": 0
            })
        map_data.append(row_data)
    
    return {
        "map_data": map_data,
        "_comment": f"解像度{width}x{height}に基づく{rows}x{cols}グリッド",
        "_calculation": {
            "width": width,
            "height": height,
            "grid_rows": rows,
            "grid_cols": cols,
            "cell_width": round(cell_width, 2),
            "cell_height": round(cell_height, 2)
        }
    }

def main():
    # setting.jsonから解像度を読み込み
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    setting_path = os.path.join(current_dir, "config", "setting.json")
    
    with open(setting_path, "r") as f:
        settings = json.load(f)
    
    width = settings["width"]
    height = settings["height"]
    
    print(f"カメラ解像度: {width}x{height}")
    print("グリッドサイズを入力してください")
    
    # ユーザー入力
    try:
        rows = int(input("行数 (デフォルト: 3): ") or "3")
        cols = int(input("列数 (デフォルト: 3): ") or "3")
    except ValueError:
        print("無効な入力です。デフォルト値(3x3)を使用します。")
        rows = 3
        cols = 3
    
    # 生成
    map_data = generate_map_data(width, height, rows, cols)
    
    # 保存
    output_path = os.path.join(current_dir, "config", "map_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(map_data, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ map_data.json を生成しました: {output_path}")
    print(f"グリッド: {rows}x{cols}")
    
    # プレビュー
    print("\n生成された座標:")
    for i, row in enumerate(map_data["map_data"]):
        print(f"行{i}: ", end="")
        for j, cell in enumerate(row):
            print(f"[{i},{j}]:({cell['x']},{cell['y']}) ", end="")
        print()

if __name__ == "__main__":
    main()