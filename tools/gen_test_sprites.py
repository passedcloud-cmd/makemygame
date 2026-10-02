"""테스트용 캐릭터 도트 생성기 (2등신 버전).

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
BLUSH = c("#f5b0a0")

# 2등신: 머리가 키의 절반 정도
HEAD = [5, 7, 8, 9, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 9, 9, 8, 7, 5]
CAP = [5, 7, 9, 10, 10, 11, 11, 11]
HEAD_H = len(HEAD)
TORSO_H = 8

CHARS = {
    "A": dict(
        leg=6,
        hair=(c("#e9cf8e"), c("#c8a564"), c("#f7e7b6")),
        eye=(c("#b8834c"), c("#7d5028")),
        mouth=c("#d07a6a"),
        blush=True,
    ),
    "B": dict(
        leg=8,
        hair=(c("#2c2c3a"), c("#1b1b25"), c("#50506c")),
        eye=(c("#86cff2"), c("#4a94c2")),
        mouth=c("#b0756a"),
        blush=False,
    ),
    "C": dict(
        leg=6,
        hair=(c("#8b5b3d"), c("#6a4029"), c("#ab7754")),
        eye=(c("#58ad5f"), c("#2f7037")),
        mouth=c("#d07a6a"),
        blush=True,
    ),
}

# ---------------------------------------------------------------- 의상 색

A_HOOD = (c("#c9a266"), c("#a47f43"), c("#ddbd88"))   # 진한 베이지 ~ 황토
A_STRING = c("#ffe36b")
A_JEAN = (c("#4c71a8"), c("#3a5686"), c("#6c90c6"))
A_SHOE = (c("#f0f0f0"), c("#c4c4cc"))

B_COAT = (c("#8ccbec"), c("#64a6cd"), c("#b6e2f8"))   # 하늘색 마이
B_SHIRT = (c("#f7f7fa"), c("#d4d5e2"))
B_PANTS = (c("#262630"), c("#1a1a22"), c("#3a3a4a"))
B_SHOE = (c("#17171c"), c("#3c3c48"))
B_GLASS = c("#121216")
B_TIE = c("#5c6672")

C_CARD = (c("#7f8f3e"), c("#62702b"), c("#9cad57"))   # 올리브 가디건
C_BLOUSE = (c("#f4ebd3"), c("#ddd0ae"))
C_SKIRT = (c("#5c3f2f"), c("#452e22"), c("#76533f"))
C_SHOE = (c("#2e2420"), c("#4e403a"))

TOP = {"A": A_HOOD, "B": B_COAT, "C": C_CARD}


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
        """빈 칸 중 그림과 맞닿은 칸에 이웃 색을 어둡게 해서 테두리를 그린다."""
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
    tt = tb - TORSO_H + 1
    ht = tt - HEAD_H + 1          # 턱이 옷깃 위로 1줄 겹친다
    return dict(ground=ground, shoe_top=shoe_top, leg_bot=leg_bot,
                leg_top=leg_top, tb=tb, tt=tt, ht=ht, ey=ht + 11)


# ---------------------------------------------------------------- 정면 / 뒷면 몸

def draw_arms_front(cv, L, top, cuff, arm_dy):
    base, sh, _ = top
    tt = L["tt"]
    for (x0, x1, dy, inner) in ((9, 10, arm_dy[0], 10), (21, 22, arm_dy[1], 21)):
        cv.rect(x0, tt + 1, x1, tt + 5 + dy, base)
        cv.rect(inner, tt + 1, inner, tt + 5 + dy, sh)
        cv.rect(x0, tt + 5 + dy, x1, tt + 5 + dy, cuff or sh)
        cv.rect(x0, tt + 6 + dy, x1, tt + 7 + dy, SKIN)
        cv.set(x0 if x0 == 9 else x1, tt + 7 + dy, SKIN_SH)


def draw_torso_front(cv, who, L, arm_dy, back=False):
    tt, tb = L["tt"], L["tb"]
    base, sh, hi = TOP[who]
    cv.rect(10, tt, 21, tt, base)
    cv.rect(11, tt, 20, tb, base)
    draw_arms_front(cv, L, TOP[who], B_SHIRT[0] if who == "B" else None, arm_dy)
    cv.rect(11, tb, 20, tb, sh)
    if who == "A":
        if not back:
            cv.rect(11, tt, 13, tt + 1, sh)
            cv.rect(18, tt, 20, tt + 1, sh)
            cv.rect(14, tt + 1, 14, tt + 3, A_STRING)
            cv.rect(17, tt + 1, 17, tt + 3, A_STRING)
            cv.rect(12, tt + 5, 19, tt + 5, sh)
            cv.set(11, tt + 2, hi)
        else:
            cv.rect(12, tt, 19, tt + 3, sh)
            cv.rect(13, tt, 18, tt + 2, base)
    elif who == "B":
        if not back:
            ws, wsh = B_SHIRT
            cv.rect(13, tt, 18, tt, ws)
            cv.rect(14, tt + 1, 17, tt + 1, ws)
            cv.rect(15, tt + 2, 16, tt + 3, ws)
            cv.set(15, tt + 3, wsh)
            cv.set(13, tt + 1, hi)
            cv.set(18, tt + 1, hi)
            cv.set(14, tt + 2, hi)
            cv.set(17, tt + 2, hi)
            cv.rect(15, tt + 4, 15, tb, sh)
            cv.set(16, tt + 5, B_SHIRT[0])
        else:
            cv.rect(13, tt, 18, tt, B_SHIRT[0])
            cv.rect(15, tt + 2, 16, tb, sh)
    else:
        if not back:
            bl, bsh = C_BLOUSE
            cv.rect(13, tt, 18, tt, bl)
            cv.rect(14, tt, 17, tb - 1, bl)
            cv.set(15, tt + 2, bsh)
            cv.set(15, tt + 4, bsh)
            cv.rect(13, tt + 1, 13, tb, sh)
            cv.rect(18, tt + 1, 18, tb, sh)
            cv.set(12, tt + 2, hi)


def draw_legs_front(cv, who, L, raise_):
    lt, lb, st, g = L["leg_top"], L["leg_bot"], L["shoe_top"], L["ground"]
    if who == "C":
        base, sh, hi = C_SKIRT
        n = lb - lt
        for i in range(n):
            w = 6 + min(2, (i + 1) // 2)
            cv.rect(16 - w, lt + i, 15 + w, lt + i, base)
        cv.rect(8, lt + n - 1, 23, lt + n - 1, sh)
        cv.rect(15, lt + 1, 16, lt + n - 2, sh)
        cv.set(11, lt + 1, hi)
        cv.set(10, lt + 3, hi)
        for (x0, r) in ((12, raise_[0]), (18, raise_[1])):
            cv.rect(x0, lb - r, x0 + 1, lb - r, SKIN)
            cv.rect(x0 - 1, st - r, x0 + 2, g - r, C_SHOE[0])
            cv.set(x0, st - r, C_SHOE[1])
        return
    base, sh, hi = A_JEAN if who == "A" else B_PANTS
    shoe = A_SHOE if who == "A" else B_SHOE
    cv.rect(11, lt, 20, lt, base)
    for (x0, r, inner) in ((11, raise_[0], 14), (17, raise_[1], 17)):
        cv.rect(x0, lt + 1, x0 + 3, lb - r, base)
        cv.rect(inner, lt + 1, inner, lb - r, sh)
        cv.set(x0 + (1 if x0 == 11 else 2), lt + 2, hi)
        cv.rect(x0, st - r, x0 + 3, g - r, shoe[0])
        cv.rect(x0, g - r, x0 + 3, g - r, shoe[1])


# ---------------------------------------------------------------- 얼굴 / 머리

def draw_head(cv, L):
    ht = L["ht"]
    for i, hw in enumerate(HEAD):
        cv.row(ht + i, hw, SKIN)
    cv.row(ht + HEAD_H - 1, HEAD[-1], SKIN_SH)


def draw_eye(cv, x0, ey, iris, iris_d, lash_x):
    """3x4 큰 눈. x0 = 눈의 왼쪽 끝."""
    for x in lash_x:
        cv.set(x, ey, LASH)
    cv.rect(x0, ey + 1, x0 + 2, ey + 1, iris_d)
    cv.set(x0, ey + 2, WHITE)
    cv.set(x0 + 1, ey + 2, iris)
    cv.set(x0 + 2, ey + 2, iris_d)
    cv.rect(x0, ey + 3, x0 + 2, ey + 3, iris)
    cv.set(x0 + 2, ey + 3, c("#ffffff") if False else iris)


def draw_face_front(cv, who, cfg, L):
    ey = L["ey"]
    iris, iris_d = cfg["eye"]
    if who == "B":
        draw_eye(cv, 10, ey, iris, iris_d, range(10, 13))
        draw_eye(cv, 19, ey, iris, iris_d, range(19, 22))
        # 안경 (검은 얇은 테)
        for x0 in (9, 18):
            cv.rect(x0, ey - 1, x0 + 4, ey - 1, B_GLASS)
            cv.rect(x0, ey + 4, x0 + 4, ey + 4, B_GLASS)
            cv.rect(x0, ey - 1, x0, ey + 4, B_GLASS)
            cv.rect(x0 + 4, ey - 1, x0 + 4, ey + 4, B_GLASS)
        cv.rect(14, ey + 1, 17, ey + 1, B_GLASS)
        cv.rect(7, ey + 1, 8, ey + 1, B_GLASS)
        cv.rect(23, ey + 1, 24, ey + 1, B_GLASS)
        cv.rect(15, ey + 6, 16, ey + 6, cfg["mouth"])
    else:
        draw_eye(cv, 10, ey, iris, iris_d, range(9, 13))
        draw_eye(cv, 19, ey, iris, iris_d, range(19, 23))
        if who == "C":
            cv.set(14, ey + 5, cfg["mouth"])
            cv.set(17, ey + 5, cfg["mouth"])
            cv.rect(15, ey + 6, 16, ey + 6, cfg["mouth"])
        else:
            cv.rect(15, ey + 6, 16, ey + 6, cfg["mouth"])
    if cfg["blush"]:
        cv.rect(8, ey + 5, 9, ey + 5, BLUSH)
        cv.rect(22, ey + 5, 23, ey + 5, BLUSH)


def hair_cap(cv, L, hair):
    base, sh, hi = hair
    ht = L["ht"]
    for i, hw in enumerate(CAP):
        cv.row(ht - 1 + i, hw, base)
    # 하이라이트 (천사 링)
    cv.rect(10, ht + 2, 13, ht + 2, hi)
    cv.rect(18, ht + 2, 21, ht + 2, hi)
    cv.rect(8, ht + 3, 9, ht + 3, hi)


def draw_hair_front(cv, who, cfg, L, layer):
    base, sh, hi = cfg["hair"]
    ht, tt = L["ht"], L["tt"]
    if layer == "back":
        if who == "A":
            cv.rect(6, ht + 5, 25, tt + 3, base)
            cv.rect(7, tt + 4, 24, tt + 4, sh)
        elif who == "C":
            cv.rect(6, ht + 5, 25, ht + 18, sh)
        else:
            cv.rect(7, ht + 5, 24, ht + 17, sh)
        return

    hair_cap(cv, L, cfg["hair"])
    y = ht + 7   # 앞머리 시작 줄
    if who == "A":
        cv.rect(5, y, 26, y + 1, base)
        for x in (10, 11, 20, 21):
            cv.set(x, y + 1, SKIN)
        for x in (7, 8, 13, 14, 17, 18, 23, 24):
            cv.set(x, y + 2, base)
        cv.rect(14, y, 17, y, sh)
        # 어깨 아래까지 흘러내리는 옆머리
        for (x0, x1, ish) in ((5, 7, 7), (24, 26, 24)):
            cv.rect(x0, y, x1, tt + 4, base)
            cv.rect(ish, y + 3, ish, tt + 4, sh)
        cv.rect(5, tt + 5, 6, tt + 5, base)
        cv.rect(25, tt + 5, 26, tt + 5, base)
        cv.set(6, ht + 10, hi)
        cv.set(25, ht + 10, hi)
    elif who == "B":
        cv.rect(5, y, 26, y, base)
        cv.rect(5, y + 1, 9, y + 1, base)
        cv.rect(13, y + 1, 18, y + 1, base)
        cv.rect(22, y + 1, 26, y + 1, base)
        for x in (6, 14, 15, 17, 24):
            cv.set(x, y + 2, base)
        cv.set(15, y + 3, base)
        cv.rect(13, y - 1, 17, y, sh)
        # 얼굴을 감싸는 가는 옆머리 + 삐져나온 잔머리
        cv.rect(5, y, 6, ht + 18, base)
        cv.rect(25, y, 26, ht + 18, base)
        cv.rect(6, y + 3, 6, ht + 17, sh)
        cv.rect(25, y + 3, 25, ht + 17, sh)
        cv.set(17, ht - 2, base)
        cv.set(18, ht - 3, base)
        cv.set(19, ht - 3, base)
        cv.set(27, ht + 4, base)
        cv.set(4, ht + 12, base)
    else:
        cv.rect(5, y, 26, y + 2, base)
        cv.rect(8, y + 2, 23, y + 2, sh)
        for x in (10, 15, 16, 21):
            cv.set(x, y + 2, SKIN)
        # 턱선까지 오는 단발
        cv.rect(5, y, 7, ht + 18, base)
        cv.rect(24, y, 26, ht + 18, base)
        cv.rect(6, ht + 19, 8, ht + 19, base)
        cv.rect(23, ht + 19, 25, ht + 19, base)
        cv.rect(7, y + 3, 7, ht + 18, sh)
        cv.rect(24, y + 3, 24, ht + 18, sh)
        cv.set(6, ht + 11, hi)
        cv.set(25, ht + 11, hi)


def draw_hair_back(cv, who, cfg, L):
    """뒷모습: 머리가 머리통 전체를 덮는다."""
    base, sh, hi = cfg["hair"]
    ht, tt = L["ht"], L["tt"]
    for i, hw in enumerate(CAP):
        cv.row(ht - 1 + i, hw, base)
    for i, hw in enumerate(HEAD[7:]):
        cv.row(ht + 7 + i, hw + 1, base)
    cv.rect(10, ht + 2, 13, ht + 2, hi)
    cv.rect(18, ht + 2, 21, ht + 2, hi)
    if who == "A":
        cv.rect(5, ht + 7, 26, tt + 4, base)
        cv.rect(6, tt + 5, 25, tt + 5, base)
        for x in (10, 15, 16, 21):
            cv.rect(x, ht + 9, x, tt + 4, sh)
    elif who == "B":
        cv.rect(14, ht + 13, 17, ht + 13, B_TIE)
        cv.rect(14, ht + 14, 17, tt + 4, base)
        cv.rect(15, tt + 5, 16, tt + 7, base)
        cv.rect(15, ht + 15, 15, tt + 6, sh)
        cv.rect(16, ht + 15, 16, tt + 5, hi)
        cv.set(17, ht - 2, base)
        cv.set(18, ht - 3, base)
        cv.set(19, ht - 3, base)
    else:
        cv.rect(6, ht + 19, 25, ht + 19, base)
        cv.rect(8, ht + 20, 23, ht + 20, base)
        for x in (11, 16, 20):
            cv.rect(x, ht + 9, x, ht + 19, sh)


# ---------------------------------------------------------------- 옆모습 (왼쪽을 봄)

def draw_side(cv, who, cfg, L, step):
    """step: 0 = 서 있기, 1/2 = 걷기"""
    hb, hs, hh = cfg["hair"]
    ht, tt, tb, ey = L["ht"], L["tt"], L["tb"], L["ey"]
    lt, lb, st, g = L["leg_top"], L["leg_bot"], L["shoe_top"], L["ground"]

    # 몸 뒤로 넘어가는 머리
    if who == "A":
        cv.rect(16, ht + 5, 25, tt + 4, hb)
        cv.rect(17, tt + 5, 24, tt + 5, hs)
    elif who == "B":
        cv.rect(23, ht + 11, 26, ht + 12, hb)
        cv.rect(24, ht + 13, 26, ht + 13, B_TIE)
        cv.rect(24, ht + 14, 27, tt + 3, hb)
        cv.rect(25, tt + 4, 26, tt + 6, hb)
        cv.rect(25, ht + 15, 25, tt + 3, hh)

    # 다리 / 치마
    if who == "C":
        base, sh, hi = C_SKIRT
        n = lb - lt
        for i in range(n):
            w = min(2, (i + 1) // 2)
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
        base, sh, hi = A_JEAN if who == "A" else B_PANTS
        shoe = A_SHOE if who == "A" else B_SHOE
        cv.rect(13, lt, 18, lt, base)
        if step == 0:
            cv.rect(14, lt, 17, lb, base)
            cv.rect(17, lt + 1, 17, lb, sh)
            cv.rect(12, st, 17, g, shoe[0])
            cv.rect(12, g, 17, g, shoe[1])
        else:
            d = 2 if step == 1 else 1
            cv.rect(15 + d, lt + 1, 18 + d, lb, sh)          # 뒤쪽 다리
            cv.rect(15 + d, st, 19 + d, g, shoe[1])
            cv.rect(14 - d, lt + 1, 17 - d, lb, base)        # 앞쪽 다리
            cv.rect(12 - d, st, 17 - d, g, shoe[0])
            cv.rect(12 - d, g, 17 - d, g, shoe[1])

    # 몸통
    base, sh, hi = TOP[who]
    cv.rect(12, tt, 19, tb, base)
    cv.rect(12, tb, 19, tb, sh)
    if who == "A":
        cv.rect(17, tt, 20, tt + 2, sh)
        cv.rect(12, tt + 1, 12, tt + 3, A_STRING)
    elif who == "B":
        cv.rect(12, tt, 12, tt + 2, B_SHIRT[0])
        cv.rect(13, tt, 13, tt + 3, hi)
    else:
        cv.rect(12, tt, 12, tb - 1, C_BLOUSE[0])
        cv.rect(13, tt, 13, tb - 1, sh)

    # 팔 (흔들기)
    ax = 15 + (0 if step == 0 else (-1 if step == 1 else 1))
    cv.rect(ax, tt + 1, ax + 2, tt + 5, base)
    cv.rect(ax + 2, tt + 2, ax + 2, tt + 5, sh)
    if who == "B":
        cv.rect(ax, tt + 5, ax + 2, tt + 5, B_SHIRT[0])
    cv.rect(ax, tt + 6, ax + 2, tt + 7, SKIN)
    cv.set(ax + 2, tt + 7, SKIN_SH)

    # 머리통 + 얼굴
    draw_head(cv, L)
    iris, iris_d = cfg["eye"]
    cv.rect(7, ey, 10, ey, LASH)
    cv.rect(7, ey + 1, 9, ey + 1, iris_d)
    cv.set(7, ey + 2, iris)
    cv.set(8, ey + 2, WHITE)
    cv.set(9, ey + 2, iris_d)
    cv.rect(7, ey + 3, 9, ey + 3, iris)
    cv.set(7, ey + 6, cfg["mouth"])
    if cfg["blush"]:
        cv.rect(10, ey + 5, 11, ey + 5, BLUSH)

    # 머리카락
    hair_cap(cv, L, cfg["hair"])
    y = ht + 7
    if who == "A":
        cv.rect(14, y, 26, tt + 1, hb)
        cv.rect(6, y, 13, y + 1, hb)
        cv.set(9, y + 1, SKIN)
        cv.rect(6, y + 2, 7, y + 2, hb)
        cv.rect(16, y + 3, 16, tt + 1, hs)
    elif who == "B":
        cv.rect(15, y, 25, ht + 15, hb)
        cv.rect(6, y, 13, y, hb)
        cv.rect(6, y + 1, 8, y + 1, hb)
        cv.set(12, y + 1, hb)
        cv.rect(16, ey + 1, 17, ey + 3, SKIN_SH)
        cv.set(17, ht - 2, hb)
        cv.set(18, ht - 3, hb)
        cv.set(19, ht - 3, hb)
        # 안경
        cv.rect(6, ey - 1, 10, ey - 1, B_GLASS)
        cv.rect(6, ey + 4, 10, ey + 4, B_GLASS)
        cv.rect(10, ey - 1, 10, ey + 4, B_GLASS)
        cv.rect(6, ey - 1, 6, ey + 4, B_GLASS)
        cv.rect(11, ey + 1, 16, ey + 1, B_GLASS)
    else:
        cv.rect(14, y, 26, ht + 18, hb)
        cv.rect(15, ht + 19, 25, ht + 19, hb)
        cv.rect(6, y, 13, y + 2, hb)
        cv.rect(8, y + 2, 13, y + 2, hs)
        cv.set(10, y + 2, SKIN)
        cv.rect(16, y + 3, 16, ht + 18, hs)


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
            draw_head(cv, L)
            draw_face_front(cv, who, cfg, L)
            draw_hair_front(cv, who, cfg, L, "front")
        else:
            draw_legs_front(cv, who, L, raise_)
            draw_torso_front(cv, who, L, arm_dy, back=True)
            draw_hair_back(cv, who, cfg, L)
    else:
        draw_side(cv, who, cfg, L, [1, 0, 2][col])
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


PORTRAIT_OUT = OUT.parent.parent / "portraits"
STANDING_OUT = OUT.parent.parent / "standing"


def portrait(who):
    """대화창용 임시 얼굴 그림 (32x32). 정면 도트에서 머리 부분만 잘라낸다."""
    L = layout(CHARS[who])
    top = L["ht"] - 4
    return frame(who, "down", 1).crop((0, top, 32, top + 32))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PORTRAIT_OUT.mkdir(parents=True, exist_ok=True)
    STANDING_OUT.mkdir(parents=True, exist_ok=True)
    for who in CHARS:
        sheet(who).save(OUT / f"{who}_test.png")
        portrait(who).save(PORTRAIT_OUT / f"{who}.png")
        # 임시 스탠딩 일러: 정면 도트 한 칸 그대로 (게임에서 크게 키워서 보여준다)
        frame(who, "down", 1).save(STANDING_OUT / f"{who}.png")

    scale = 6
    # 정면 / 옆 / 뒤 미리보기
    prev = background(W * 3 * 3 + 16, H + 4)
    for i, who in enumerate(CHARS):
        for j, d in enumerate(("down", "left", "up")):
            prev.alpha_composite(frame(who, d, 1), (i * (W * 3 + 8) + j * W, 0))
    prev.resize((prev.width * scale, prev.height * scale), Image.NEAREST).save(OUT / "preview" / "preview.png")

    # 걷기 애니메이션 GIF
    frames = []
    for col in (0, 1, 2, 1):
        f = background(W * 6 + 8, H * 2 + 4)
        for i, who in enumerate(CHARS):
            f.alpha_composite(frame(who, "down", col), (i * W, 0))
            f.alpha_composite(frame(who, "left", col), (W * 3 + 8 + i * W, 0))
            f.alpha_composite(frame(who, "up", col), (i * W, H + 4))
            f.alpha_composite(frame(who, "right", col), (W * 3 + 8 + i * W, H + 4))
        frames.append(f.resize((f.width * scale, f.height * scale), Image.NEAREST).convert("RGB"))
    frames[0].save(OUT / "preview" / "walk.gif", save_all=True, append_images=frames[1:], duration=180, loop=0)


if __name__ == "__main__":
    main()
