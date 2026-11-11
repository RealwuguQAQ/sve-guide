"""生成《基本玩法》页面用的示意图（PNG，2 倍分辨率）。

输出到 docs/public/images/basics/：
  playmat.png    对战场地九区示意
  turn-flow.png  回合三阶段流程
  evolve.png     进化流程
  attack.png     攻击目标规则（横置 / 竖置）
  card-parts.png 卡面部位说明

用法：python tools/make-basics-images.py
"""

import os
from PIL import Image, ImageDraw, ImageFont

S = 2                      # 超采样倍数
OUT = os.path.join("docs", "public", "images", "basics")

INK = "#1f1f1f"
MUTED = "#6b7280"
LINE = "#c9d1db"
PANEL = "#f3f6fa"
BRAND = "#245b9e"
BRAND_SOFT = "#e8f0fa"
OK = "#1f7a4d"
NO = "#c0392b"
GOLD = "#b8860b"

FONT_BODY = r"C:\Windows\Fonts\msyh.ttc"
FONT_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"


class Canvas:
    def __init__(self, w, h, bg="white"):
        self.w, self.h = w, h
        self.img = Image.new("RGB", (w * S, h * S), bg)
        self.d = ImageDraw.Draw(self.img)

    def font(self, size, bold=False):
        return ImageFont.truetype(FONT_BOLD if bold else FONT_BODY, int(size * S))

    def text(self, x, y, s, size=14, bold=False, fill=INK, anchor="la"):
        self.d.text((x * S, y * S), s, font=self.font(size, bold), fill=fill, anchor=anchor)

    def box(self, x1, y1, x2, y2, r=8, fill=None, outline=LINE, width=1):
        self.d.rounded_rectangle(
            [x1 * S, y1 * S, x2 * S, y2 * S],
            radius=r * S, fill=fill, outline=outline, width=int(width * S),
        )

    def line(self, x1, y1, x2, y2, fill=LINE, width=1):
        self.d.line([x1 * S, y1 * S, x2 * S, y2 * S], fill=fill, width=int(width * S))

    def arrow(self, x1, y1, x2, y2, fill=BRAND, width=2, head=8):
        import math
        self.line(x1, y1, x2, y2, fill=fill, width=width)
        ang = math.atan2(y2 - y1, x2 - x1)
        for sign in (+1, -1):
            a = ang + sign * math.radians(26)
            self.line(x2, y2, x2 - head * math.cos(a), y2 - head * math.sin(a), fill=fill, width=width)

    def badge(self, cx, cy, n, r=11, fill=BRAND):
        self.d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=fill)
        self.text(cx, cy - 1, str(n), 12, True, "#ffffff", "mm")

    def check(self, cx, cy, size=7, fill=OK, width=2.6):
        self.line(cx - size, cy, cx - size * 0.25, cy + size * 0.7, fill=fill, width=width)
        self.line(cx - size * 0.25, cy + size * 0.7, cx + size, cy - size * 0.8, fill=fill, width=width)

    def cross(self, cx, cy, size=7, fill=NO, width=2.6):
        self.line(cx - size, cy - size, cx + size, cy + size, fill=fill, width=width)
        self.line(cx - size, cy + size, cx + size, cy - size, fill=fill, width=width)

    def save(self, name):
        os.makedirs(OUT, exist_ok=True)
        self.img.save(os.path.join(OUT, name), optimize=True)
        print("written", os.path.join(OUT, name), self.img.size)


def rounded_label(c, x, y, w, h, title, sub=None, fill=PANEL, outline=LINE,
                  title_size=15, sub_size=11.5, title_fill=INK):
    c.box(x, y, x + w, y + h, fill=fill, outline=outline)
    if sub:
        c.text(x + w / 2, y + h / 2 - 10, title, title_size, True, title_fill, "mm")
        c.text(x + w / 2, y + h / 2 + 12, sub, sub_size, False, MUTED, "mm")
    else:
        c.text(x + w / 2, y + h / 2, title, title_size, True, title_fill, "mm")


def mini_card(c, x, y, w, h, label="", landscape=False, fill="#ffffff", edge=BRAND):
    c.box(x, y, x + w, y + h, r=6, fill=fill, outline=edge, width=1.2)
    if landscape:
        c.line(x + 8, y + h * 0.72, x + w * 0.72, y + h * 0.72, fill="#e3e8ef", width=3)
        c.line(x + w * 0.14, y + 10, x + w * 0.14, y + h - 10, fill="#e3e8ef", width=3)
    else:
        c.box(x + 6, y + 6, x + w - 6, y + h * 0.5, r=3, fill="#eef2f7", outline=None)
        c.line(x + 10, y + h * 0.64, x + w - 10, y + h * 0.64, fill="#e3e8ef", width=2)
        c.line(x + 10, y + h * 0.72, x + w * 0.62, y + h * 0.72, fill="#e3e8ef", width=2)
    if label:
        c.text(x + w / 2, y + h - 8, label, 10.5, False, MUTED, "ms")


# ---------------------------------------------------------------- 场地
def playmat():
    c = Canvas(980, 600)
    c.text(24, 18, "对战场地（以自己一侧为例）", 18, True)

    rounded_label(c, 24, 64, 150, 92, "主战者", "放主战者卡")
    rounded_label(c, 24, 170, 150, 92, "牌组", "面朝下")
    rounded_label(c, 24, 276, 150, 92, "进化牌组", "面朝下")

    c.text(196, 64, "战场（最多 5 张）", 14, True, BRAND)
    for i in range(5):
        rounded_label(c, 196 + i * 84, 88, 76, 118, str(i + 1), None, fill="#fbfcfe")
    c.text(196, 214, "随从与护符都放在这里", 11.5, False, MUTED)

    c.text(196, 246, "额外区（最多 5 张，相当于第二手牌）", 14, True, BRAND)
    for i in range(5):
        rounded_label(c, 196 + i * 84, 270, 76, 96, str(i + 1), None, fill="#f7faf7")
    c.text(196, 374, "放在这里的卡可以像手牌一样直接使用", 11.5, False, MUTED)

    rounded_label(c, 620, 64, 130, 88, "墓场", "被破坏/用掉")
    rounded_label(c, 620, 166, 130, 88, "消失", "除外区")
    rounded_label(c, 620, 268, 130, 88, "手牌", "不占场地")

    c.text(24, 424, "能量点（每回合 +1，上限 10）", 14, True, BRAND)
    for i in range(10):
        x = 24 + i * 96
        fill = BRAND_SOFT if i < 4 else PANEL
        c.box(x, 450, x + 86, 500, fill=fill, outline=LINE)
        c.text(x + 43, 475, str(i + 1), 15, True, BRAND if i < 4 else MUTED, "mm")
    c.text(24, 510, "示例：第 4 回合，最大值 4、剩余 4（深色为可用）", 11.5, False, MUTED)
    c.text(24, 552, "提示：随从攻击或支付费用而横置的卡，会在自己回合开始时竖回来。", 12, False, MUTED)
    c.save("playmat.png")


# ---------------------------------------------------------------- 回合流程
def turn_flow():
    c = Canvas(980, 430)
    c.text(24, 16, "一个回合的三个阶段", 18, True)

    cols = [
        (24, 300, "① 开始阶段", [
            "能量点最大值 +1（上限 10）",
            "剩余能量点补满",
            "所有横置的卡转回竖置",
            "抽 1 张（先手第 1 回合不抽）",
        ]),
        (340, 300, "② 主要阶段", [
            "使用卡牌",
            "使用启动能力",
            "随从进行攻击",
            "进化随从（每回合仅 1 次）",
        ]),
        (656, 300, "③ 结束阶段", [
            "处理「结束阶段开始时」能力",
            "可横置自己的【守护】随从",
            "对手可用【快速】卡牌",
            "手牌 8 张以上弃到 7 张",
        ]),
    ]

    for x, w, title, items in cols:
        c.box(x, 58, x + w, 300, fill="#ffffff", outline=LINE)
        c.box(x, 58, x + w, 100, r=8, fill=BRAND_SOFT, outline=BRAND_SOFT)
        c.text(x + w / 2, 79, title, 16, True, BRAND, "mm")
        for i, it in enumerate(items):
            c.text(x + 16, 120 + i * 44, "・" + it, 12.5, False, INK)

    c.arrow(324, 180, 336, 180, BRAND, 2, 7)
    c.arrow(640, 180, 652, 180, BRAND, 2, 7)

    c.text(24, 322, "主要阶段里这四件事可以任意顺序、任意次数进行（进化除外）。", 12, False, MUTED)
    c.text(24, 350, "结束阶段交出回合后轮到对手，对手再跑一遍他自己的三个阶段。", 12, False, MUTED)
    c.text(24, 386, "注：先手玩家第 1 回合不抽牌，这是和手游版最容易被忽略的区别之一。", 12, False, MUTED)
    c.save("turn-flow.png")


# ---------------------------------------------------------------- 进化
def evolve():
    c = Canvas(900, 470)
    c.text(24, 16, "进化：从进化牌组取出同名进化卡叠上去", 18, True)

    c.box(24, 74, 240, 330, fill=PANEL, outline=LINE)
    c.text(132, 92, "进化牌组（≤10 张）", 13, True, BRAND, "mm")
    for i in range(3):
        mini_card(c, 60 + i * 52, 120 + i * 10, 54, 76, fill="#ffffff")
    c.text(132, 268, "面朝下", 11.5, False, MUTED, "mm")
    c.text(132, 292, "只放进化随从", 11.5, False, MUTED, "mm")

    mini_card(c, 420, 150, 86, 120, fill="#ffffff")
    c.text(463, 292, "战场上的随从", 12, False, MUTED, "mm")

    c.arrow(250, 200, 408, 200, BRAND, 2, 8)
    c.text(330, 178, "取同名进化卡", 11.5, False, BRAND, "mm")

    mini_card(c, 660, 150, 86, 120, fill="#fffdf5", edge=GOLD)
    mini_card(c, 670, 140, 86, 120, fill="#ffffff", edge=GOLD)
    c.text(703, 292, "进化后（数值与能力替换）", 12, False, MUTED, "mm")

    c.arrow(516, 200, 648, 200, BRAND, 2, 8)
    c.text(582, 178, "叠放", 11.5, False, BRAND, "mm")

    c.box(24, 344, 876, 448, fill="#fbfcfe", outline=LINE)
    notes = [
        "・支付进化费用（能量点）；1 张进化点卡可以代替其中 1 点能量点，每次进化最多用 1 张。",
        "・只有「能进化」的随从才能进化，且进化牌组里必须有它的进化卡；同名卡主牌组 + 进化牌组合计最多 3 张。",
        "・每回合只能进化 1 次；进化不限制回合数，付得起费第 1 回合就能进化。",
        "・身上的状态指示物（伤害、加成）会保留；进化随从离场时，进化卡正面朝上放回进化牌组顶部。",
    ]
    for i, n in enumerate(notes):
        c.text(36, 356 + i * 23, n, 11.5, False, INK)
    c.save("evolve.png")


# ---------------------------------------------------------------- 攻击规则
def attack():
    c = Canvas(900, 560)
    c.text(24, 16, "能打谁：对手横置（已行动）的随从，或者主战者", 18, True)

    # 自己一侧
    c.box(24, 90, 250, 470, fill="#fffdf5", outline=LINE)
    c.text(38, 98, "自己", 13, True, MUTED)
    mini_card(c, 92, 200, 90, 126, landscape=True, fill="#ffffff", edge=GOLD)
    c.text(137, 350, "发动攻击的随从", 11.5, False, MUTED, "mm")
    c.text(137, 372, "攻击时横置", 11.5, False, MUTED, "mm")

    # 对手一侧
    c.box(300, 90, 876, 496, fill="#fbfcfe", outline=LINE)
    c.text(314, 98, "对手", 13, True, MUTED)

    rows = [
        (140, "主战者", "可以攻击", OK, False),
        (270, "横置的随从", "可以攻击", OK, True),
        (388, "竖置的随从", "打不到", NO, False),
    ]
    for y, name, verdict, color, landscape in rows:
        if landscape:
            mini_card(c, 330, y + 20, 110, 74, landscape=True, fill="#ffffff")
        else:
            mini_card(c, 345, y, 76, 104, fill="#ffffff")
        c.text(470, y + 22, name, 14, True, INK)
        c.text(470, y + 50, verdict, 13, True, color)
        if color == OK:
            c.check(630, y + 58, 7, OK, 2.6)
        else:
            c.cross(630, y + 40, 7, NO, 2.6)

    # 箭头
    c.arrow(190, 236, 330, 192, OK, 2, 8)
    c.arrow(190, 258, 328, 327, OK, 2, 8)
    c.arrow(190, 282, 343, 446, NO, 2, 8)

    c.text(300, 520, "竖置 = 还没行动，相当于半个「潜伏」；想解掉它，得靠法术或能力。", 11.5, False, MUTED)
    c.save("attack.png")


# ---------------------------------------------------------------- 卡面部位
def card_parts():
    c = Canvas(900, 560)
    c.text(24, 16, "卡面怎么看", 18, True)

    x, y, w, h = 170, 80, 220, 330
    c.box(x, y, x + w, y + h, r=10, fill="#ffffff", outline="#8b98a8", width=1.6)
    c.box(x + 12, y + 14, x + w - 12, y + h * 0.44, r=6, fill="#eef3f9", outline=None)
    c.text(x + w / 2, y + h * 0.25, "卡图", 14, False, "#93a2b5", "mm")

    # 费用
    c.d.ellipse([(x - 4) * S, (y - 4) * S, (x + 32) * S, (y + 32) * S], fill=BRAND)
    c.text(x + 14, y + 14, "3", 15, True, "#ffffff", "mm")

    # 名称
    c.box(x + 10, y + h * 0.47, x + w - 10, y + h * 0.545, r=4, fill="#f2f5f9", outline=None)
    c.text(x + 18, y + h * 0.507, "卡牌名称", 12.5, True, INK, "lm")

    # 能力
    c.box(x + 12, y + h * 0.575, x + w - 12, y + h * 0.775, r=4, fill="#fafbfd", outline="#e3e8ef")
    c.text(x + 20, y + h * 0.62, "能力文字", 11.5, False, MUTED)
    c.text(x + 20, y + h * 0.69, "（入场曲 / 启动 / 关键词…）", 10.5, False, MUTED)

    # 攻击力 / 生命值
    c.d.ellipse([(x + w - 76) * S, (y + h - 52) * S, (x + w - 44) * S, (y + h - 20) * S], fill="#fdf1d6", outline=GOLD)
    c.text(x + w - 60, y + h - 36, "③", 13, True, "#7a5b00", "mm")
    c.d.ellipse([(x + w - 38) * S, (y + h - 52) * S, (x + w - 6) * S, (y + h - 20) * S], fill="#fbe3e3", outline=NO)
    c.text(x + w - 22, y + h - 36, "④", 13, True, "#8c2020", "mm")

    # 职业 / 种类 / 类型
    c.text(x + 18, y + h - 36, "⑥ 职业　⑦ 种类　⑧ 类型", 10.5, False, MUTED)

    # 编号徽章
    c.badge(x - 22, y + 14, 1)
    c.badge(x + w + 18, y + h * 0.507, 2)
    c.badge(x + w + 18, y + h * 0.675, 5)

    legend = [
        ("① 费用", "使用这张卡要支付的能量点"),
        ("② 卡牌名称", "同名卡在主牌组里最多 3 张"),
        ("③ 攻击力", "攻击时对敌方造成的伤害"),
        ("④ 生命值", "受到伤害减到 0 或以下即破坏"),
        ("⑤ 能力", "入场曲、启动能力、关键词等"),
        ("⑥ 职业", "精灵 / 皇家护卫 / 巫师 / 龙族 / 梦魇 / 主教"),
        ("⑦ 种类", "随从 / 进化随从 / 法术 / 护符"),
        ("⑧ 类型", "卡牌所属的系列或主题"),
    ]
    c.box(430, 80, 876, 496, fill="#fbfcfe", outline=LINE)
    for i, (k, v) in enumerate(legend):
        yy = 104 + i * 48
        c.text(448, yy, k, 13, True, BRAND)
        c.text(448, yy + 22, v, 11.5, False, MUTED)

    c.text(24, 516, "注：不同卡面的排版略有差异，以卡面实际印制的数值与文字为准。", 11.5, False, MUTED)
    c.save("card-parts.png")


if __name__ == "__main__":
    playmat()
    turn_flow()
    evolve()
    attack()
    card_parts()


