"""Original, small-scale artwork based on the characters' cutie marks."""

import math

from PIL import Image, ImageDraw


class Mark:
    def __init__(self):
        self.image = Image.new("RGBA", (400, 400))
        self.draw = ImageDraw.Draw(self.image)
        self.origin = (0, 0)
        self.scale = 1

    def point(self, x, y):
        return tuple(round(4 * (offset + self.scale * value))
                     for offset, value in zip(self.origin, (x, y)))

    def ellipse(self, x, y, xr, yr, color, outline=None, width=2):
        self.draw.ellipse((self.point(x - xr, y - yr), self.point(x + xr, y + yr)),
                          fill=color, outline=outline, width=max(1, round(4 * width * self.scale)))

    def line(self, points, color, width=3):
        self.draw.line([self.point(*p) for p in points], fill=color,
                       width=max(1, round(4 * width * self.scale)), joint="curve")

    def poly(self, points, color, outline=None):
        self.draw.polygon([self.point(*p) for p in points], fill=color, outline=outline)

    def star(self, x, y, radius, color, count=5, inner=.48):
        self.poly([(x + math.sin(a) * r, y - math.cos(a) * r)
                   for i in range(count * 2)
                   for a, r in [(math.pi * i / count, radius * (inner if i % 2 else 1))]], color)

    def stamp(self, painter, x, y, scale, *args):
        old_origin, old_scale = self.origin, self.scale
        self.origin = (old_origin[0] + x * old_scale, old_origin[1] + y * old_scale)
        self.scale *= scale
        painter(self, *args)
        self.origin, self.scale = old_origin, old_scale


def heart(m, color):
    m.ellipse(34, 39, 19, 18, color)
    m.ellipse(66, 39, 19, 18, color)
    m.poly([(15, 43), (50, 80), (85, 43)], color)


def apple(m, color, sliced=False):
    m.line([(49, 38), (48, 20), (58, 16)], "#875236", 6)
    m.ellipse(62, 22, 11, 6, "#83cf61")
    m.ellipse(36, 56, 23, 23, color)
    m.ellipse(63, 56, 23, 23, color)
    m.ellipse(50, 66, 32, 21, color)
    if sliced:
        m.ellipse(49, 59, 26, 22, "#f9f5c6")
        m.ellipse(43, 58, 3, 7, "#6a3f31")
        m.ellipse(55, 58, 3, 7, "#6a3f31")
    else:
        m.ellipse(30, 49, 4, 8, "#ffe1ab")


def diamond(m, color, shine):
    m.poly([(50, 9), (76, 48), (50, 91), (24, 48)], color)
    m.poly([(50, 9), (50, 48), (24, 48)], shine)
    m.poly([(50, 48), (76, 48), (50, 91)], "#4690c9")
    m.line([(24, 48), (76, 48)], shine, 2)


def butterfly(m):
    m.line([(44, 44), (36, 27), (28, 24)], "#f9d7e8", 3)
    m.line([(55, 44), (63, 28), (71, 25)], "#f9d7e8", 3)
    m.ellipse(32, 48, 20, 13, "#ff91c7")
    m.ellipse(68, 48, 20, 13, "#ff91c7")
    m.ellipse(37, 64, 13, 12, "#e95398")
    m.ellipse(63, 64, 13, 12, "#e95398")
    m.ellipse(50, 55, 5, 18, "#76d6ef")


def balloon(m, color):
    m.line([(50, 65), (47, 74), (54, 85), (48, 98)], "#faf0dd", 3)
    m.poly([(50, 60), (44, 69), (56, 69)], color)
    m.ellipse(50, 39, 21, 26, color)
    m.ellipse(42, 31, 4, 8, "#fff3ef")


def sun(m, a, b):
    m.star(50, 50, 45, b, 8, .59)
    m.ellipse(50, 50, 24, 24, a, "#fff3b7", 2)


def moon(m, color):
    m.poly([(72, 10), (57, 10), (41, 16), (29, 27), (21, 41),
            (18, 57), (22, 71), (31, 83), (45, 91), (62, 94), (77, 91),
            (88, 83), (92, 75), (77, 78), (64, 74), (55, 67), (48, 56),
            (46, 44), (49, 32), (57, 20)], color)


def note(m, color):
    m.ellipse(34, 73, 14, 10, color)
    m.line([(46, 73), (46, 24), (71, 43), (75, 54)], color, 7)


def flower(m, color):
    for i in range(5):
        angle = i * math.tau / 5
        m.ellipse(50 + 25 * math.sin(angle), 50 + 25 * math.cos(angle), 15, 15, color)
    m.ellipse(50, 50, 17, 17, "#fff2cf")
    m.ellipse(44, 47, 2, 3, "#a95556")
    m.ellipse(56, 47, 2, 3, "#a95556")
    m.line([(43, 55), (47, 59), (53, 59), (57, 55)], "#a95556", 3)


def candy(m, color):
    m.poly([(34, 50), (8, 34), (10, 65)], color)
    m.poly([(66, 50), (92, 34), (90, 65)], color)
    m.ellipse(50, 50, 22, 18, color, "#fff0df", 4)
    m.line([(44, 37), (57, 61)], "#fff0df", 5)


def spiral(m, cx, cy, radius, turns, color, width=3, end=0):
    m.line([(cx + math.cos(a + end) * r, cy + math.sin(a + end) * r)
            for i in range(81)
            for a, r in [(math.tau * turns * i / 80, radius * i / 80)]], color, width)


def shield(m, color, border):
    outline = [(9, 14), (29, 18), (50, 7), (71, 18), (91, 14),
               (87, 61), (76, 81), (50, 95), (24, 81), (13, 61)]
    m.poly(outline, border)
    m.poly([(50 + (x - 50) * .85, 50 + (y - 50) * .85) for x, y in outline], color)


def draw_mark(kind):
    m = Mark()
    if kind == "twilight":
        for x, y in ((22, 25), (77, 22), (87, 59), (56, 88), (14, 68)):
            m.star(x, y, 11, "#fff5ff", 6)
        m.star(50, 50, 34, "#fff5ff", 6, .59)
        m.star(50, 50, 28, "#f05bb4", 6, .50)
    elif kind == "apples":
        for x, y in ((5, 0), (50, 3), (26, 45)):
            m.stamp(apple, x, y, .48, "#f45253")
    elif kind == "rainbow":
        for x, color in ((0, "#2caef0"), (-9, "#ffdf45"), (-18, "#ef4554")):
            m.poly([(69+x, 39), (55+x, 61), (69+x, 64), (35+x, 96),
                    (48+x, 71), (34+x, 68), (51+x, 39)], color)
        for x, y, r in ((33, 39, 15), (48, 28, 20), (68, 29, 16), (81, 40, 12)):
            m.ellipse(x, y, r, r * .82, "#f7fcff")
    elif kind == "diamonds":
        for x, y in ((1, 8), (51, 2), (27, 43)):
            m.stamp(diamond, x, y, .48, "#72caf3", "#e8fbff")
    elif kind == "butterflies":
        for x, y in ((1, 3), (50, 5), (26, 43)):
            m.stamp(butterfly, x, y, .47)
    elif kind == "balloons":
        for x, y, c in ((2, 26, "#55bbfa"), (25, -1, "#ffe957"), (52, 23, "#55bbfa")):
            m.stamp(balloon, x, y, .49, c)
    elif kind == "spike":
        m.poly([(48, 96), (30, 89), (17, 74), (15, 53), (25, 33), (28, 50),
                (39, 27), (55, 9), (54, 29), (69, 47), (77, 30), (86, 57),
                (83, 75), (70, 90)], "#75d658")
        m.poly([(46, 92), (31, 81), (31, 62), (45, 45), (52, 29), (59, 47),
                (71, 55), (75, 70), (65, 86)], "#b8ff89")
        m.stamp(diamond, 21, 35, .62, "#b583f3", "#eedaff")
    elif kind == "celestia":
        sun(m, "#ffdd57", "#ffc061")
    elif kind == "luna":
        m.ellipse(48, 61, 43, 30, "#251d54", "#7575ba")
        m.stamp(moon, 10, 1, .82, "#ecedff")
    elif kind == "cadance":
        m.stamp(heart, 4, -1, .93, "#85dcff")
        m.poly([(20, 37), (50, 53), (50, 72), (35, 57)], "#d7f8ff")
        m.poly([(80, 37), (50, 53), (50, 72)], "#4d96dc")
        m.line([(36, 72), (25, 82), (33, 90), (45, 82)], "#ffdf87", 5)
        m.line([(64, 72), (75, 82), (67, 90), (55, 82)], "#ffdf87", 5)
    elif kind == "armor":
        m.stamp(shield, 13, 27, .74, "#517ad7", "#ebf4ff")
        m.star(50, 63, 21, "#ef75c5", 6)
        for x, y in ((25, 23), (50, 13), (75, 23)):
            m.star(x, y, 9, "#c2e1ff", 5)
    elif kind == "starlight":
        for offset, color in ((-6, "#cfd2ff"), (2, "#71ead9")):
            m.line([(13, 89+offset), (37, 79+offset), (46, 62+offset),
                    (65, 57+offset), (87, 42+offset)], color, 5)
        m.star(62, 43, 31, "#e694f8", 4, .35)
        m.star(62, 43, 18, "#f7c8ff", 4, .34)
    elif kind == "sunset":
        m.star(50, 50, 46, "#ffd142", 12, .69)
        m.ellipse(50, 50, 29, 29, "#ec5142")
        m.poly([(25, 36), (36, 29), (47, 31), (57, 42), (58, 55),
                (65, 63), (77, 60), (71, 70), (62, 76), (50, 79),
                (37, 76), (27, 68), (22, 56), (21, 47)], "#ffe263")
    elif kind == "trixie":
        m.stamp(moon, 3, 0, .91, "#a6d2ff")
        m.line([(30, 83), (75, 32)], "#6ea9ec", 12)
        m.line([(30, 81), (74, 31)], "#e4edff", 4)
        m.star(76, 29, 17, "#c6c6ff", 6)
        m.star(88, 54, 8, "#e9edff", 4)
    elif kind in ("apple-bloom", "scootaloo", "sweetie-belle"):
        shield(m, "#a65ec0", "#ef6583")
        m.poly([(19, 27), (50, 20), (81, 27), (77, 69), (50, 83), (23, 69)], "#647cd5")
        if kind == "apple-bloom":
            m.stamp(apple, 21, 22, .58, "#ef839d")
            m.stamp(heart, 36, 42, .28, "#fff1e3")
        elif kind == "scootaloo":
            m.poly([(24, 61), (37, 48), (65, 34), (78, 31), (71, 44),
                    (76, 44), (65, 56), (70, 55), (58, 67), (41, 72)], "#f0b7eb")
            m.poly([(45, 48), (65, 43), (55, 53), (63, 53),
                    (42, 66), (48, 55), (39, 57)], "#d15483")
        else:
            m.star(50, 52, 26, "#f0b7eb", 5)
            m.stamp(note, 28, 29, .48, "#b04286")
    elif kind == "apple-half":
        apple(m, "#8bc64c", True)
    elif kind == "pie":
        m.poly([(13, 52), (87, 52), (77, 79), (24, 79)], "#c87840")
        m.ellipse(50, 50, 38, 15, "#ffcf82", "#a95636", 3)
        for offset in (-16, 0, 16):
            m.line([(38+offset, 44), (57+offset, 57)], "#ad6038", 3)
            m.line([(43+offset, 57), (61+offset, 44)], "#ad6038", 3)
    elif kind == "flowers":
        for x, y, c in ((4, 3, "#f68ebd"), (52, 6, "#ed89cf"), (27, 43, "#ffaad1")):
            m.stamp(flower, x, y, .46, c)
    elif kind == "rock":
        m.poly([(27, 26), (69, 22), (90, 43), (49, 89), (10, 47)], "#8e909c", "#f0e8fb")
        m.poly([(27, 26), (69, 22), (90, 43), (59, 51), (32, 50), (10, 47)], "#c2c0cf")
        m.poly([(32, 50), (59, 51), (49, 89)], "#a5a6b5")
        m.poly([(59, 51), (90, 43), (49, 89)], "#656778")
        m.line([(10, 47), (32, 50), (59, 51), (90, 43)], "#dfd6e7", 2)
    elif kind == "spiral":
        for i in range(8):
            a = i * math.tau / 8
            m.line([(50 + math.sin(a + bend) * r, 50 + math.cos(a + bend) * r)
                    for bend, r in ((0, 29), (.13, 37), (.28, 45))], "#e8c88a", 4)
        spiral(m, 50, 50, 27, 1.7, "#e8c88a", 5)
    elif kind == "quaver":
        for x in (28, 62):
            m.ellipse(x, 69, 16, 11, "#182640", "#bfeeff", 3)
            m.line([(x+13, 69), (x+13, 27)], "#c0efff", 11)
            m.line([(x+13, 69), (x+13, 27)], "#182640", 6)
        m.poly([(37, 25), (80, 17), (80, 34), (37, 43)], "#bfeeff")
        m.poly([(41, 28), (76, 21), (76, 31), (41, 38)], "#182640")
    elif kind == "clef":
        points = [(55, 88), (65, 93), (72, 86), (69, 71), (55, 28),
                  (54, 14), (60, 6), (67, 14), (65, 27), (52, 43), (36, 55),
                  (30, 66), (35, 77), (50, 82), (66, 78), (74, 68), (71, 57),
                  (62, 52), (50, 53), (44, 63), (50, 71)]
        m.line(points, "#edb4e8", 6)
        m.ellipse(55, 89, 6, 5, "#edb4e8")
    elif kind == "bubbles":
        for x, y, r in ((24, 20, 10), (55, 18, 12), (78, 35, 10),
                        (35, 45, 13), (17, 61, 8), (67, 63, 13), (45, 81, 9)):
            m.ellipse(x, y, r, r, "#6fc6e2", "#e6fbff", 3)
            m.ellipse(x-r*.29, y-r*.32, r*.25, r*.22, "#f7feff")
    elif kind == "lyre":
        m.line([(49, 83), (31, 70), (21, 54), (22, 32), (15, 19), (29, 13),
                (37, 23), (32, 35), (68, 35), (63, 23), (71, 13), (85, 19),
                (78, 32), (79, 54), (69, 70), (49, 83)], "#ffdc70", 7)
        for x in (39, 46, 53, 60):
            m.line([(x, 35), (x, 72)], "#fff6c2", 3)
        m.line([(29, 88), (71, 88)], "#f2ae50", 6)
    elif kind == "bonbons":
        for x, y, c in ((5, 4, "#ed81ad"), (51, 14, "#7ecdee"), (28, 47, "#e796b8")):
            m.stamp(candy, x, y, .47, c)
    elif kind == "hourglass":
        m.poly([(26, 19), (74, 19), (66, 38), (55, 50), (67, 62), (74, 81),
                (26, 81), (33, 62), (45, 50), (33, 38)], "#f9e3a3", "#deb06d")
        m.poly([(34, 27), (66, 27), (58, 39), (50, 46), (42, 39)], "#cd9143")
        m.poly([(33, 76), (50, 60), (67, 76)], "#ca8940")
        for y in (17, 85):
            m.line([(23, y), (77, y)], "#ffd889", 7)
    elif kind == "compass":
        m.ellipse(50, 50, 35, 35, "#785c39", "#ffdfa0", 3)
        m.star(50, 50, 46, "#f6d390", 4, .24)
        m.poly([(50, 4), (61, 49), (50, 50), (39, 51)], "#d27648")
        m.ellipse(50, 50, 5, 5, "#fff0bc")
    elif kind == "spitfire":
        m.poly([(12, 87), (29, 70), (45, 62), (28, 58), (13, 45), (9, 20),
                (24, 39), (38, 42), (50, 53), (53, 32), (68, 14), (86, 9),
                (74, 26), (91, 22), (80, 39), (68, 49), (78, 52), (90, 49),
                (78, 65), (62, 67), (46, 84), (27, 92), (35, 80)], "#fd7b43")
        m.poly([(25, 84), (48, 66), (54, 56), (63, 32), (73, 23),
                (69, 41), (79, 34), (66, 53), (79, 56), (65, 62), (51, 74)], "#ffe073")
    elif kind == "sunburst":
        m.stamp(sun, 23, 20, .65, "#ffea78", "#ff9e58")
        for x, y in ((15, 41), (22, 20), (45, 13), (68, 15), (87, 25), (91, 45)):
            m.star(x, y, 7, "#bde7ff", 4, .35)
    elif kind == "coco":
        m.ellipse(48, 73, 37, 14, "#8d709e", "#ebdcf5", 2)
        m.poly([(29, 68), (32, 43), (61, 41), (67, 69)], "#ad8fbb")
        m.line([(31, 62), (65, 61)], "#f5d99b", 7)
        m.poly([(56, 55), (64, 26), (79, 11), (93, 8), (85, 27), (70, 37)], "#f394a6")
        m.line([(56, 55), (82, 17)], "#ffe2d9", 2)
    elif kind == "tiara":
        points = [(13, 38), (33, 60), (49, 25), (65, 60), (87, 38),
                  (78, 76), (67, 82), (33, 82), (22, 76)]
        m.poly(points, "#d9d8ec")
        m.line([*points, points[0]], "#fff4f7", 4)
        m.stamp(diamond, 34, 37, .31, "#f58ed4", "#fff0ff")
        for x, y in ((13, 37), (49, 26), (87, 37)):
            m.ellipse(x, y, 4, 4, "#f99bdb")
    elif kind == "spoon":
        m.ellipse(37, 31, 18, 23, "#cbcce0", "#fff5ff", 3)
        m.ellipse(34, 26, 8, 13, "#e5e7f3")
        m.line([(43, 49), (67, 78)], "#d8d1e6", 10)
        m.stamp(heart, 53, 61, .39, "#e5d9f8")
    elif kind == "cupcake":
        m.poly([(20, 55), (80, 55), (73, 84), (27, 84)], "#dfaa71")
        for x in (32, 43, 54, 65):
            m.line([(x, 61), (x+2, 81)], "#f6d395", 3)
        for x, y, r in ((32, 49, 17), (65, 49, 19), (50, 33, 19)):
            m.ellipse(x, y, r, r*.75, "#f8a3d2")
        m.ellipse(51, 21, 6, 6, "#e8679c")
    else:
        raise ValueError(f"Unknown cutie mark {kind}")
    return m.image
