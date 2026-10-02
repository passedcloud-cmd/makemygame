"""테스트 맵용 임시 타일(바닥, 벽) 생성기.

실행: python3 tools/gen_test_tiles.py
"""

from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parent.parent / "art" / "tiles" / "test"


def c(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def floor():
    """파스텔 톤 마룻바닥 (32x32, 이어 붙이면 무늬가 자연스럽게 이어짐)."""
    base, line, light = c("#f3e3c8"), c("#e2ccaa"), c("#fbf1de")
    img = Image.new("RGBA", (32, 32), base)
    for y in (0, 16):
        for x in range(32):
            img.putpixel((x, y), line)
            img.putpixel((x, y + 1), light)
    for (x, y0) in ((10, 1), (26, 17)):
        for y in range(y0, y0 + 15):
            img.putpixel((x, y), line)
    return img


def wall():
    """벽면 (32x32). 위쪽은 몰딩, 아래쪽은 걸레받이."""
    base, sh, hi = c("#c9dff0"), c("#a9c4dc"), c("#e4f0fa")
    img = Image.new("RGBA", (32, 32), base)
    for x in range(32):
        img.putpixel((x, 0), hi)
        img.putpixel((x, 1), hi)
        img.putpixel((x, 2), sh)
        for y in range(27, 32):
            img.putpixel((x, y), sh if y > 27 else hi)
    for y in range(3, 27):
        img.putpixel((0, y), sh)
    return img


def box():
    """나무 상자 (32x40). 아래 32px가 바닥에 닿는 부분."""
    base, sh, hi, dark = c("#d9a066"), c("#b07a45"), c("#f0c38c"), c("#6e4524")
    img = Image.new("RGBA", (32, 40), (0, 0, 0, 0))
    for y in range(4, 40):
        for x in range(2, 30):
            col = base
            if y < 12:
                col = hi
            if x in (2, 29) or y in (4, 39):
                col = dark
            elif y == 12:
                col = sh
            elif x in (15, 16) and y > 12:
                col = sh
            img.putpixel((x, y), col)
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    floor().save(OUT / "floor.png")
    wall().save(OUT / "wall.png")
    box().save(OUT / "box.png")


if __name__ == "__main__":
    main()
