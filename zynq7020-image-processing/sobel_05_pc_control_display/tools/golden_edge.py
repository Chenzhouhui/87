"""
Edge Detection Golden Output Generator (Sobel + Laplacian + Prewitt + Roberts)
===============================================================================
Usage: python golden_edge.py
Outputs: golden_output/{sobel_edge,laplacian_edge,prewitt_edge,roberts_edge}.png,
         comparison.png
"""

import numpy as np
from PIL import Image, ImageDraw
import os

IMG_WIDTH = 128
IMG_HEIGHT = 72
OUTPUT_DIR = "golden_output"

def rgb_to_gray_bt601(rgb):
    r = rgb[:, :, 0].astype(np.uint16)
    g = rgb[:, :, 1].astype(np.uint16)
    b = rgb[:, :, 2].astype(np.uint16)
    gray = (r * 77 + g * 150 + b * 29) >> 8
    return gray.astype(np.uint8)

def sobel_edge(gray):
    h, w = gray.shape
    edge = np.zeros((h, w), dtype=np.uint8)
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            t0, t1, t2 = int(gray[y-1,x-1]), int(gray[y-1,x]), int(gray[y-1,x+1])
            m0, m1, m2 = int(gray[y,  x-1]), int(gray[y,  x]), int(gray[y,  x+1])
            b0, b1, b2 = int(gray[y+1,x-1]), int(gray[y+1,x]), int(gray[y+1,x+1])
            gx = -t0 + t2 - 2*m0 + 2*m2 - b0 + b2
            gy = -t0 - 2*t1 - t2 + b0 + 2*b1 + b2
            mag = abs(gx) + abs(gy)
            edge[y, x] = min(mag, 255)
    return edge

def prewitt_edge(gray):
    h, w = gray.shape
    edge = np.zeros((h, w), dtype=np.uint8)
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            t0, t1, t2 = int(gray[y-1,x-1]), int(gray[y-1,x]), int(gray[y-1,x+1])
            m0, m1, m2 = int(gray[y,  x-1]), int(gray[y,  x]), int(gray[y,  x+1])
            b0, b1, b2 = int(gray[y+1,x-1]), int(gray[y+1,x]), int(gray[y+1,x+1])
            gx = -t0 + t2 - m0 + m2 - b0 + b2
            gy = -t0 - t1 - t2 + b0 + b1 + b2
            mag = abs(gx) + abs(gy)
            edge[y, x] = min(mag, 255)
    return edge

def roberts_edge(gray):
    h, w = gray.shape
    edge = np.zeros((h, w), dtype=np.uint8)
    for y in range(h - 1):
        for x in range(w - 1):
            top_left = int(gray[y, x])
            top_right = int(gray[y, x + 1])
            bottom_left = int(gray[y + 1, x])
            bottom_right = int(gray[y + 1, x + 1])
            gx = top_left - bottom_right
            gy = top_right - bottom_left
            mag = abs(gx) + abs(gy)
            edge[y, x] = min(mag, 255)
    return edge

def normalize_uint8(img):
    peak = int(img.max())
    if peak <= 0:
        return np.zeros_like(img, dtype=np.uint8)
    scaled = (img.astype(np.float32) * 255.0 / float(peak)).round()
    return np.clip(scaled, 0, 255).astype(np.uint8)

def threshold_uint8(img, threshold=80):
    return np.where(img >= threshold, 255, 0).astype(np.uint8)

def laplacian_edge(gray):
    """Laplacian 4-neighbor: [0 -1 0; -1 4 -1; 0 -1 0]
    L = |4*mid1 - top1 - mid0 - mid2 - bot1|"""
    h, w = gray.shape
    edge = np.zeros((h, w), dtype=np.uint8)
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            mid1 = int(gray[y, x])
            top1 = int(gray[y-1, x])
            mid0 = int(gray[y, x-1])
            mid2 = int(gray[y, x+1])
            bot1 = int(gray[y+1, x])
            L = 4 * mid1 - top1 - mid0 - mid2 - bot1
            edge[y, x] = min(abs(L), 255)
    return edge

def generate_test_pattern():
    rgb = np.zeros((IMG_HEIGHT, IMG_WIDTH, 3), dtype=np.uint8)

    # Top gradient band: easy to see the gray conversion, but still with sharp borders.
    for x in range(IMG_WIDTH):
        value = (x * 255) // (IMG_WIDTH - 1)
        rgb[:14, x] = [value, value, value]

    # Large white block in the left-middle area.
    rgb[18:46, 10:46] = [255, 255, 255]

    # High-contrast color block to exercise RGB->gray conversion.
    rgb[18:46, 54:90] = [0, 220, 60]

    # Strong red block on the right.
    rgb[18:46, 96:122] = [255, 48, 48]

    # Checkerboard patch in the lower-left quadrant.
    for y in range(48, 68):
        for x in range(8, 40):
            cell = ((x - 8) // 4 + (y - 48) // 4) & 1
            rgb[y, x] = [240, 240, 240] if cell else [20, 20, 20]

    # Diagonal white line and a thin vertical bar.
    for offset in range(0, 34):
        x = 62 + offset
        y = 50 + offset // 2
        if 0 <= x < IMG_WIDTH and 0 <= y < IMG_HEIGHT:
            rgb[y, x] = [255, 255, 255]
    rgb[8:66, 110:112] = [255, 255, 255]

    # Border frame so the outside contour is also obvious.
    rgb[0:2, :] = [255, 255, 255]
    rgb[-2:, :] = [255, 255, 255]
    rgb[:, 0:2] = [255, 255, 255]
    rgb[:, -2:] = [255, 255, 255]

    # Explicitly draw a dark circle cut-out in the white block to create curved edges.
    pil_rgb = Image.fromarray(rgb, mode="RGB")
    draw = ImageDraw.Draw(pil_rgb)
    draw.ellipse((18, 24, 38, 44), fill=(0, 0, 0))
    return np.array(pil_rgb, dtype=np.uint8)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    rgb = generate_test_pattern()
    gray = rgb_to_gray_bt601(rgb)

    sobel = sobel_edge(gray)
    laplace = laplacian_edge(gray)
    prewitt = prewitt_edge(gray)
    roberts = roberts_edge(gray)

    sobel_vis = normalize_uint8(sobel)
    laplace_vis = normalize_uint8(laplace)
    prewitt_vis = normalize_uint8(prewitt)
    roberts_vis = normalize_uint8(roberts)
    sobel_bin = threshold_uint8(sobel, 80)
    prewitt_bin = threshold_uint8(prewitt, 80)

    Image.fromarray(rgb).save(os.path.join(OUTPUT_DIR, "input_rgb.png"))
    Image.fromarray(gray, mode='L').save(os.path.join(OUTPUT_DIR, "gray.png"))
    Image.fromarray(sobel_vis, mode='L').save(os.path.join(OUTPUT_DIR, "sobel_edge.png"))
    Image.fromarray(laplace_vis, mode='L').save(os.path.join(OUTPUT_DIR, "laplacian_edge.png"))
    Image.fromarray(prewitt_vis, mode='L').save(os.path.join(OUTPUT_DIR, "prewitt_edge.png"))
    Image.fromarray(roberts_vis, mode='L').save(os.path.join(OUTPUT_DIR, "roberts_edge.png"))
    Image.fromarray(sobel_bin, mode='L').save(os.path.join(OUTPUT_DIR, "sobel_bin_t80.png"))
    Image.fromarray(prewitt_bin, mode='L').save(os.path.join(OUTPUT_DIR, "prewitt_bin_t80.png"))

    print(f"Sobel     mean={sobel.mean():.1f} std={sobel.std():.1f} max={sobel.max()}")
    print(f"Laplacian mean={laplace.mean():.1f} std={laplace.std():.1f} max={laplace.max()}")
    print(f"Prewitt   mean={prewitt.mean():.1f} std={prewitt.std():.1f} max={prewitt.max()}")
    print(f"Roberts   mean={roberts.mean():.1f} std={roberts.std():.1f} max={roberts.max()}")

    def report_diff(name, a, b):
        diff = abs(a.astype(int) - b.astype(int))
        corr = np.corrcoef(a.ravel(), b.ravel())[0, 1]
        print(f"{name:<10} mean abs diff={diff.mean():.1f}, Corr={corr:.4f}")

    report_diff("Sobel/Lap", sobel, laplace)
    report_diff("Sobel/Pw", sobel, prewitt)
    report_diff("Sobel/Rob", sobel, roberts)
    report_diff("Lap/Pw", laplace, prewitt)
    report_diff("Lap/Rob", laplace, roberts)
    report_diff("Pw/Rob", prewitt, roberts)

    # Side-by-side comparison
    comp = np.zeros((IMG_HEIGHT, IMG_WIDTH * 5, 3), dtype=np.uint8)
    comp[:, :IMG_WIDTH] = np.stack([gray, gray, gray], axis=-1)
    comp[:, IMG_WIDTH:2*IMG_WIDTH] = np.stack([sobel_vis, sobel_vis, sobel_vis], axis=-1)
    comp[:, 2*IMG_WIDTH:3*IMG_WIDTH] = np.stack([laplace_vis, laplace_vis, laplace_vis], axis=-1)
    comp[:, 3*IMG_WIDTH:4*IMG_WIDTH] = np.stack([prewitt_vis, prewitt_vis, prewitt_vis], axis=-1)
    comp[:, 4*IMG_WIDTH:] = np.stack([roberts_vis, roberts_vis, roberts_vis], axis=-1)
    Image.fromarray(comp).save(os.path.join(OUTPUT_DIR, "comparison.png"))
    print(f"\nSaved to {OUTPUT_DIR}/: input_rgb.png gray.png sobel_edge.png laplacian_edge.png prewitt_edge.png roberts_edge.png sobel_bin_t80.png prewitt_bin_t80.png comparison.png")

if __name__ == "__main__":
    main()
