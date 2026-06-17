#!/usr/bin/env python3
"""Generate a deterministic RGB888 test image for the Sobel simulation."""

from __future__ import annotations

import argparse
from pathlib import Path


def pixel(width: int, height: int, x: int, y: int) -> tuple[int, int, int]:
    # 基础背景：均匀中灰色，避免渐变干扰边缘判断
    r, g, b = 128, 128, 128

    # 1. 左上角：实心深色圆形（测试曲线边缘）
    cx1, cy1, radius1 = width // 4, height // 4, min(width, height) // 6
    if (x - cx1) ** 2 + (y - cy1) ** 2 <= radius1 ** 2:
        r, g, b = 20, 20, 20

    # 2. 右上角：空心浅色正方形（测试直角与空心轮廓）
    cx2, cy2, half_len = (width * 3) // 4, height // 4, min(width, height) // 6
    in_square = (cx2 - half_len <= x <= cx2 + half_len) and (cy2 - half_len <= y <= cy2 + half_len)
    in_inner = (cx2 - half_len + 3 < x < cx2 + half_len - 3) and (cy2 - half_len + 3 < y < cy2 + half_len - 3)
    if in_square and not in_inner:
        r, g, b = 230, 230, 230

    # 3. 左下角：水平黑白条纹（测试垂直方向边缘）
    if y >= height // 2 and x < width // 2:
        if (y // 8) % 2 == 0:
            r, g, b = 255, 255, 255
        else:
            r, g, b = 0, 0, 0

    # 4. 右下角：垂直黑白条纹（测试水平方向边缘）
    if y >= height // 2 and x >= width // 2:
        if (x // 8) % 2 == 0:
            r, g, b = 255, 255, 255
        else:
            r, g, b = 0, 0, 0

    # 5. 中心区域：45°斜向条纹（测试斜向边缘响应）
    mid_x, mid_y = width // 2, height // 2
    if abs(x - mid_x) < width // 6 and abs(y - mid_y) < height // 6:
        if ((x + y) // 6) % 2 == 0:
            r, g, b = 200, 200, 200
        else:
            r, g, b = 50, 50, 50

    return r, g, b

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=128)
    parser.add_argument("--height", type=int, default=72)
    parser.add_argument("--output", type=Path, default=Path("data/input_rgb.hex"))
    args = parser.parse_args()

    if args.width <= 1 or args.height <= 1:
        raise SystemExit("width and height must be greater than 1")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="ascii") as f:
        for y in range(args.height):
            for x in range(args.width):
                for channel in pixel(args.width, args.height, x, y):
                    f.write(f"{channel:02x}\n")


if __name__ == "__main__":
    main()
