#!/usr/bin/env python3
"""Generate a deterministic RGB888 test image for the Sobel simulation."""

from __future__ import annotations

import argparse
from pathlib import Path


def pixel(width: int, height: int, x: int, y: int) -> tuple[int, int, int]:
    r = g = b = 128

    # 1. 顶部：8级灰度阶梯条
    if y < height // 6:
        step = width // 8
        idx = x // step
        r = g = b = min(idx * 32, 255)

    # 2. 左侧：倾斜阶跃边
    slope = height / width
    if y < int(x * slope) + height // 6:
        r = g = b = 40

    # 3. 中心：3×3灰阶方块阵列（修复溢出：最大值不超过255）
    block_size = min(width, height) // 8
    for row in range(3):
        for col in range(3):
            bx = width // 2 - block_size * 3 // 2 + col * block_size
            by = height // 2 - block_size * 3 // 2 + row * block_size
            if bx <= x < bx + block_size - 2 and by <= y < by + block_size - 2:
                val = 60 + (row * 3 + col) * 21  # 60+8*21=228 ≤ 255
                r = g = b = val

    # 4. 底部：楔形条纹（由疏到密）
    if y > height * 5 // 6:
        period = max(2, 12 - (x * 10) // width)
        r = g = b = 255 if (x // period) % 2 == 0 else 0

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
