"""테스트용 캐릭터 도트 생성기.

실제 그림이 나오기 전까지 Godot에서 쓸 임시(placeholder) 스프라이트를 만든다.
각 캐릭터마다 32x48 프레임으로 된 스프라이트 시트를 만든다.

시트 구성 (RPG 메이커 방식):
    행: 아래(정면), 왼쪽, 오른쪽, 위(뒷모습)
    열: 걷기1, 서 있기, 걷기2

실행: python3 tools/gen_test_sprites.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

W, H = 32, 48
OUT = Path(__file__).resolve().parent.parent / "art" / "sprites" / "test"


def c(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


SKIN = c("#fbe0cb")
SKIN_SH = c("#ecc2a6")
LASH = c("#3a2626")
WHITE = c("#ffffff")
BLUSH = c("#f5b5a5")

CHARS = {
    "A": dict(
        leg=9,
        hair=(c("#e9cf8e"), c("#c8a564"), c("#f7e7b6")),
        eye=(c("#b8834c"), c("#8a5a2e")),
        mouth=c("#d07a6a"),
        blush=True,
    ),
    "B": dict(
        leg=12,
        hair=(c("#2c2c3a"), c("#1b1b25"), c("#4c4c66")),
        eye=(c("#86cff2"), c("#4f9fcc")),
        mouth=c("#b0756a"),
        blush=False,
    ),
    "C": dict(
        leg=8,
        hair=(c("#8b5b3d"), c("#6a4029"), c("#ab7754")),
        eye=(c("#58ad5f"), c("#357c3d")),
        mouth=c("#d07a6a"),
        blush=True,
    ),
}

HEAD = [4, 6, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 7, 7, 6, 4]
CAP = [4, 6, 8, 8, 9, 9, 9]


class Canvas:
    def __init__(self):
        self.p = [[None] * W for _ in range(H)]

    def set(self, x, y, col):
        if 0 <= x < W and 0 <= y < H and col is not None:
            self.p[y][x] = col

    def get(self, x, y):
        if 0 <= x < W and 0 <= y < H:
            return self.p[y][x]
        return None

    def rect(self, x0, y0, x1, y1, col):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, col)

    def row(self, y, hw, col, cx=16):
        self.rect(cx - hw, y, cx + hw - 1, y, col)

    def outline(self):
        add = []
        for y in range(H):
            for x in range(W):
                if self.p[y][x] is not None:
                    continue
                best = None
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = self.get(x + dx, y + dy)
                    if n is not None and (best is None or sum(n[:3]) < sum(best[:3])):
                        best = n
                if best is not None:
                    add.append((x, y, tuple(int(v * 0.45) for v in best[:3]) + (255,)))
        for x, y, col in add:
            self.p[y][x] = col

    def image(self):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for y in range(H):
            for x in range(W):
                if self.p[y][x] is not None:
                    img.putpixel((x, y), self.p[y][x])
        return img


def layout(cfg):
    ground = 46
    shoe_top = ground - 1
    leg_bot = shoe_top - 1
    leg_top = leg_bot - cfg["leg"] + 1
    tb = leg_top - 1
    tt = tb - 10
    ht = tt - 15
    return dict(ground=ground, shoe_top=shoe_top, leg_bot=leg_bot, leg_top=leg_top, tb=tb, tt=tt, ht=ht)


# ---------------------------------------------------------------- 의상 색

A_HOOD = (c("#dcc7a2"), c("#b9a07a"), c("#eee2c8"))
A_JEAN = (c("#4c71a8"), c("#3a5686"), c("#6c90c6"))
A_SHOE = (c("#f0f0f0"), c("#c4c4cc"))
A_STRING = c("#f5d03f")

B_COAT = (c("#2f2f3b"), c("#1f1f29"), c("#47475c"))
B_SHIRT = (c("#f4f4f8"), c("#cfd0de"))
B_PANTS = (c("#262630"), c("#1a1a22"), c("#3a3a4a"))
B_SHOE = (c("#17171c"), c("#3c3c48"))
B_GLASS = c("#121216")

C_CARD = (c("#7f8f3e"), c("#62702b"), c("#9cad57"))
C_BLOUSE = (c("#f4ebd3"), c("#ddd0ae"))
C_SKIRT = (c("#5c3f2f"), c("#452e22"), c("#76533f"))
C_SHOE = (c("#2e2420"), c("#4e403a"))


# ---------------------------------------------------------------- 몸통 (정면/뒷면 공통)

def draw_arms_front(cv, L, base, sh, cuff, arm_dy):
    tt = L["tt"]
    for (x0, x1, dy, inner) in ((9, 10, arm_dy[0], 10), (21, 22, arm_dy[1], 21)):
        cv.rect(x0, tt + 1, x1, tt + 8 + dy, base)
        cv.rect(inner, tt + 1, inner, tt + 8 + dy, sh)
        if cuff is not None:
            cv.rect(x0, tt + 8 + dy, x1, tt + 8 + dy, cuff)
        cv.rect(x0, tt + 9 + dy, x1, tt + 10 + dy, SKIN)
        cv.set(x0 if x0 == 9 else x1, tt + 10 + dy, SKIN_SH)


def draw_torso_front(cv, who, L, arm_dy, back=False):
    tt, tb = L["tt"], L["tb"]
    if who == "A":
        base, sh, hi = A_HOOD
        cv.rect(10, tt, 21, tt, base)
        cv.rect(11, tt, 20, tb, base)
        draw_arms_front(cv, L, base, sh, sh, arm_dy)
        cv.rect(11, tb, 20, tb, sh)
        if not back:
            cv.rect(11, tt, 13, tt + 1, sh)
            cv.rect(18, tt, 20, tt + 1, sh)
            cv.rect(14, tt + 2, 14, tt + 5, A_STRING)
            cv.rect(17, tt + 2, 17, tt + 5, A_STRING)
            cv.rect(12, tt + 6, 19, tt + 6, sh)
            cv.set(12, tt + 7, sh)
            cv.set(19, tt + 7, sh)
            cv.set(11, tt + 2, hi)
        else:
            cv.rect(12, tt, 19, tt + 4, sh)
            cv.rect(13, tt, 18, tt + 3, base)
            cv.rect(13, tt + 4, 18, tt + 4, sh)
    elif who == "B":
        base, sh, hi = B_COAT
        cv.rect(10, tt, 21, tt, base)
        cv.rect(11, tt, 20, tb, base)
        draw_arms_front(cv, L, base, sh, B_SHIRT[0], arm_dy)
        if not back:
            ws, wsh = B_SHIRT
            cv.rect(13, tt, 18, tt, ws)
            cv.rect(14, tt + 1, 17, tt + 1, ws)
            cv.rect(15, tt + 2, 16, tt + 4, ws)
            cv.set(15, tt + 4, wsh)
            cv.set(13, tt + 1, hi)
            cv.set(18, tt + 1, hi)
            cv.set(14, tt + 2, hi)
            cv.set(17, tt + 2, hi)
            cv.rect(15, tt + 5, 16, tb, sh)
            cv.set(16, tt + 6, hi)
            cv.set(16, tt + 8, hi)
        else:
            cv.rect(13, tt, 18, tt, B_SHIRT[0])
            cv.rect(15, tt + 3, 16, tb, sh)
        cv.rect(11, tb, 20, tb, sh)
    else:
        base, sh, hi = C_CARD
        cv.rect(10, tt, 21, tt, base)
        cv.rect(11, tt, 20, tb, base)
        draw_arms_front(cv, L, base, sh, sh, arm_dy)
        if not back:
            bl, bsh = C_BLOUSE
            cv.rect(14, tt, 17, tb, bl)
            cv.rect(13, tt, 18, tt, bl)
            cv.set(15, tt + 3, bsh)
            cv.set(15, tt + 6, bsh)
            cv.rect(13, tt + 1, 13, tb, sh)
            cv.rect(18, tt + 1, 18, tb, sh)
            cv.set(12, tt + 2, hi)
        cv.rect(11, tb, 20, tb, sh)


def draw_legs_front(cv, who, L, raise_):
    lt, lb, st, g = L["leg_top"], L["leg_bot"], L["shoe_top"], L["ground"]
    if who == "C":
        base, sh, hi = C_SKIRT
        n = lb - lt
        for i in range(n):
            w = 6 + min(2, i // 3)
            cv.rect(16 - w, lt + i, 15 + w, lt + i, base)
        cv.rect(16 - 8, lt + n - 1, 15 + 8, lt + n - 1, sh)
        cv.rect(15, lt + 1, 16, lt + n - 2, sh)
        cv.set(11, lt + 2, hi)
        cv.set(10, lt + 5, hi)
        for (x0, r) in ((12, raise_[0]), (18, raise_[1])):
            cv.rect(x0, lb - r, x0 + 1, lb - r, SKIN)
            cv.rect(x0 - 1, st - r, x0 + 2, g - r, C_SHOE[0])
            cv.set(x0, st - r, C_SHOE[1])
        return
    pants = A_JEAN if who == "A" else B_PANTS
    shoe = A_SHOE if who == "A" else B_SHOE
    base, sh, hi = pants
    cv.rect(11, lt, 20, lt + 1, base)
    for (x0, r, inner) in ((11, raise_[0], 14), (17, raise_[1], 17)):
        cv.rect(x0, lt + 2, x0 + 3, lb - r, base)
        cv.rect(inner, lt + 2, inner, lb - r, sh)
        cv.set(x0 + (1 if x0 == 11 else 2), lt + 3, hi)
        cv.rect(x0, st - r, x0 + 3, g - r, shoe[0])
        cv.rect(x0, g - r, x0 + 3, g - r, shoe[1])
    if who == "A":
        cv.rect(11, lt, 20, lt, sh)


# ---------------------------------------------------------------- 머리

def draw_head_front(cv, L):
    ht = L["ht"]
    for i, hw in enumerate(HEAD):
        cv.row(ht + i, hw, SKIN)
    cv.row(ht + 15, 4, SKIN_SH)


def draw_face_front(cv, who, cfg, L):
    ht = L["ht"]
    ey = ht + 9
    iris, iris_d = cfg["eye"]
    for (x0, tail) in ((11, 10), (19, 21)):
        cv.rect(x0, ey, x0 + 1, ey, LASH)
        cv.set(tail, ey, LASH)
        cv.set(x0, ey + 1, WHITE)
        cv.set(x0 + 1, ey + 1, iris)
        cv.set(x0, ey + 2, iris)
        cv.set(x0 + 1, ey + 2, iris_d)
    if cfg["blush"]:
        cv.set(10, ey + 3, BLUSH)
        cv.set(21, ey + 3, BLUSH)
    if who == "B":
        cv.rect(15, ey + 4, 16, ey + 4, cfg["mouth"])
        # 안경 (검은 얇은 테)
        for x0 in (10, 18):
            for x in range(x0, x0 + 4):
                cv.set(x, ey - 1, B_GLASS)
                cv.set(x, ey + 3, B_GLASS)
            for y in range(ey - 1, ey + 4):
                cv.set(x0, y, B_GLASS)
                cv.set(x0 + 3, y, B_GLASS)
        cv.rect(14, ey, 17, ey, B_GLASS)
        cv.set(9, ey, B_GLASS)
        cv.set(22, ey, B_GLASS)
        # 눈 위치를 안경 안쪽으로 다시 칠함
        for (x0, tail) in ((11, None), (19, None)):
            cv.rect(x0, ey, x0 + 1, ey, LASH)
    else:
        cv.set(15, ey + 4, cfg["mouth"])
        cv.set(16, ey + 4, cfg["mouth"])
        if who == "C":
            cv.set(14, ey + 3, cfg["mouth"])
            cv.set(17, ey + 3, cfg["mouth"])
            cv.set(15, ey + 4, cfg["mouth"])
            cv.set(16, ey + 4, cfg["mouth"])


def hair_cap(cv, L, hair):
    base, sh, hi = hair
    ht = L["ht"]
    for i, hw in enumerate(CAP):
        cv.row(ht - 1 + i, hw, base)
    # 하이라이트 (천사 링)
    cv.rect(11, ht + 1, 13, ht + 1, hi)
    cv.rect(18, ht + 1, 20, ht + 1, hi)
    cv.rect(10, ht + 2, 11, ht + 2, hi)


def draw_hair_front(cv, who, cfg, L, layer):
    base, sh, hi = cfg["hair"]
    ht, tt = L["ht"], L["tt"]
    if layer == "back":
        if who == "A":
            cv.rect(8, ht + 4, 23, tt + 3, base)
            cv.rect(9, tt + 4, 22, tt + 5, sh)
        elif who == "C":
            cv.rect(8, ht + 4, 23, ht + 15, sh)
        else:
            cv.rect(9, ht + 4, 22, ht + 13, sh)
        return

    hair_cap(cv, L, cfg["hair"])
    y = ht + 6
    if who == "A":
        cv.rect(7, y, 24, y, base)
        for x in (12, 13, 18, 19):
            cv.set(x, y, SKIN)
        for x in (8, 9, 10, 15, 16, 21, 22, 23):
            cv.set(x, y + 1, base)
        cv.rect(14, y, 17, y, sh)
        # 양옆으로 흘러내리는 머리 (어깨 아래까지)
        for (x0, x1, ish) in ((7, 9, 9), (22, 24, 22)):
            cv.rect(x0, y, x1, tt + 4, base)
            cv.rect(ish, y + 2, ish, tt + 4, sh)
        cv.rect(7, tt + 5, 8, tt + 5, base)
        cv.rect(23, tt + 5, 24, tt + 5, base)
        cv.set(8, ht + 8, hi)
        cv.set(23, ht + 8, hi)
    elif who == "B":
        cv.rect(7, y, 24, y, base)
        for x in (11, 12, 13, 19, 20):
            cv.set(x, y, SKIN)
        for x in (8, 14, 15, 16, 22, 23):
            cv.set(x, y + 1, base)
        cv.set(15, y + 2, base)
        cv.rect(14, y - 1, 16, y, sh)
        # 얼굴을 감싸는 옆머리 (가늘게) + 삐져나온 잔머리
        cv.rect(7, y, 8, ht + 14, base)
        cv.rect(23, y, 24, ht + 14, base)
        cv.set(8, ht + 15, base)
        cv.set(23, ht + 15, base)
        cv.rect(8, y + 2, 8, ht + 13, sh)
        cv.rect(23, y + 2, 23, ht + 13, sh)
        cv.set(17, ht - 2, base)
        cv.set(18, ht - 3, base)
        cv.set(25, ht + 3, base)
        cv.set(6, ht + 10, base)
    else:
        cv.rect(7, y, 24, y + 1, base)
        for x in (11, 15, 20):
            cv.set(x, y + 1, SKIN)
        cv.rect(10, y + 1, 21, y + 1, sh)
        for x in (11, 15, 20):
            cv.set(x, y + 1, SKIN)
        # 턱선까지 오는 단발
        cv.rect(7, y, 9, ht + 14, base)
        cv.rect(22, y, 24, ht + 14, base)
        cv.rect(8, ht + 15, 10, ht + 15, base)
        cv.rect(21, ht + 15, 23, ht + 15, base)
        cv.rect(9, y + 2, 9, ht + 14, sh)
        cv.rect(22, y + 2, 22, ht + 14, sh)
        cv.set(8, ht + 8, hi)
        cv.set(23, ht + 8, hi)


def draw_hair_back(cv, who, cfg, L):
    """뒷모습: 머리가 머리통 전체를 덮는다."""
    base, sh, hi = cfg["hair"]
    ht, tt = L["ht"], L["tt"]
    for i, hw in enumerate(CAP):
        cv.row(ht - 1 + i, hw, base)
    for i, hw in enumerate(HEAD[6:]):
        cv.row(ht + 6 + i, hw + 1, base)
    cv.rect(11, ht + 1, 13, ht + 1, hi)
    cv.rect(18, ht + 1, 20, ht + 1, hi)
    if who == "A":
        cv.rect(7, ht + 6, 24, tt + 4, base)
        cv.rect(8, tt + 5, 23, tt + 5, base)
        for x in (11, 15, 16, 20):
            cv.rect(x, ht + 8, x, tt + 4, sh)
    elif who == "B":
        cv.rect(14, ht + 10, 17, ht + 15, sh)
        cv.rect(14, ht + 11, 17, ht + 11, c("#5c6672"))
        cv.rect(14, ht + 12, 17, tt + 6, base)
        cv.rect(15, tt + 7, 16, tt + 9, base)
        cv.rect(15, ht + 13, 15, tt + 8, sh)
        # 검은 마이에 묻히지 않게 포니테일 테두리를 밝게
        cv.rect(13, ht + 13, 13, tt + 5, hi)
        cv.rect(18, ht + 13, 18, tt + 5, hi)
        cv.rect(14, tt + 7, 14, tt + 8, hi)
        cv.rect(17, tt + 7, 17, tt + 8, hi)
        cv.rect(16, ht + 13, 16, tt + 7, hi)
        cv.set(17, ht - 2, base)
        cv.set(18, ht - 3, base)
    else:
        cv.rect(8, ht + 15, 23, ht + 15, base)
        cv.rect(9, ht + 16, 22, ht + 16, base)
        for x in (12, 16, 19):
            cv.rect(x, ht + 8, x, ht + 15, sh)


# ---------------------------------------------------------------- 옆모습 (왼쪽을 봄)

def draw_side(cv, who, cfg, L, step):
    """step: 0 = 서 있기, 1/2 = 걷기"""
    base_h, sh_h, hi_h = cfg["hair"]
    ht, tt, tb = L["ht"], L["tt"], L["tb"]
    lt, lb, st, g = L["leg_top"], L["leg_bot"], L["shoe_top"], L["ground"]

    # 뒤쪽 머리 (몸 뒤로)
    if who == "A":
        cv.rect(17, ht + 4, 23, tt + 4, base_h)
        cv.rect(18, tt + 5, 22, tt + 5, sh_h)
    elif who == "B":
        tie = c("#5c6672")
        cv.rect(22, ht + 9, 24, ht + 10, base_h)
        cv.set(23, ht + 11, tie)
        cv.set(24, ht + 11, tie)
        cv.rect(23, ht + 12, 25, tt + 5, base_h)
        cv.rect(24, tt + 6, 24, tt + 8, base_h)
        cv.rect(25, ht + 13, 25, tt + 4, sh_h)

    # 다리 / 치마
    far = 0 if step == 0 else (1 if step == 1 else 2)
    if who == "C":
        base, sh, hi = C_SKIRT
        n = lb - lt
        for i in range(n):
            w = min(2, i // 3)
            cv.rect(12 - w, lt + i, 19 + w, lt + i, base)
        cv.rect(10, lt + n - 1, 21, lt + n - 1, sh)
        cv.rect(17, lt + 1, 18, lt + n - 2, sh)
        if step == 0:
            cv.rect(14, lb, 15, lb, SKIN)
            cv.rect(12, st, 16, g, C_SHOE[0])
        else:
            fx, bx = (12, 18) if step == 1 else (13, 17)
            cv.rect(bx, lb, bx + 1, lb, SKIN_SH)
            cv.rect(bx, st, bx + 3, g, C_SHOE[1])
            cv.rect(fx, lb, fx + 1, lb, SKIN)
            cv.rect(fx - 1, st, fx + 2, g, C_SHOE[0])
    else:
        pants = A_JEAN if who == "A" else B_PANTS
        shoe = A_SHOE if who == "A" else B_SHOE
        base, sh, hi = pants
        cv.rect(13, lt, 18, lt + 1, base)
        if step == 0:
            cv.rect(14, lt, 17, lb, base)
            cv.rect(17, lt + 2, 17, lb, sh)
            cv.rect(12, st, 17, g, shoe[0])
            cv.rect(12, g, 17, g, shoe[1])
        else:
            d = 2 if step == 1 else 1
            # 뒤쪽 다리 (어둡게)
            cv.rect(16 + d - 1, lt + 2, 19 + d - 1, lb, sh)
            cv.rect(16 + d - 1, st, 20 + d - 1, g, shoe[1])
            # 앞쪽 다리
            cv.rect(13 - d + 1, lt + 2, 16 - d + 1, lb, base)
            cv.rect(11 - d + 1, st, 16 - d + 1, g, shoe[0])
            cv.rect(11 - d + 1, g, 16 - d + 1, g, shoe[1])

    # 몸통
    if who == "A":
        base, sh, hi = A_HOOD
    elif who == "B":
        base, sh, hi = B_COAT
    else:
        base, sh, hi = C_CARD
    cv.rect(12, tt, 19, tb, base)
    cv.rect(12, tb, 19, tb, sh)
    if who == "A":
        cv.rect(17, tt, 20, tt + 2, sh)
        cv.rect(12, tt + 1, 12, tt + 4, A_STRING)
    elif who == "B":
        cv.rect(12, tt, 12, tt + 3, B_SHIRT[0])
        cv.rect(13, tt, 13, tt + 4, hi)
    else:
        cv.rect(12, tt, 12, tb - 1, C_BLOUSE[0])
        cv.rect(13, tt, 13, tb - 1, sh)

    # 팔 (흔들기)
    ax = 15 + (0 if step == 0 else (-1 if step == 1 else 1))
    cv.rect(ax, tt + 1, ax + 2, tt + 8, base)
    cv.rect(ax + 2, tt + 2, ax + 2, tt + 8, sh)
    if who == "B":
        cv.rect(ax, tt + 8, ax + 2, tt + 8, B_SHIRT[0])
    cv.rect(ax, tt + 9, ax + 2, tt + 10, SKIN)
    cv.set(ax + 2, tt + 10, SKIN_SH)

    # 머리통
    for i, hw in enumerate(HEAD):
        cv.row(ht + i, hw, SKIN)
    cv.row(ht + 15, 4, SKIN_SH)
    ey = ht + 9
    iris, iris_d = cfg["eye"]
    cv.rect(10, ey, 11, ey, LASH)
    cv.set(12, ey, LASH)
    cv.set(10, ey + 1, iris)
    cv.set(11, ey + 1, WHITE)
    cv.set(10, ey + 2, iris_d)
    cv.set(11, ey + 2, iris)
    cv.set(9, ey + 4, cfg["mouth"])
    if cfg["blush"]:
        cv.set(12, ey + 3, BLUSH)

    # 머리카락
    hair_cap(cv, L, cfg["hair"])
    y = ht + 6
    if who == "A":
        cv.rect(14, y, 24, tt + 1, base_h)
        cv.rect(8, y, 13, y, base_h)
        cv.set(8, y + 1, base_h)
        cv.set(9, y + 1, base_h)
        cv.rect(16, y + 2, 16, tt + 1, sh_h)
    elif who == "B":
        cv.rect(15, y, 24, ht + 12, base_h)
        cv.rect(8, y, 13, y, base_h)
        cv.set(8, y + 1, base_h)
        cv.set(13, y + 1, base_h)
        cv.rect(16, ey + 1, 17, ey + 2, SKIN_SH)
        cv.set(17, ht - 2, base_h)
        cv.set(18, ht - 3, base_h)
        # 안경
        for x in range(9, 13):
            cv.set(x, ey - 1, B_GLASS)
            cv.set(x, ey + 3, B_GLASS)
        for yy in range(ey - 1, ey + 4):
            cv.set(9, yy, B_GLASS)
            cv.set(12, yy, B_GLASS)
        cv.rect(13, ey, 16, ey, B_GLASS)
        cv.rect(10, ey, 11, ey, LASH)
    else:
        cv.rect(14, y, 24, ht + 14, base_h)
        cv.rect(15, ht + 15, 23, ht + 15, base_h)
        cv.rect(8, y, 13, y + 1, base_h)
        cv.set(10, y + 1, SKIN)
        cv.rect(16, y + 2, 16, ht + 14, sh_h)


# ---------------------------------------------------------------- 프레임 조립

def frame(who, direction, col):
    cfg = CHARS[who]
    L = layout(cfg)
    cv = Canvas()
    if direction in ("down", "up"):
        raise_ = [(1, 0), (0, 0), (0, 1)][col]
        arm_dy = [(1, -1), (0, 0), (-1, 1)][col]
        if direction == "down":
            draw_hair_front(cv, who, cfg, L, "back")
            draw_legs_front(cv, who, L, raise_)
            draw_torso_front(cv, who, L, arm_dy)
            draw_head_front(cv, L)
            draw_face_front(cv, who, cfg, L)
            draw_hair_front(cv, who, cfg, L, "front")
        else:
            draw_legs_front(cv, who, L, raise_)
            draw_torso_front(cv, who, L, arm_dy, back=True)
            draw_hair_back(cv, who, cfg, L)
    else:
        step = [1, 0, 2][col]
        draw_side(cv, who, cfg, L, step)
    cv.outline()
    img = cv.image()
    if direction == "right":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def sheet(who):
    img = Image.new("RGBA", (W * 3, H * 4), (0, 0, 0, 0))
    for r, d in enumerate(("down", "left", "right", "up")):
        for col in range(3):
            img.paste(frame(who, d, col), (col * W, r * H))
    return img


def background(w, h):
    bg = Image.new("RGBA", (w, h), c("#b9e09a"))
    d = ImageDraw.Draw(bg)
    for ty in range(0, h, 32):
        for tx in range(0, w, 32):
            if (tx // 32 + ty // 32) % 2:
                d.rectangle([tx, ty, tx + 31, ty + 31], fill=c("#aed68e"))
    return bg


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for who in CHARS:
        sheet(who).save(OUT / f"{who}_test.png")

    scale = 6
    # 정면 / 옆 / 뒤 미리보기
    prev = background(W * 3 * 3 + 16, H + 8)
    for i, who in enumerate(CHARS):
        for j, d in enumerate(("down", "left", "up")):
            spr = frame(who, d, 1)
            prev.alpha_composite(spr, (i * (W * 3 + 8) + j * W, 4))
    prev.resize((prev.width * scale, prev.height * scale), Image.NEAREST).save(OUT / "preview.png")

    # 걷기 애니메이션 GIF
    frames = []
    for col in (0, 1, 2, 1):
        f = background(W * 6 + 8, H * 2 + 8)
        for i, who in enumerate(CHARS):
            f.alpha_composite(frame(who, "down", col), (i * W, 4))
            f.alpha_composite(frame(who, "left", col), (W * 3 + 8 + i * W, 4))
            f.alpha_composite(frame(who, "up", col), (i * W, H + 4))
            f.alpha_composite(frame(who, "right", col), (W * 3 + 8 + i * W, H + 4))
        frames.append(f.resize((f.width * scale, f.height * scale), Image.NEAREST).convert("RGB"))
    frames[0].save(OUT / "walk.gif", save_all=True, append_images=frames[1:], duration=180, loop=0)


if __name__ == "__main__":
    main()
