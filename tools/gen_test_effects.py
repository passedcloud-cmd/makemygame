"""테스트용 이펙트/몬스터/UI 그림 생성기.

실행: python3 tools/gen_test_effects.py
"""

import math
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent / "art"


def c(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


def slash():
    """휘두르기 이펙트 (32x32 x 3프레임). 오른쪽을 향한 모양으로 그리고, 게임에서 돌려서 쓴다."""
    img = Image.new("RGBA", (96, 32), (0, 0, 0, 0))
    frames = [(-85, -15, 255), (-70, 70, 255), (15, 85, 150)]
    for f, (a0, a1, alpha) in enumerate(frames):
        for deg10 in range(a0 * 10, a1 * 10 + 1, 5):
            t = math.radians(deg10 / 10)
            for r, col in ((10, c("#b9b0d9", alpha)), (11, c("#ffffff", alpha)),
                           (12, c("#ffffff", alpha)), (13, c("#b9b0d9", alpha))):
                x = round(4 + r * math.cos(t))
                y = round(16 + r * math.sin(t))
                if 0 <= x < 32 and 0 <= y < 32:
                    img.putpixel((f * 32 + x, y), col)
    return img


def blob():
    """그림자 몬스터 (32x32 x 2프레임, 숨 쉬듯 움찔거림). 발밑이 y=30."""
    img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    body, rim, dark = c("#2b2140"), c("#4b3b66"), c("#1a1428")
    eye, eye_glow = c("#ffe9a8"), c("#ff9fb2")
    for f, (top, half) in enumerate(((9, 11), (10, 12))):
        ox = f * 32
        for y in range(top, 31):
            # 위는 반원처럼 둥글고, 아래는 치마처럼 살짝 퍼지는 모양
            dy = top + half - y
            if dy > 0:
                w = int(round(math.sqrt(max(0, half * half - dy * dy))))
            else:
                w = half + (1 if y > 25 else 0)
            for x in range(16 - w, 16 + w):
                col = body
                if x in (16 - w, 16 + w - 1) or y == top:
                    col = rim
                if y == 30 and (x + f) % 3 == 0:
                    continue        # 아래쪽이 흐물흐물 녹아내리는 느낌
                if y >= 28:
                    col = dark
                img.putpixel((ox + x, y), col)
        ey = top + 8
        for ex in (12, 19):
            img.putpixel((ox + ex, ey), eye)
            img.putpixel((ox + ex + 1, ey), eye)
            img.putpixel((ox + ex, ey + 1), eye_glow)
            img.putpixel((ox + ex + 1, ey + 1), eye_glow)
    return img


def hearts():
    """체력 하트 (9x8 x 2프레임: 꽉 찬 하트, 빈 하트)."""
    shape = [
        ".##...##.",
        "####.####",
        "#########",
        "#########",
        ".#######.",
        "..#####..",
        "...###...",
        "....#....",
    ]
    img = Image.new("RGBA", (18, 8), (0, 0, 0, 0))
    for f, (fill, edge) in enumerate(((c("#e0566f"), c("#7a1f33")), (c("#2a2433"), c("#6d6280")))):
        for y, row in enumerate(shape):
            for x, ch in enumerate(row):
                if ch != "#":
                    continue
                neighbors = [
                    shape[yy][xx] if 0 <= yy < 8 and 0 <= xx < 9 else "."
                    for (xx, yy) in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
                ]
                col = edge if "." in neighbors else fill
                img.putpixel((f * 9 + x, y), col)
        if f == 0:
            img.putpixel((2, 2), c("#ffc2cc"))
            img.putpixel((2, 3), c("#ffc2cc"))
    return img


def door():
    """나무 문 (32x48). 벽에 붙여서 쓴다."""
    img = Image.new("RGBA", (32, 48), (0, 0, 0, 0))
    frame_c, wood, wood_d, knob = c("#1c1722"), c("#5a4136"), c("#46322a"), c("#c9a15a")
    for y in range(0, 48):
        for x in range(3, 29):
            col = wood
            if x in (3, 4, 27, 28) or y < 2:
                col = frame_c
            elif x in (15, 16):
                col = wood_d
            elif y in (14, 15, 34, 35):
                col = wood_d
            img.putpixel((x, y), col)
    for (x, y) in ((22, 26), (23, 26), (22, 27), (23, 27)):
        img.putpixel((x, y), knob)
    return img


def main():
    (ROOT / "effects").mkdir(parents=True, exist_ok=True)
    (ROOT / "monsters").mkdir(parents=True, exist_ok=True)
    (ROOT / "ui").mkdir(parents=True, exist_ok=True)
    slash().save(ROOT / "effects" / "slash.png")
    blob().save(ROOT / "monsters" / "shadow_blob.png")
    hearts().save(ROOT / "ui" / "hearts.png")
    door().save(ROOT / "tiles" / "test" / "door.png")


if __name__ == "__main__":
    main()
