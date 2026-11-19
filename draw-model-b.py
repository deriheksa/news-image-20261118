#!/usr/bin/env python3
"""MODEL B v4 — 'Light Broadsheet' — news-image-20261118 (Wed 18 Nov 2026).
v4 = rebuild following the USER'S REFERENCE IMAGE (IMG_20261120_030320.jpg):
- BIG SCENE illustrations (not small icons): hero art ~92px, grid art 56px.
- Big number label INSIDE each illustration (black pill, bottom-left),
  red number badge top-left inside the art.
- Bolder, bigger headlines (hero 18px, grid 14px).
- SOURCE line under every story (hero + grid).
- NO MAP AT ALL: the "WHERE IT HAPPENED" / "STORIES BY REGION" strip is
  REMOVED entirely (user order). Freed space goes to bigger hero/grid art.
- File size rule relaxed by user: JPEG quality 92-95, target 400-900KB, <1MiB.
Text/numbers unchanged from verified research (37 stories).
"""
import hashlib, sys
from PIL import Image, ImageDraw, ImageFont

FDIR = "/usr/share/fonts/truetype/liberation/"
SERIF_B = FDIR + "LiberationSerif-Bold.ttf"
SERIF   = FDIR + "LiberationSerif-Regular.ttf"
SERIF_I = FDIR + "LiberationSerif-Italic.ttf"
SANS    = FDIR + "LiberationSans-Regular.ttf"
SANS_B  = FDIR + "LiberationSans-Bold.ttf"

# ---- palette (light broadsheet) ----
PAPER   = (247, 242, 231)   # cream
PAPER2  = (242, 235, 218)   # slightly deeper cream
INK     = (26, 26, 26)
RED     = (158, 27, 27)
RED_DK  = (140, 29, 24)
BLUE    = (46, 90, 136)
SLATE   = (34, 56, 79)
GRAY    = (107, 101, 88)
LGRAY   = (150, 142, 126)
RULE    = (201, 191, 168)
SEA     = (214, 231, 240)   # pale blue sea
LAND    = (227, 213, 184)   # cream-tan land
LAND_DK = (206, 188, 152)
GOLD    = (201, 162, 39)
TEAL    = (42, 110, 102)
WHITE   = (255, 255, 255)
NIGHT   = (18, 28, 52)     # dark night sky
SPACE   = (10, 22, 44)     # dark space

MASTHEAD = "Wednesday, 18 November 2026"

# ---------------- data ----------------
# heroes: (num, kicker, headline, body, source)
HEROES = [
    (1, "ASIA \u00b7 APEC SUMMIT",
     "Xi greets Trump on the tarmac as APEC opens",
     "Xi met Trump at Air Force One in Shenzhen. Xi\u2013Putin met Wed; "
     "first Xi\u2013Trump\u2013Putin talks Thu 19 Nov; tariff truce to 10 Jan 2027.",
     "Reuters \u00b7 AFP"),
    (2, "MIDDLE EAST \u00b7 IRAN WAR",
     "Iran hits Bahrain and Kuwait after US strike on Qeshm",
     "Bahrain and Kuwait say defences intercepted Iranian drones. Iran claims "
     "it downed a US MQ-9 \u2014 unverified. Three US carrier groups in the region.",
     "AFP \u00b7 US CENTCOM"),
    (3, "SPACE \u00b7 SCIENCE",
     "Voyager 1 reaches one light-day from Earth",
     "16.1bn miles (25.9bn km) at 5:16:07 a.m. EST \u2014 the first human-made "
     "object this far. A radio signal now takes 24 hours. Launched 5 Sep 1977.",
     "NASA"),
]

# grid: (num, kicker, headline, body, art_key, source)
GRID = [
    (4,  "EUROPE \u00b7 UKRAINE WAR", "Russia fires 141 drones at Ukraine; 126 downed",
     "Overnight strikes hit 7 sites; 4 killed in Odesa, 13 hurt.", "drones", "Reuters \u00b7 AFP"),
    (5,  "EUROPE \u00b7 UKRAINE AID", "EU proposes \u20ac45bn loan to Ukraine for 2027",
     "\u20ac20bn budget, \u20ac25bn military. Repaid only once Russia pays reparations.", "euro", "Reuters"),
    (6,  "AMERICAS \u00b7 MARKETS", "Fed minutes point to more hikes; Dow falls 561",
     "Dow \u22121.11% to 50,198; S&P \u22120.23%, 5th straight loss. Nvidia \u22122.9%; AMD +5.31%.", "chart", "AP"),
    (7,  "ASIA \u00b7 WEATHER", "Cyclone Akvan veers toward Odisha",
     "Winds 90\u2013100 km/h, gusts 110; landfall Fri 20 Nov noon. 47,000+ evacuated.", "cyclone", "IMD"),
    (8,  "EUROPE \u00b7 ECONOMY", "UK inflation climbs to 3.6%, a one-year high",
     "Fuel +33.2% on the year; diesel hits a record 199.5p a litre.", "pump", "ONS"),
    (9,  "AMERICAS \u00b7 US POLITICS", "Jeffries wins Democrats\u2019 nod for Speaker, 251\u201311",
     "House votes 3 Jan; he would be the first Black Speaker.", "ballot", "AP"),
    (10, "AMERICAS \u00b7 BUSINESS", "Anthropic prices IPO at $83; raises $81.3bn",
     "Biggest IPO ever; about $1.5tn valuation. Shares trade Thu as ANT.", "bars", "NPR \u00b7 Al Jazeera"),
    (11, "MIDDLE EAST \u00b7 GAZA", "Israel\u2019s first ground push in central Gaza since ceasefire",
     "Tanks cross near Nuseirat; 3 killed. IDF cites a tunnel threat; Hamas: a violation.", "tank", "AP \u00b7 Al Jazeera"),
    (12, "AMERICAS \u00b7 DEFENCE", "Hegseth\u2019s surprise Caracas trip; US\u2013Venezuela defence pact",
     "Joint training and intel sharing agreed, 10 months after Maduro\u2019s capture.", "flags", "AP"),
    (13, "AFRICA \u00b7 HORN", "Ethiopia and Eritrea mass troops on the border",
     "Monitors report clashes near Badme; Reuters could not confirm them.", "border", "Reuters"),
    (14, "ASIA \u00b7 LABOUR", "Bangladesh wage protests shut about 535 factories",
     "Workers want Tk30,000 a month, up from Tk12,500; about 300 arrested.", "factory", "AFP"),
    (15, "GLOBAL \u00b7 CLIMATE", "COP31 split over fossil-fuel phase-out",
     "Oceans in the draft; 23 nations back a wildfire plan. No US federal delegation.", "globe", "Al Jazeera"),
]

# briefs grouped by region: (region, [(num, text), ...])
BRIEF_COLS = [
    [("ASIA-PACIFIC", [
        (16, "Philippines: Trump claims a \u2018very big\u2019 trade deal; Manila says nothing signed \u2014 only an understanding."),
        (17, "Takaichi meets Putin for ~30 min at APEC \u2014 first Japan\u2013Russia leaders\u2019 contact since Sep 2019."),
        (18, "GTA VI goes on sale at midnight; New Zealand first at 11:00 UTC. About 16m copies pre-sold, over $1.5bn."),
        (19, "Tame Impala sweeps the ARIAs \u2014 7 wins; career total 22, the most in ARIA history."),
        (20, "South Korea: Lee seeks Xi\u2019s help on North Korea at APEC."),
    ]),
     ("AFRICA", [
        (21, "Ebola in DR Congo passes 11,000 cases \u2014 second-largest outbreak on record."),
        (22, "Amnesty: RSF drones killed 37 in El Obeid, Sudan; it urges a war-crimes inquiry."),
    ])],
    [("MIDDLE EAST", [
        (23, "Australia sanctions settler leader Daniella Weiss over West Bank violence."),
        (24, "Iran claims it downed a US MQ-9 drone \u2014 unverified, no US confirmation."),
        (25, "Trump\u2019s Board of Peace faults Israel and Hamas over the Gaza truce."),
        (26, "Gaza: cold threatens displaced in tents; WHO puts 950,000 on flood-prone ground."),
    ]),
     ("EUROPE", [
        (27, "Alcaraz beats Medvedev 6\u20132, 6\u20134 at the ATP Finals in Turin; 11th straight win."),
        (28, "Ukraine hits two oil refineries in Russia\u2019s Krasnodar region."),
        (29, "Poland says it foiled a Russian false-flag plot at the Kaliningrad border."),
        (30, "Geneva: 128 states weigh a ban on killer robots."),
    ])],
    [("AMERICAS", [
        (31, "OpenAI launches GPT-6.2 Astra and Sol; Astra $8/$40 per million tokens."),
        (32, "Google counters with Gemini 4 Neon \u2014 1m-token context."),
        (33, "US officials: no sign of cyberattack behind bank and NSA outages."),
        (34, "Canada: Carney to meet Trump at APEC."),
        (35, "Gold drops 2.1% to $3,770."),
        (36, "AMD jumps 5.3% as chip stocks split."),
        (37, "Microsoft launches seven in-house AI models at Ignite."),
    ])],
]

DATE_CHECK = ("Left out on purpose \u2014 first reported Tue 17 Nov, not today: "
    "Peltola\u2019s Alaska Senate win \u00b7 Nvidia\u2019s $115.8bn quarter \u00b7 Kerch Bridge span falls "
    "\u00b7 Knesset picks Kahana \u00b7 An-12 crash, 19 killed \u00b7 Prague train crash \u00b7 Mongolia "
    "president resigns \u00b7 Serbia Student List sworn in \u00b7 US loses measles-free status \u00b7 "
    "China\u2013Canada tariff cuts.")

FOOTER = ("Every story here happened or was first reported on Wednesday 18 November 2026. "
    "CLAIM = one side\u2019s account, not independently confirmed. "
    "Sources: AP, Reuters, AFP, Al Jazeera, NASA, ONS, IMD, Amnesty. Original drawings.")

STATS = [
    ("$81.3bn", "biggest IPO ever \u2014 Anthropic"),
    ("141 drones", "fired at Ukraine; 126 downed"),
    ("16.1bn miles", "Voyager 1: one light-day"),
    ("\u20ac45bn", "EU loan plan for Ukraine"),
]

# ---------------- helpers ----------------
class Ctx:
    def __init__(self, S):
        self.S = S
        self.W = 1024 * S
        self.H = 1024 * S
        self.img = Image.new("RGB", (self.W, self.H), PAPER)
        self.d = ImageDraw.Draw(self.img)
        self.warn = []
    def f(self, path, size):
        return ImageFont.truetype(path, int(round(size * self.S)))
    def u(self, v):
        return int(round(v * self.S))
    def line(self, x0, y0, x1, y1, fill=INK, w=1):
        self.d.line([(self.u(x0), self.u(y0)), (self.u(x1), self.u(y1))],
                    fill=fill, width=max(1, self.u(w)))
    def rect(self, x0, y0, x1, y1, fill=None, out=None, w=1):
        self.d.rectangle([self.u(x0), self.u(y0), self.u(x1), self.u(y1)],
                         fill=fill, outline=out, width=max(1, self.u(w)))
    def rrect(self, x0, y0, x1, y1, r, fill=None, out=None, w=1):
        self.d.rounded_rectangle([self.u(x0), self.u(y0), self.u(x1), self.u(y1)],
                                 radius=self.u(r), fill=fill, outline=out,
                                 width=max(1, self.u(w)))
    def text(self, x, y, s, font, fill=INK, anchor="la"):
        self.d.text((self.u(x), self.u(y)), s, font=font, fill=fill, anchor=anchor)
    def tlen(self, s, font):
        return self.d.textlength(s, font=font) / self.S
    def wrap(self, s, font, width):
        """Greedy wrap; returns list of lines, all <= width (unless one word too long)."""
        words, lines, cur = s.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if self.tlen(t, font) <= width or not cur:
                cur = t
            else:
                lines.append(cur); cur = w
        if cur:
            lines.append(cur)
        return lines
    def para(self, x, y, s, font, width, leading, max_lines=None, fill=INK):
        lines = self.wrap(s, font, width)
        if max_lines is not None and len(lines) > max_lines:
            self.warn.append(f"OVERFLOW ({len(lines)}>{max_lines}): {s[:60]}...")
            lines = lines[:max_lines]
        for i, ln in enumerate(lines):
            self.text(x, y + i * leading, ln, font, fill=fill)
        return y + len(lines) * leading
    def dashed(self, pts, fill, w=1, dash=5, gap=4):
        import math
        for a, b in zip(pts, pts[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            if L == 0:
                continue
            ux, uy = dx / L, dy / L
            t = 0.0
            while t < L:
                e = min(t + dash, L)
                self.line(a[0] + ux * t, a[1] + uy * t,
                          a[0] + ux * e, a[1] + uy * e, fill=fill, w=w)
                t = e + gap

def art_badge(ctx, x, y, n, size=16):
    """Red rounded square with white number, top-left inside the art."""
    ctx.rrect(x, y, x + size, y + size, 3, fill=RED)
    ctx.text(x + size / 2, y + size / 2 - 0.5, str(n), ctx.f(SANS_B, size - 5),
             fill=WHITE, anchor="mm")

def pill(ctx, x, y, s, font, fg=WHITE, bg=INK, h=15):
    """Pill label; top-left at (x,y). Returns width."""
    w = ctx.tlen(s, font) + 12
    ctx.rrect(x, y, x + w, y + h, 3, fill=bg)
    ctx.text(x + w / 2, y + h / 2 - 0.5, s, font, fill=fg, anchor="mm")
    return w

def pill_r(ctx, x_right, y, s, font, fg=WHITE, bg=INK, h=15):
    """Pill label right-anchored at x_right. Returns width."""
    w = ctx.tlen(s, font) + 12
    ctx.rrect(x_right - w, y, x_right, y + h, 3, fill=bg)
    ctx.text(x_right - w / 2, y + h / 2 - 0.5, s, font, fill=fg, anchor="mm")
    return w

def flag_cn(ctx, x, y, w, h):
    ctx.rect(x, y, x + w, y + h, fill=(178, 30, 30))
    ctx.d.ellipse([ctx.u(x + 2), ctx.u(y + 2), ctx.u(x + 7), ctx.u(y + 7)], fill=GOLD)

def flag_us(ctx, x, y, w, h):
    n = 7
    for j in range(n):
        ctx.rect(x, y + j * h / n, x + w, y + (j + 1) * h / n,
                 fill=(178, 30, 30) if j % 2 == 0 else WHITE)
    ctx.rect(x, y, x + w * 0.4, y + h * 0.55, fill=BLUE)

def flag_ru(ctx, x, y, w, h):
    for j, c in enumerate([(255, 255, 255), (46, 90, 136), (178, 30, 30)]):
        ctx.rect(x, y + j * h / 3, x + w, y + (j + 1) * h / 3, fill=c)

def flag_ua(ctx, x, y, w, h):
    ctx.rect(x, y, x + w, y + h / 2, fill=(0, 87, 184))
    ctx.rect(x, y + h / 2, x + w, y + h, fill=(255, 215, 0))

def flag_eu(ctx, x, y, w, h):
    import math
    ctx.rect(x, y, x + w, y + h, fill=(0, 51, 153))
    for k in range(12):
        a = k * math.pi / 6 - math.pi / 2
        sx, sy = x + w / 2 + (w * 0.32) * math.cos(a), y + h / 2 + (h * 0.32) * math.sin(a)
        ctx.d.ellipse([ctx.u(sx - 1), ctx.u(sy - 1), ctx.u(sx + 1), ctx.u(sy + 1)], fill=GOLD)

def flag_ve(ctx, x, y, w, h):
    for j, c in enumerate([(255, 215, 0), (46, 90, 136), (178, 30, 30)]):
        ctx.rect(x, y + j * h / 3, x + w, y + (j + 1) * h / 3, fill=c)

def person(ctx, x, y, hgt, suit, skin=(210, 180, 150)):
    """Simple standing person: head + suited body. (x,y) = top of head."""
    ctx.d.ellipse([ctx.u(x), ctx.u(y), ctx.u(x + 8), ctx.u(y + 8)], fill=skin)
    ctx.rect(x - 1, y + 8, x + 9, y + hgt, fill=suit)
    ctx.line(x + 4, y + 8, x + 4, y + hgt - 2, fill=WHITE, w=1)


# ---------------- hero illustrations (art 92px tall, w=316) ----------------
def art_hero1(ctx, x, y, w, h):
    """Shenzhen tarmac: big Air Force One, skyline, red carpet, 2 figures
    shaking hands, 3 flags. Caption band at bottom (13px)."""
    bot = y + h - 13          # caption band top
    gy = bot - 17             # tarmac line
    ctx.rect(x, y, x + w, y + h, fill=(238, 226, 198))
    # Shenzhen skyline towers rising from the tarmac line
    for bx, bw, bh in [(4, 16, 26), (24, 12, 34), (40, 18, 22), (62, 14, 38),
                       (80, 20, 28), (262, 14, 44), (280, 18, 30), (300, 12, 36)]:
        ctx.rect(x + bx, gy - bh, x + bx + bw, gy, fill=(196, 182, 150))
    # tall tapered tower
    ctx.d.polygon([(ctx.u(x + 240), ctx.u(gy)), (ctx.u(x + 244), ctx.u(y + 6)),
                   (ctx.u(x + 252), ctx.u(y + 6)), (ctx.u(x + 256), ctx.u(gy))],
                  fill=(180, 164, 130))
    # tarmac
    ctx.rect(x, gy, x + w, bot, fill=(120, 108, 84))
    ctx.line(x, gy, x + w, gy, fill=(90, 80, 60), w=1)
    # Air Force One, BIG: fuselage x+8..x+196, nose right
    fx, fy = x + 8, y + 20
    ctx.rrect(fx, fy, fx + 188, fy + 17, 8, fill=WHITE, out=(90, 90, 90), w=1)
    ctx.rect(fx + 4, fy + 12, fx + 184, fy + 17, fill=BLUE)
    ctx.d.polygon([(ctx.u(fx + 174), ctx.u(fy + 2)), (ctx.u(fx + 190), ctx.u(fy - 13)),
                   (ctx.u(fx + 196), ctx.u(fy - 13)), (ctx.u(fx + 186), ctx.u(fy + 2))], fill=BLUE)
    ctx.d.polygon([(ctx.u(fx + 78), ctx.u(fy + 16)), (ctx.u(fx + 96), ctx.u(fy + 16)),
                   (ctx.u(fx + 114), ctx.u(fy + 28)), (ctx.u(fx + 92), ctx.u(fy + 28))], fill=(150, 150, 150))
    ctx.d.polygon([(ctx.u(fx + 140), ctx.u(fy + 16)), (ctx.u(fx + 154), ctx.u(fy + 16)),
                   (ctx.u(fx + 164), ctx.u(fy + 28)), (ctx.u(fx + 148), ctx.u(fy + 28))], fill=(150, 150, 150))
    for i in range(12):
        ctx.d.ellipse([ctx.u(fx + 16 + i * 13), ctx.u(fy + 4), ctx.u(fx + 22 + i * 13), ctx.u(fy + 9)],
                      fill=SLATE)
    ctx.text(fx + 70, y + 10, "AIR FORCE ONE", ctx.f(SANS_B, 7), fill=SLATE)
    # red carpet LYING FLAT on the tarmac (gy..bot only): narrow at the far
    # end by the figures' feet, wide at the near end by the viewer
    ctx.d.polygon([(ctx.u(x + 128), ctx.u(gy + 2)), (ctx.u(x + 160), ctx.u(gy + 2)),
                   (ctx.u(x + 176), ctx.u(bot)), (ctx.u(x + 112), ctx.u(bot))], fill=RED_DK)
    ctx.line(x + 128, gy + 2, x + 112, bot, fill=GOLD, w=1)
    ctx.line(x + 160, gy + 2, x + 176, bot, fill=GOLD, w=1)
    # two figures standing ON the carpet, feet on the carpet, heads up near
    # the plane (tall, like the reference)
    person(ctx, x + 126, gy - 28, 36, (26, 26, 26))
    person(ctx, x + 148, gy - 28, 36, (46, 56, 80))
    # arms reaching in, hands clasped together at the centre
    ctx.line(x + 135, gy - 10, x + 142, gy - 7, fill=(210, 180, 150), w=3)
    ctx.line(x + 157, gy - 10, x + 150, gy - 7, fill=(210, 180, 150), w=3)
    ctx.d.ellipse([ctx.u(x + 140), ctx.u(gy - 10), ctx.u(x + 152), ctx.u(gy - 1)], fill=(210, 180, 150), outline=(150, 120, 90))
    ctx.line(x + 146, gy - 9, x + 146, gy - 2, fill=(150, 120, 90), w=1)
    # flags: China, US, Russia on poles (bigger)
    for i, fn in enumerate([flag_cn, flag_us, flag_ru]):
        px = x + 206 + i * 38
        ctx.line(px, y + 8, px, gy, fill=INK, w=1)
        fn(ctx, px, y + 8, 30, 16)
    # badge + SHENZHEN pill bottom-right on the tarmac (top-right would
    # cover the Russia flag) + caption band
    art_badge(ctx, x + 6, y + 6, 1, 16)
    sw = ctx.tlen("SHENZHEN", ctx.f(SANS_B, 8)) + 12
    ctx.rrect(x + w - 6 - sw, bot - 17, x + w - 6, bot - 2, 3, fill=INK, out=WHITE, w=1)
    ctx.text(x + w - 6 - sw / 2, bot - 9.5, "SHENZHEN", ctx.f(SANS_B, 8), fill=WHITE, anchor="mm")
    ctx.rect(x, bot, x + w, y + h, fill=INK)
    ctx.text(x + w / 2, bot + 6.5, "SHENZHEN  \u00b7  APEC LEADERS\u2019 WEEK",
             ctx.f(SANS_B, 8), fill=WHITE, anchor="mm")

def art_hero2(ctx, x, y, w, h):
    """Clear Gulf map (92px): Arabia bottom-left, Iran top-right, Gulf channel
    diagonal, Qeshm island, drone arcs, intercept bursts, carrier.
    Labels all isolated. Badge 2 top-left, QESHM pill top-right,
    CLAIM pill bottom-left inside the art."""
    bot = y + h - 13
    ctx.rect(x, y, x + w, y + h, fill=SEA)
    # Arabian Peninsula (bottom-left wedge)
    ctx.d.polygon([(ctx.u(x), ctx.u(bot)), (ctx.u(x), ctx.u(y + 52)),
                   (ctx.u(x + 40), ctx.u(y + 46)), (ctx.u(x + 80), ctx.u(y + 58)),
                   (ctx.u(x + 95), ctx.u(bot))], fill=LAND_DK)
    # Iran (top-right)
    ctx.d.polygon([(ctx.u(x + 200), ctx.u(y)), (ctx.u(x + w), ctx.u(y)),
                   (ctx.u(x + w), ctx.u(y + 30)), (ctx.u(x + 280), ctx.u(y + 36)),
                   (ctx.u(x + 240), ctx.u(y + 42)), (ctx.u(x + 210), ctx.u(y + 32)),
                   (ctx.u(x + 200), ctx.u(y + 14))], fill=LAND_DK)
    # Qatar peninsula
    ctx.d.polygon([(ctx.u(x + 92), ctx.u(y + 66)), (ctx.u(x + 100), ctx.u(y + 54)),
                   (ctx.u(x + 108), ctx.u(y + 66))], fill=LAND)
    # UAE coast (bottom-right strip)
    ctx.d.polygon([(ctx.u(x + 230), ctx.u(bot)), (ctx.u(x + 250), ctx.u(y + 70)),
                   (ctx.u(x + 290), ctx.u(y + 74)), (ctx.u(x + w), ctx.u(bot))], fill=LAND)
    # Qeshm Island (red-marked island in the strait)
    ctx.d.polygon([(ctx.u(x + 218), ctx.u(y + 48)), (ctx.u(x + 238), ctx.u(y + 45)),
                   (ctx.u(x + 246), ctx.u(y + 51)), (ctx.u(x + 230), ctx.u(y + 56))], fill=(200, 120, 100))
    # ---- labels, each isolated ----
    ctx.text(x + 24, y + 10, "PERSIAN GULF", ctx.f(SERIF_I, 7.5), fill=(70, 110, 140))
    ctx.text(x + 10, y + 52, "SAUDI ARABIA", ctx.f(SANS_B, 6.5), fill=(110, 95, 70))
    ctx.text(x + 224, y + 12, "IRAN", ctx.f(SANS_B, 8), fill=(110, 95, 70), anchor="ma")
    ctx.text(x + 232, y + 32, "QESHM", ctx.f(SANS_B, 6.5), fill=RED, anchor="ma")
    ctx.text(x + 232, y + 66, "HORMUZ", ctx.f(SANS_B, 5.5), fill=(70, 110, 140), anchor="ma")
    ctx.text(x + 100, y + 34, "BAHRAIN", ctx.f(SANS_B, 6.5), fill=INK, anchor="ra")
    ctx.text(x + 162, y + 58, "KUWAIT", ctx.f(SANS_B, 6.5), fill=INK, anchor="la")
    # drone arcs (dashed red) from Iran toward Bahrain / Kuwait
    ctx.dashed([(x + 205, y + 36), (x + 165, y + 40), (x + 118, y + 46)], fill=RED, w=1)
    ctx.dashed([(x + 205, y + 36), (x + 180, y + 48), (x + 155, y + 60)], fill=RED, w=1)
    # drone silhouettes on the arcs
    for dx, dy in [(168, 38), (182, 48)]:
        ctx.d.polygon([(ctx.u(x + dx), ctx.u(y + dy + 5)), (ctx.u(x + dx + 14), ctx.u(y + dy)),
                       (ctx.u(x + dx + 14), ctx.u(y + dy + 10))], fill=SLATE)
        ctx.d.ellipse([ctx.u(x + dx + 15), ctx.u(y + dy + 3), ctx.u(x + dx + 18), ctx.u(y + dy + 6)], fill=RED)
    # targets: Bahrain + Kuwait dots with intercept bursts
    for tx, ty in [(110, 46), (150, 64)]:
        tx, ty = x + tx, y + ty
        for k in range(8):
            import math
            a = k * math.pi / 4
            ctx.line(tx + 4 * math.cos(a), ty + 4 * math.sin(a),
                     tx + 9 * math.cos(a), ty + 9 * math.sin(a), fill=GOLD, w=1)
        ctx.d.ellipse([ctx.u(tx - 3), ctx.u(ty - 3), ctx.u(tx + 3), ctx.u(ty + 3)], fill=RED)
    # US carrier in the strait (hull + tower + mast + flag)
    ctx.rrect(x + 278, y + 54, x + 310, y + 62, 2, fill=SLATE)
    ctx.rect(x + 288, y + 46, x + 299, y + 54, fill=SLATE)
    ctx.line(x + 293, y + 40, x + 293, y + 46, fill=SLATE, w=1)
    ctx.rect(x + 293, y + 40, x + 299, y + 43, fill=RED)
    # badge + QESHM pill top-right + CLAIM pill bottom-left
    art_badge(ctx, x + 6, y + 6, 2, 16)
    pill_r(ctx, x + w - 6, y + 6, "QESHM", ctx.f(SANS_B, 8))
    ctx.rrect(x + 6, bot - 19, x + 6 + ctx.tlen("CLAIM \u00b7 UNVERIFIED", ctx.f(SANS_B, 7.5)) + 10,
              bot - 6, 2, fill=WHITE, out=RED, w=1)
    ctx.text(x + 6 + (ctx.tlen("CLAIM \u00b7 UNVERIFIED", ctx.f(SANS_B, 7.5)) + 10) / 2,
             bot - 12.5, "CLAIM \u00b7 UNVERIFIED", ctx.f(SANS_B, 7.5), fill=RED, anchor="mm")
    ctx.rect(x, bot, x + w, y + h, fill=INK)
    ctx.text(x + w / 2, bot + 6.5, "BAHRAIN  \u00b7  KUWAIT  \u00b7  THE GULF",
             ctx.f(SANS_B, 8), fill=WHITE, anchor="mm")

def art_hero3(ctx, x, y, w, h):
    """Voyager 1 on a DARK space background: Earth left, clock '24 h',
    dashed signal line to the big dish, '16.1bn mi' top-right."""
    bot = y + h - 13
    ctx.rect(x, y, x + w, y + h, fill=SPACE)
    import random
    rnd = random.Random(42)
    for _ in range(40):
        sx, sy = rnd.uniform(x + 6, x + w - 6), rnd.uniform(y + 4, bot - 4)
        r = rnd.choice([0.8, 1.2, 1.6])
        ctx.d.ellipse([ctx.u(sx), ctx.u(sy), ctx.u(sx + r), ctx.u(sy + r)],
                      fill=rnd.choice([(255, 255, 255), (200, 210, 230), (160, 175, 200)]))
    # Earth, left
    ex, ey, er = x + 36, y + 52, 18
    ctx.d.ellipse([ctx.u(ex - er), ctx.u(ey - er), ctx.u(ex + er), ctx.u(ey + er)], fill=BLUE)
    ctx.d.ellipse([ctx.u(ex - 10), ctx.u(ey - 9), ctx.u(ex + 1), ctx.u(ey + 0)], fill=(86, 160, 90))
    ctx.d.ellipse([ctx.u(ex - 2), ctx.u(ey + 3), ctx.u(ex + 11), ctx.u(ey + 12)], fill=(86, 160, 90))
    ctx.d.ellipse([ctx.u(ex - 14), ctx.u(ey - 2), ctx.u(ex - 6), ctx.u(ey + 6)], fill=(86, 160, 90))
    ctx.text(ex, ey + er + 2, "EARTH", ctx.f(SANS_B, 6.5), fill=(200, 215, 235), anchor="ma")
    # clock "24 h" (signal travel time) centre-top
    ccx, ccy, cr = x + 150, y + 22, 10
    ctx.d.ellipse([ctx.u(ccx - cr), ctx.u(ccy - cr), ctx.u(ccx + cr), ctx.u(ccy + cr)],
                  outline=(220, 225, 235), width=max(1, ctx.u(1.5)))
    ctx.line(ccx, ccy, ccx, ccy - 6, fill=(220, 225, 235), w=1)
    ctx.line(ccx, ccy, ccx + 5, ccy + 2, fill=(220, 225, 235), w=1)
    ctx.text(ccx, ccy + cr + 2, "24 h", ctx.f(SANS_B, 7.5), fill=(220, 225, 235), anchor="ma")
    # dashed signal path Earth -> Voyager dish
    ctx.dashed([(x + 58, y + 50), (x + 150, y + 44), (x + 224, y + 38)], fill=(150, 165, 190), w=1)
    # Voyager: big parabolic dish at an angle + body + solar wings
    vx, vy = x + 254, y + 38
    ctx.d.ellipse([ctx.u(vx - 30), ctx.u(vy - 17), ctx.u(vx + 30), ctx.u(vy + 1)],
                  fill=(235, 238, 242), outline=SLATE, width=max(1, ctx.u(1)))
    ctx.d.ellipse([ctx.u(vx - 22), ctx.u(vy - 13), ctx.u(vx + 22), ctx.u(vy - 2)],
                  fill=(198, 206, 214), outline=(170, 178, 186))
    ctx.line(vx - 26, vy - 8, vx - 3, vy - 7, fill=SLATE, w=1)
    ctx.line(vx + 26, vy - 8, vx + 3, vy - 7, fill=SLATE, w=1)
    ctx.line(vx, vy - 17, vx, vy - 11, fill=SLATE, w=1)
    ctx.d.ellipse([ctx.u(vx - 3), ctx.u(vy - 11), ctx.u(vx + 3), ctx.u(vy - 4)], fill=GOLD)
    ctx.line(vx, vy + 1, vx, vy + 14, fill=SLATE, w=2)
    ctx.rect(vx - 11, vy + 14, vx + 11, vy + 24, fill=(200, 205, 210), out=SLATE)
    ctx.line(vx + 11, vy + 18, vx + 28, vy + 27, fill=SLATE, w=2)
    ctx.d.ellipse([ctx.u(vx + 25), ctx.u(vy + 24), ctx.u(vx + 31), ctx.u(vy + 30)], fill=GOLD)
    ctx.rect(vx - 36, vy + 14, vx - 13, vy + 22, fill=(30, 60, 110), out=SLATE)
    ctx.rect(vx + 13, vy + 14, vx + 36, vy + 22, fill=(30, 60, 110), out=SLATE)
    for i in range(1, 4):
        ctx.line(vx - 36 + i * 6, vy + 14, vx - 36 + i * 6, vy + 22, fill=(90, 130, 190), w=1)
        ctx.line(vx + 13 + i * 6, vy + 14, vx + 13 + i * 6, vy + 22, fill=(90, 130, 190), w=1)
    ctx.text(vx, vy + 34, "VOYAGER 1", ctx.f(SANS_B, 7), fill=(220, 225, 235), anchor="ma")
    # "16.1bn mi" big top-right (no subtitle — the dish would cover it)
    ctx.text(x + w - 8, y + 6, "16.1bn mi", ctx.f(SERIF_B, 16), fill=WHITE, anchor="ra")
    # badge + caption band
    art_badge(ctx, x + 6, y + 6, 3, 16)
    ctx.rect(x, bot, x + w, y + h, fill=(8, 16, 32))
    ctx.text(x + w / 2, bot + 6.5, "INTERSTELLAR SPACE  \u00b7  NASA",
             ctx.f(SANS_B, 8), fill=WHITE, anchor="mm")

HERO_ART = {1: art_hero1, 2: art_hero2, 3: art_hero3}

# ---------------- grid illustrations (art 56px tall, w=234) ----------------
# Every scene: full-bleed background + real scene + red badge top-left +
# big black pill label bottom-left (the number/word, like the reference).
def art_grid(ctx, key, num, label, x, y, w, h):
    ctx.rect(x, y, x + w, y + h, fill=PAPER2)
    cx = x + 10
    mid = y + h / 2
    if key == "drones":
        # NIGHT scene: dark sky, moon, city skyline with lit windows,
        # quadcopters flying, explosions over the city
        ctx.rect(x, y, x + w, y + h, fill=NIGHT)
        import random
        rnd = random.Random(7)
        for _ in range(18):
            sx, sy = rnd.uniform(x + 6, x + w - 6), rnd.uniform(y + 3, y + 18)
            ctx.d.ellipse([ctx.u(sx), ctx.u(sy), ctx.u(sx + 1.2), ctx.u(sy + 1.2)], fill=(200, 210, 230))
        # moon
        ctx.d.ellipse([ctx.u(x + w - 26), ctx.u(y + 5), ctx.u(x + w - 12), ctx.u(y + 19)], fill=(235, 230, 200))
        ctx.d.ellipse([ctx.u(x + w - 22), ctx.u(y + 9), ctx.u(x + w - 19), ctx.u(y + 12)], fill=(210, 205, 175))
        # city skyline (dark buildings, lit windows)
        bx = x
        for bw, bh in [(26, 22), (18, 30), (30, 18), (22, 26), (28, 20), (20, 32), (34, 24), (26, 18)]:
            ctx.rect(bx, y + h - bh, bx + bw, y + h, fill=(38, 46, 70))
            for wy in range(y + h - bh + 4, y + h - 4, 6):
                for wx in range(int(bx + 3), int(bx + bw - 3), 6):
                    if (wx + wy) % 3 == 0:
                        ctx.rect(wx, wy, wx + 2, wy + 3, fill=(255, 210, 90))
            bx += bw + 2
        # explosions over the city (starbursts + smoke)
        for ex, ey in [(cx + 40, y + 22), (cx + 120, y + 18)]:
            for k in range(8):
                import math
                a = k * math.pi / 4
                ctx.line(ex + 3 * math.cos(a), ey + 3 * math.sin(a),
                         ex + 9 * math.cos(a), ey + 9 * math.sin(a), fill=GOLD, w=2)
            ctx.d.ellipse([ctx.u(ex - 3), ctx.u(ey - 3), ctx.u(ex + 3), ctx.u(ey + 3)], fill=(255, 120, 40))
            ctx.d.ellipse([ctx.u(ex - 9), ctx.u(ey - 10), ctx.u(ex - 2), ctx.u(ey - 4)], fill=(120, 118, 110))
        # quadcopters in the sky
        def quad(qx, qy):
            for rx, ry in [(qx - 4, qy - 3), (qx + 14, qy - 3), (qx - 4, qy + 7), (qx + 14, qy + 7)]:
                ctx.d.ellipse([ctx.u(rx - 4), ctx.u(ry - 1), ctx.u(rx + 4), ctx.u(ry + 1)], fill=(150, 160, 175))
            ctx.rect(qx, qy, qx + 10, qy + 5, fill=(200, 205, 215))
            ctx.d.ellipse([ctx.u(qx + 7), ctx.u(qy + 1), ctx.u(qx + 10), ctx.u(qy + 4)], fill=RED)
        quad(cx + 8, y + 8)
        quad(cx + 70, y + 6)
        quad(cx + 150, y + 10)
    elif key == "euro":
        # EU parliament building + EU flag + Ukraine flag + money bag + coins
        # + blue arrow to a small house (Ukraine)
        ctx.rect(x, y, x + w, y + h, fill=(220, 232, 242))
        # columned building (left)
        ctx.rect(cx, y + 34, cx + 74, y + h, fill=WHITE, out=(180, 175, 160))
        ctx.d.polygon([(ctx.u(cx - 2), ctx.u(y + 34)), (ctx.u(cx + 37), ctx.u(y + 20)),
                       (ctx.u(cx + 76), ctx.u(y + 34))], fill=WHITE, outline=(180, 175, 160))
        for i in range(5):
            ctx.rect(cx + 6 + i * 14, y + 36, cx + 12 + i * 14, y + h - 2, fill=(220, 215, 195))
        # EU flag on pole
        ctx.line(cx + 92, y + 6, cx + 92, y + 30, fill=INK, w=1)
        flag_eu(ctx, cx + 92, y + 6, 34, 20)
        # Ukraine flag on pole
        ctx.line(cx + 150, y + 6, cx + 150, y + 30, fill=INK, w=1)
        flag_ua(ctx, cx + 150, y + 6, 34, 20)
        # money bag with euro sign
        ctx.d.polygon([(ctx.u(cx + 100), ctx.u(y + 34)), (ctx.u(cx + 108), ctx.u(y + 28)),
                       (ctx.u(cx + 116), ctx.u(y + 28)), (ctx.u(cx + 124), ctx.u(y + 34)),
                       (ctx.u(cx + 130), ctx.u(y + 50)), (ctx.u(cx + 94), ctx.u(y + 50))],
                      fill=(170, 140, 90), outline=(120, 95, 55))
        ctx.text(cx + 112, y + 42, "\u20ac", ctx.f(SERIF_B, 13), fill=(90, 65, 20), anchor="mm")
        # gold coins
        for cox, coy in [(132, 43), (140, 45), (136, 39)]:
            ctx.d.ellipse([ctx.u(cx + cox), ctx.u(y + coy), ctx.u(cx + cox + 7), ctx.u(y + coy + 7)],
                          fill=GOLD, outline=(150, 115, 20))
        # blue arrow to the small house (Ukraine)
        ctx.line(cx + 150, y + 44, cx + 178, y + 44, fill=BLUE, w=3)
        ctx.d.polygon([(ctx.u(cx + 178), ctx.u(y + 44)), (ctx.u(cx + 168), ctx.u(y + 39)),
                       (ctx.u(cx + 168), ctx.u(y + 49))], fill=BLUE)
        # small house
        ctx.rect(cx + 186, y + 34, cx + 216, y + h, fill=(235, 220, 185), out=(180, 165, 130))
        ctx.d.polygon([(ctx.u(cx + 182), ctx.u(y + 34)), (ctx.u(cx + 201), ctx.u(y + 24)),
                       (ctx.u(cx + 220), ctx.u(y + 34))], fill=(178, 60, 40))
        ctx.rect(cx + 196, y + 44, cx + 206, y + h, fill=(120, 100, 70))
    elif key == "chart":
        # Fed building (white columns + dome + US flag) + dark screen with
        # steep falling red line + small suited figure watching
        ctx.rect(x, y, x + w, y + h, fill=(240, 234, 220))
        # Fed building
        ctx.rect(cx, y + 30, cx + 78, y + h, fill=WHITE, out=(180, 175, 160))
        ctx.d.pieslice([ctx.u(cx + 24), ctx.u(y + 12), ctx.u(cx + 54), ctx.u(y + 32)],
                       start=180, end=360, fill=WHITE, outline=(180, 175, 160))
        ctx.rect(cx + 37, y + 8, cx + 41, y + 14, fill=(180, 175, 160))
        for i in range(4):
            ctx.rect(cx + 6 + i * 18, y + 32, cx + 12 + i * 18, y + h - 2, fill=(220, 215, 195))
        ctx.line(cx + 39, y + 2, cx + 39, y + 10, fill=INK, w=1)
        flag_us(ctx, cx + 39, y + 2, 16, 10)
        # dark screen with falling line
        ctx.rect(cx + 92, y + 6, cx + 216, y + 46, fill=(20, 30, 50))
        pts = [(cx + 98, y + 12), (cx + 122, y + 15), (cx + 146, y + 14),
               (cx + 172, y + 26), (cx + 198, y + 34), (cx + 210, y + 42)]
        for a, b in zip(pts, pts[1:]):
            ctx.line(a[0], a[1], b[0], b[1], fill=(255, 80, 60), w=2)
        for px, py in pts:
            ctx.d.ellipse([ctx.u(px - 2), ctx.u(py - 2), ctx.u(px + 2), ctx.u(py + 2)], fill=(255, 80, 60))
        ctx.text(cx + 98, y + 38, "DOW", ctx.f(SANS_B, 6.5), fill=(150, 165, 190))
        # suited figure watching the screen
        person(ctx, cx + 196, y + 44, 12, (40, 40, 40))
    elif key == "cyclone":
        # big spiral over the sea + coastline with palm trees, houses, people
        ctx.rect(x, y, x + w, y + 30, fill=(200, 222, 235))
        ctx.rect(x, y + 30, x + w, y + h, fill=(90, 140, 180))
        import math
        for r in (6, 12, 18):
            ctx.d.arc([ctx.u(cx + 26 - r), ctx.u(y + 20 - r), ctx.u(cx + 26 + r), ctx.u(y + 20 + r)],
                      start=30, end=320, fill=TEAL, width=max(1, ctx.u(2)))
        ctx.d.ellipse([ctx.u(cx + 23), ctx.u(y + 17), ctx.u(cx + 29), ctx.u(y + 23)], fill=TEAL)
        # rain dashes under the spiral
        for i in range(4):
            ctx.line(cx + 14 + i * 10, y + 34, cx + 12 + i * 10, y + 40, fill=(220, 230, 245), w=1)
        # coastline (tan wedge, right)
        ctx.d.polygon([(ctx.u(cx + 120), ctx.u(y + 30)), (ctx.u(cx + 150), ctx.u(y + 30)),
                       (ctx.u(cx + 160), ctx.u(y + h)), (ctx.u(cx + 110), ctx.u(y + h))],
                      fill=LAND_DK, outline=(150, 130, 100))
        # palm trees
        for px in (cx + 128, cx + 146):
            ctx.line(px, y + 34, px, y + 22, fill=(110, 85, 50), w=2)
            for a in (200, 250, 290, 330):
                ctx.line(px, y + 22, px + 7 * math.cos(math.radians(a)),
                         y + 22 + 7 * math.sin(math.radians(a)), fill=(40, 120, 70), w=1)
        # small houses + people on the coast
        ctx.rect(cx + 168, y + 38, cx + 188, y + 52, fill=(235, 220, 185), out=(150, 130, 100))
        ctx.d.polygon([(ctx.u(cx + 165), ctx.u(y + 38)), (ctx.u(cx + 178), ctx.u(y + 30)),
                       (ctx.u(cx + 191), ctx.u(y + 38))], fill=(178, 60, 40))
        for px, c in [(cx + 196, RED), (cx + 204, BLUE), (cx + 212, (40, 120, 70))]:
            person(ctx, px, y + 44, 12, c)
        # red dashed arrow from spiral toward the coast
        ctx.dashed([(cx + 50, y + 20), (cx + 80, y + 18), (cx + 108, y + 22)], fill=RED, w=1)
        ctx.d.polygon([(ctx.u(cx + 108), ctx.u(y + 22)), (ctx.u(cx + 99), ctx.u(y + 18)),
                       (ctx.u(cx + 99), ctx.u(y + 26))], fill=RED)
    elif key == "pump":
        # big red gas pump with readable "199.5p" display + big red up arrow
        # + shopping basket + small clock
        ctx.rect(x, y, x + w, y + h, fill=(240, 232, 214))
        # pump
        ctx.rect(cx, y + 4, cx + 46, y + h - 2, fill=WHITE, out=INK, w=1)
        ctx.rect(cx + 5, y + 9, cx + 41, y + 21, fill=INK)
        ctx.text(cx + 23, y + 15, "199.5p", ctx.f(SANS_B, 8), fill=GOLD, anchor="mm")
        ctx.rect(cx + 6, y + 25, cx + 40, y + 33, fill=RED)
        ctx.line(cx + 46, y + 16, cx + 54, y + 16, fill=INK, w=1)
        ctx.line(cx + 54, y + 16, cx + 54, y + 34, fill=INK, w=1)
        ctx.d.ellipse([ctx.u(cx + 51), ctx.u(y + 32), ctx.u(cx + 57), ctx.u(y + 38)], fill=INK)
        # big red up arrow (prices rising)
        ctx.d.polygon([(ctx.u(cx + 62), ctx.u(y + 44)), (ctx.u(cx + 76), ctx.u(y + 16)),
                       (ctx.u(cx + 90), ctx.u(y + 44))], fill=RED)
        ctx.rect(cx + 70, y + 42, cx + 82, y + h - 2, fill=RED)
        # shopping basket with items
        ctx.d.polygon([(ctx.u(cx + 100), ctx.u(y + 34)), (ctx.u(cx + 140), ctx.u(y + 34)),
                       (ctx.u(cx + 134), ctx.u(y + h - 2)), (ctx.u(cx + 106), ctx.u(y + h - 2))],
                      fill=(150, 110, 60))
        ctx.line(cx + 108, y + 34, cx + 114, y + 24, fill=(150, 110, 60), w=1)
        ctx.line(cx + 132, y + 34, cx + 126, y + 24, fill=(150, 110, 60), w=1)
        ctx.d.ellipse([ctx.u(cx + 112), ctx.u(y + 28), ctx.u(cx + 119), ctx.u(y + 35)], fill=(90, 140, 70))
        ctx.d.ellipse([ctx.u(cx + 122), ctx.u(y + 29), ctx.u(cx + 128), ctx.u(y + 35)], fill=(200, 80, 60))
        # small clock (time is running out on prices) + tag
        ctx.d.ellipse([ctx.u(cx + 160), ctx.u(y + 6), ctx.u(cx + 174), ctx.u(y + 20)],
                      outline=INK, width=max(1, ctx.u(1)))
        ctx.line(cx + 167, y + 13, cx + 167, y + 8, fill=INK, w=1)
        ctx.line(cx + 167, y + 13, cx + 171, y + 15, fill=INK, w=1)
        ctx.rrect(cx + 182, y + 8, cx + 222, y + 20, 2, fill=WHITE, out=RED, w=1)
        ctx.text(cx + 202, y + 14, "-33.2%", ctx.f(SANS_B, 7.5), fill=RED, anchor="mm")
    elif key == "ballot":
        # US Capitol dome + columns + blue "251" box + suited figure + ballot box
        ctx.rect(x, y, x + w, y + h, fill=(220, 232, 242))
        # Capitol dome
        ctx.rect(cx + 44, y + 2, cx + 48, y + 10, fill=INK)
        ctx.d.ellipse([ctx.u(cx + 44), ctx.u(y + 0), ctx.u(cx + 48), ctx.u(y + 4)], fill=INK)
        ctx.d.pieslice([ctx.u(cx + 24), ctx.u(y + 10), ctx.u(cx + 68), ctx.u(y + 34)],
                       start=180, end=360, fill=WHITE, outline=INK)
        ctx.rect(cx + 20, y + 30, cx + 72, y + 38, fill=WHITE, out=INK, w=1)
        ctx.rect(cx + 6, y + 38, cx + 86, y + h, fill=WHITE, out=INK, w=1)
        for i in range(6):
            ctx.line(cx + 12 + i * 13, y + 38, cx + 12 + i * 13, y + h - 2, fill=GRAY, w=1)
        # blue "251" box top-right
        ctx.rect(cx + 150, y + 6, cx + 200, y + 22, fill=BLUE)
        ctx.text(cx + 175, y + 14, "251", ctx.f(SANS_B, 11), fill=WHITE, anchor="mm")
        # suited figure on the steps
        person(ctx, cx + 130, y + 30, 24, (30, 30, 50))
        # ballot box with check
        ctx.rect(cx + 168, y + 38, cx + 200, y + h - 2, fill=WHITE, out=INK, w=1)
        ctx.line(cx + 176, y + 34, cx + 192, y + 38, fill=INK, w=1)
        ctx.text(cx + 184, y + 46, "\u2713", ctx.f(SANS_B, 13), fill=BLUE, anchor="mm")
    elif key == "bars":
        # rising bar chart + "ANT $83" dark tag + suited figures + confetti
        ctx.rect(x, y, x + w, y + h, fill=(240, 234, 220))
        for i, bh in enumerate([12, 22, 32, 42]):
            ctx.rect(cx + i * 20, y + h - 4 - bh, cx + i * 20 + 14, y + h - 4,
                     fill=BLUE if i < 3 else GOLD)
        # AI chip on the tallest bar
        ctx.rect(cx + 92, y + 6, cx + 122, y + 36, fill=SLATE, out=INK)
        ctx.rect(cx + 100, y + 14, cx + 114, y + 28, fill=(200, 205, 210))
        ctx.text(cx + 107, y + 21, "AI", ctx.f(SANS_B, 9), fill=SLATE, anchor="mm")
        for px in (cx + 96, cx + 103, cx + 110, cx + 117):
            ctx.line(px, y + 2, px, y + 6, fill=INK, w=1)
            ctx.line(px, y + 36, px, y + 40, fill=INK, w=1)
        # "ANT $83" dark tag top-right
        ctx.rect(cx + 140, y + 6, cx + 216, y + 20, fill=INK)
        ctx.text(cx + 178, y + 13, "ANT   $83", ctx.f(SANS_B, 9), fill=(120, 220, 130), anchor="mm")
        # suited figures (investors) + confetti
        person(ctx, cx + 140, y + 30, 24, (40, 40, 40))
        person(ctx, cx + 168, y + 34, 20, (70, 50, 30))
        import random
        rnd = random.Random(11)
        for _ in range(14):
            sx, sy = rnd.uniform(x + 130, x + w - 6), rnd.uniform(y + 24, y + 40)
            ctx.d.ellipse([ctx.u(sx), ctx.u(sy), ctx.u(sx + 2), ctx.u(sy + 2)],
                          fill=rnd.choice([RED, GOLD, BLUE, TEAL]))
    elif key == "tank":
        # two tanks ON a dark road + smoke + ruined buildings;
        # "BOTH SIDES' CLAIMS" pill top-right (like the reference)
        ctx.rect(x, y, x + w, y + h, fill=(232, 222, 200))
        # ruined buildings (back), sitting on the road
        ctx.rect(cx, y + 12, cx + 34, y + 46, fill=(150, 150, 145))
        ctx.rect(cx + 34, y + 18, cx + 52, y + 46, fill=(120, 150, 110))
        ctx.rect(cx + 190, y + 16, cx + 224, y + 46, fill=(190, 178, 150))
        ctx.rect(cx + 8, y + 20, cx + 14, y + 26, fill=(60, 60, 60))
        ctx.d.polygon([(ctx.u(cx), ctx.u(y + 12)), (ctx.u(cx + 10), ctx.u(y + 6)),
                       (ctx.u(cx + 20), ctx.u(y + 12))], fill=(130, 130, 125))
        # smoke puffs
        for sx, sy in [(cx + 60, y + 6), (cx + 90, y + 4), (cx + 150, y + 8)]:
            ctx.d.ellipse([ctx.u(sx), ctx.u(sy), ctx.u(sx + 14), ctx.u(sy + 10)], fill=(140, 135, 125))
        # dark road at the bottom — the tanks sit ON this
        ctx.rect(x, y + 46, x + w, y + h, fill=(45, 38, 32))
        ctx.line(x, y + 46, x + w, y + 46, fill=(90, 80, 70), w=1)
        # tanks, tracks on the road
        def tank(tx, ty):
            ctx.rrect(tx, ty + 14, tx + 62, ty + 28, 3, fill=(110, 95, 80))
            for i in range(5):
                ctx.d.ellipse([ctx.u(tx + 5 + i * 11), ctx.u(ty + 17), ctx.u(tx + 11 + i * 11), ctx.u(ty + 24)], fill=(60, 55, 50))
            ctx.rect(tx + 10, ty + 6, tx + 46, ty + 14, fill=(130, 115, 95))
            ctx.rect(tx + 20, ty, tx + 36, ty + 6, fill=(110, 95, 80))
            ctx.line(tx + 36, ty + 3, tx + 66, ty + 3, fill=(130, 115, 95), w=3)
        tank(cx + 10, y + 18)
        tank(cx + 120, y + 18)
        # rubble on the road
        ctx.rect(cx + 84, y + 42, cx + 96, y + 46, fill=(150, 140, 120))
        ctx.rect(cx + 100, y + 44, cx + 110, y + 46, fill=(130, 120, 100))
        # "BOTH SIDES' CLAIMS" pill top-right
        tw = ctx.tlen("BOTH SIDES\u2019 CLAIMS", ctx.f(SANS_B, 7)) + 10
        ctx.rrect(x + w - 6 - tw, y + 5, x + w - 6, y + 18, 2, fill=WHITE, out=RED, w=1)
        ctx.text(x + w - 6 - tw / 2, y + 11.5, "BOTH SIDES\u2019 CLAIMS", ctx.f(SANS_B, 7),
                 fill=RED, anchor="mm")
    elif key == "flags":
        # Caracas: mountains + US flag + VE flag + two suited men shaking hands
        ctx.rect(x, y, x + w, y + h, fill=(215, 228, 235))
        # mountains
        ctx.d.polygon([(ctx.u(x), ctx.u(y + h)), (ctx.u(cx + 30), ctx.u(y + 14)),
                       (ctx.u(cx + 70), ctx.u(y + h))], fill=(150, 165, 180))
        ctx.d.polygon([(ctx.u(cx + 50), ctx.u(y + h)), (ctx.u(cx + 110), ctx.u(y + 8)),
                       (ctx.u(cx + 170), ctx.u(y + h))], fill=(130, 148, 165))
        ctx.d.polygon([(ctx.u(cx + 150), ctx.u(y + h)), (ctx.u(cx + 200), ctx.u(y + 18)),
                       (ctx.u(x + w), ctx.u(y + h))], fill=(150, 165, 180))
        # US flag (left pole) + VE flag (right pole)
        ctx.line(cx, y + 6, cx, y + 30, fill=INK, w=1)
        flag_us(ctx, cx, y + 6, 30, 18)
        fx = cx + 190
        ctx.line(fx, y + 6, fx, y + 30, fill=INK, w=1)
        flag_ve(ctx, fx, y + 6, 30, 18)
        # two suited men shaking hands in the middle
        person(ctx, cx + 84, y + 24, 30, (30, 40, 70))
        person(ctx, cx + 128, y + 24, 30, (50, 50, 50))
        # arms reaching in, hands clasped together at the centre
        ctx.line(cx + 93, y + 34, cx + 110, y + 40, fill=(210, 180, 150), w=3)
        ctx.line(cx + 127, y + 34, cx + 110, y + 40, fill=(210, 180, 150), w=3)
        ctx.d.ellipse([ctx.u(cx + 105), ctx.u(y + 36), ctx.u(cx + 115), ctx.u(y + 44)], fill=(210, 180, 150), outline=(150, 120, 90))
        ctx.line(cx + 110, y + 37, cx + 110, y + 43, fill=(150, 120, 90), w=1)
    elif key == "border":
        # desert + mountains + UNCONFIRMED pill + soldiers + jeep + red dashed border
        ctx.rect(x, y, x + w, y + h, fill=(232, 214, 178))
        # far mountains
        ctx.d.polygon([(ctx.u(x), ctx.u(y + h)), (ctx.u(cx + 40), ctx.u(y + 16)),
                       (ctx.u(cx + 90), ctx.u(y + h))], fill=(180, 160, 125))
        ctx.d.polygon([(ctx.u(cx + 150), ctx.u(y + h)), (ctx.u(cx + 200), ctx.u(y + 20)),
                       (ctx.u(x + w), ctx.u(y + h))], fill=(180, 160, 125))
        # "UNCONFIRMED" pill top-center
        tw = ctx.tlen("UNCONFIRMED", ctx.f(SANS_B, 7.5)) + 10
        ctx.rrect(x + w / 2 - tw / 2, y + 5, x + w / 2 + tw / 2, y + 18, 2, fill=WHITE, out=RED, w=1)
        ctx.text(x + w / 2, y + 11.5, "UNCONFIRMED", ctx.f(SANS_B, 7.5), fill=RED, anchor="mm")
        # red dashed border line down the middle + BADME tag
        ctx.dashed([(cx + 112, y + 22), (cx + 112, y + h)], fill=RED, w=2, dash=5, gap=3)
        ctx.rrect(cx + 96, y + 30, cx + 128, y + 41, 2, fill=WHITE, out=RED, w=1)
        ctx.text(cx + 112, y + 35.5, "BADME", ctx.f(SANS_B, 6.5), fill=RED, anchor="mm")
        # soldiers: 3 left (Ethiopia, green) + 3 right (Eritrea, brown)
        for sx, c in [(cx + 20, (60, 100, 60)), (cx + 48, (60, 100, 60)), (cx + 76, (60, 100, 60)),
                      (cx + 140, (120, 90, 60)), (cx + 168, (120, 90, 60)), (cx + 196, (120, 90, 60))]:
            # helmet + head + body + rifle
            ctx.d.pieslice([ctx.u(sx - 4), ctx.u(y + 34), ctx.u(sx + 4), ctx.u(y + 42)],
                           start=180, end=360, fill=(50, 60, 45))
            ctx.d.ellipse([ctx.u(sx - 4), ctx.u(y + 38), ctx.u(sx + 4), ctx.u(y + 46)], fill=(210, 180, 150))
            ctx.rect(sx - 4, y + 46, sx + 4, y + h, fill=c)
            ctx.line(sx + 4, y + 42, sx + 12, y + 34, fill=INK, w=1)
        # jeep (right)
        ctx.rect(cx + 176, y + 40, cx + 216, y + 50, fill=(110, 105, 80))
        ctx.rect(cx + 184, y + 32, cx + 204, y + 40, fill=(90, 85, 65))
        ctx.d.ellipse([ctx.u(cx + 182), ctx.u(y + 48), ctx.u(cx + 190), ctx.u(y + 56)], fill=INK)
        ctx.d.ellipse([ctx.u(cx + 202), ctx.u(y + 48), ctx.u(cx + 210), ctx.u(y + 56)], fill=INK)
    elif key == "factory":
        # garment factory with CLOSED sign + row of workers, one with Tk30,000 placard
        ctx.rect(x, y, x + w, y + h, fill=(228, 226, 218))
        # factory building
        ctx.rect(cx, y + 16, cx + 96, y + h, fill=(150, 140, 120))
        ctx.rect(cx + 78, y + 4, cx + 86, y + 16, fill=(120, 110, 90))
        ctx.rect(cx + 88, y + 8, cx + 96, y + 16, fill=(120, 110, 90))
        for i in range(3):
            ctx.rect(cx + 8 + i * 28, y + 22, cx + 22 + i * 28, y + 30, fill=WHITE)
        # CLOSED sign on the shutter
        ctx.rect(cx + 24, y + 34, cx + 72, y + 46, fill=RED)
        ctx.text(cx + 48, y + 40, "CLOSED", ctx.f(SANS_B, 8), fill=WHITE, anchor="mm")
        # workers row (right), one holding a placard
        for i, wx in enumerate([cx + 116, cx + 138, cx + 160, cx + 182, cx + 204]):
            c = [(90, 100, 70), (120, 90, 60), (70, 90, 120), (110, 70, 70), (80, 110, 80)][i]
            person(ctx, wx, y + 30, 24, c)
        # placard above the middle worker
        ctx.line(cx + 164, y + 14, cx + 164, y + 30, fill=INK, w=1)
        ctx.rect(cx + 146, y + 4, cx + 182, y + 15, fill=WHITE, out=RED, w=1)
        ctx.text(cx + 164, y + 9.5, "Tk30,000", ctx.f(SANS_B, 7), fill=RED, anchor="mm")
    elif key == "globe":
        # COP31 split: clean Earth + sun (left) vs fossil factory + flame (right),
        # divided by a bold vertical crack down the middle
        ctx.rect(x, y, x + w, y + h, fill=(210, 228, 240))
        # Earth (left, big)
        ctx.d.ellipse([ctx.u(cx + 4), ctx.u(y + 8), ctx.u(cx + 72), ctx.u(y + 52)], fill=(150, 190, 220), outline=BLUE)
        ctx.d.ellipse([ctx.u(cx + 14), ctx.u(y + 16), ctx.u(cx + 28), ctx.u(y + 28)], fill=(86, 160, 90))
        ctx.d.ellipse([ctx.u(cx + 34), ctx.u(y + 30), ctx.u(cx + 50), ctx.u(y + 42)], fill=(86, 160, 90))
        # sun above the Earth
        sx, sy = cx + 52, y + 10
        ctx.d.ellipse([ctx.u(sx - 6), ctx.u(sy - 6), ctx.u(sx + 6), ctx.u(sy + 6)], fill=GOLD)
        for k in range(8):
            import math
            a = k * math.pi / 4
            ctx.line(sx + 8 * math.cos(a), sy + 8 * math.sin(a),
                     sx + 11 * math.cos(a), sy + 11 * math.sin(a), fill=GOLD, w=1)
        # factory smokestacks (right) with smoke
        for sx0 in (cx + 150, cx + 172, cx + 194):
            ctx.rect(sx0, y + 22, sx0 + 14, y + h, fill=(120, 118, 110))
            ctx.d.ellipse([ctx.u(sx0 + 1), ctx.u(y + 10), ctx.u(sx0 + 9), ctx.u(y + 18)], fill=(150, 148, 140))
            ctx.d.ellipse([ctx.u(sx0 + 5), ctx.u(y + 4), ctx.u(sx0 + 13), ctx.u(y + 12)], fill=(165, 162, 155))
        # wildfire flame at the base of the stacks
        fx = cx + 120
        ctx.d.polygon([(ctx.u(fx), ctx.u(y + 52)), (ctx.u(fx - 2), ctx.u(y + 38)),
                       (ctx.u(fx + 4), ctx.u(y + 28)), (ctx.u(fx + 6), ctx.u(y + 36)),
                       (ctx.u(fx + 11), ctx.u(y + 16)), (ctx.u(fx + 15), ctx.u(y + 30)),
                       (ctx.u(fx + 22), ctx.u(y + 38)), (ctx.u(fx + 20), ctx.u(y + 52))],
                      fill=(230, 120, 30))
        ctx.d.polygon([(ctx.u(fx + 6), ctx.u(y + 52)), (ctx.u(fx + 7), ctx.u(y + 40)),
                       (ctx.u(fx + 10), ctx.u(y + 30)), (ctx.u(fx + 13), ctx.u(y + 40)),
                       (ctx.u(fx + 14), ctx.u(y + 52))], fill=GOLD)
        ctx.rect(fx - 2, y + 50, fx + 22, y + 54, fill=(90, 70, 50))
        # bold split line down the middle (the COP31 divide)
        ctx.line(cx + 108, y + 4, cx + 108, y + h - 2, fill=INK, w=2)
    # ---- red badge top-left + big black pill bottom-left (inside the art) ----
    art_badge(ctx, x + 5, y + 5, num, 14)
    pill(ctx, x + 6, y + h - 20, label, ctx.f(SANS_B, 9.5))

# ---------------- compact map for stories 1-15 (box below #37) ----------------
def draw_map_box(ctx, x, y, w, h):
    """Compact world map in a small box: pins 1-15 + compass.
    Coordinates are geographically ordered (Americas left, Europe/Africa
    centre, Asia right) so the reader sees WHERE each story happened."""
    ctx.rrect(x, y, x + w, y + h, 4, fill=SEA, out=RULE, w=1)
    ctx.text(x + 8, y + 4, "WHERE STORIES 1\u201315 HAPPENED", ctx.f(SANS_B, 8), fill=RED)
    mx, my = x + 4, y + 14
    mw, mh = w - 8, h - 16
    # continents, scaled to the box (FAT blobs so every pin sits on land)
    blobs = [
        [(0.01, 0.12), (0.14, 0.03), (0.30, 0.05), (0.38, 0.20), (0.34, 0.40), (0.18, 0.46), (0.03, 0.32)],  # N America
        [(0.19, 0.48), (0.30, 0.43), (0.37, 0.56), (0.33, 0.78), (0.23, 0.74), (0.18, 0.58)],               # S America
        [(0.45, 0.08), (0.53, 0.02), (0.58, 0.10), (0.56, 0.26), (0.47, 0.24)],                              # Europe
        [(0.47, 0.28), (0.56, 0.24), (0.61, 0.38), (0.64, 0.55), (0.66, 0.70), (0.58, 0.74), (0.50, 0.60)],  # Africa (+Horn)
        [(0.57, 0.04), (0.74, 0.00), (0.89, 0.06), (0.97, 0.18), (0.91, 0.32), (0.85, 0.34), (0.83, 0.52), (0.79, 0.64), (0.74, 0.56), (0.70, 0.40), (0.63, 0.26)],  # Asia (+India)
        [(0.85, 0.56), (0.93, 0.52), (0.97, 0.62), (0.90, 0.72), (0.85, 0.66)],                              # Oceania
    ]
    for pts in blobs:
        poly = [(ctx.u(mx + fx * mw), ctx.u(my + fy * mh)) for fx, fy in pts]
        ctx.d.polygon(poly, fill=LAND, outline=LAND_DK)
    # pins: (num, fx, fy) — every one verified inside a blob (see check below)
    pins = [(1, 0.84, 0.28), (2, 0.70, 0.36), (4, 0.56, 0.20), (5, 0.51, 0.14),
            (6, 0.26, 0.32), (7, 0.77, 0.55), (8, 0.48, 0.10), (9, 0.23, 0.40),
            (10, 0.15, 0.36), (11, 0.60, 0.44), (12, 0.30, 0.62), (13, 0.63, 0.66),
            (14, 0.78, 0.52), (15, 0.55, 0.20)]
    r = 6
    for n, fx, fy in pins:
        px, py = mx + fx * mw, my + fy * mh
        ctx.d.ellipse([ctx.u(px - r), ctx.u(py - r), ctx.u(px + r), ctx.u(py + r)],
                      fill=RED, outline=WHITE)
        ctx.text(px, py, str(n), ctx.f(SANS_B, 6), fill=WHITE, anchor="mm")
    # Voyager 3: gold star, top-centre (space, not on Earth)
    import math
    sx, sy = mx + 0.70 * mw, my + 0.06 * mh
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        a2 = a + math.pi / 5
        ctx.d.polygon([(ctx.u(sx + 6 * math.cos(a)), ctx.u(sy + 6 * math.sin(a))),
                       (ctx.u(sx + 2.5 * math.cos(a2)), ctx.u(sy + 2.5 * math.sin(a2)))],
                      fill=GOLD, outline=(150, 115, 20))
    ctx.text(sx + 8, sy - 1, "3", ctx.f(SANS_B, 6), fill=INK, anchor="la")
    # compass (top-right corner of the box)
    cx, cy = x + w - 13, y + 13
    ctx.d.ellipse([ctx.u(cx - 7), ctx.u(cy - 7), ctx.u(cx + 7), ctx.u(cy + 7)],
                  fill=WHITE, outline=INK)
    ctx.d.polygon([(ctx.u(cx), ctx.u(cy - 6)), (ctx.u(cx - 2.5), ctx.u(cy + 2)),
                   (ctx.u(cx + 2.5), ctx.u(cy + 2))], fill=RED)
    ctx.text(cx, cy - 10, "N", ctx.f(SANS_B, 7), fill=RED, anchor="ma")

# ---------------- main render ----------------
LABELS = {"drones": "141", "euro": "\u20ac45bn", "chart": "-561",
          "cyclone": "47,000+", "pump": "3.6%", "ballot": "251\u201311",
          "bars": "$81.3bn", "tank": "3 killed", "flags": "CARACAS",
          "border": "BADME", "factory": "535", "globe": "COP31"}

def render(S, path, fmt, quality=92):
    ctx = Ctx(S)
    d = ctx.d
    MX = 28                      # margin
    CW = 1024 - 2 * MX           # 968 content width
    y = 8
    # top strip
    ctx.text(MX, y, "ONE DAY OF WORLD NEWS, ONE PICTURE", ctx.f(SANS_B, 10), fill=RED)
    ctx.text(MX + CW, y, "37 STORIES + DATE CHECK  \u00b7  6 CONTINENTS  \u00b7  EVERY ONE FROM THIS WEDNESDAY",
             ctx.f(SANS_B, 10), fill=INK, anchor="ra")
    y += 14
    ctx.line(MX, y, MX + CW, y, fill=INK, w=2)
    y += 6
    # masthead (auto-fit)
    size = 54
    while size > 30:
        fnt = ctx.f(SERIF_B, size)
        if ctx.tlen(MASTHEAD, fnt) <= CW:
            break
        size -= 1
    ctx.text(MX + CW / 2, y, MASTHEAD, fnt, fill=INK, anchor="ma")
    y += size + 1
    # tagline
    ctx.text(MX + CW / 2, y, "Every story on this page happened, or was first reported, on this Wednesday.",
             ctx.f(SERIF_I, 13), fill=GRAY, anchor="ma")
    y += 15
    ctx.line(MX, y, MX + CW, y, fill=INK, w=1)
    y += 4
    # stats strip
    stat_w = CW / 4
    for i, (big, small) in enumerate(STATS):
        sx = MX + i * stat_w
        if i:
            ctx.line(sx, y + 2, sx, y + 24, fill=RULE, w=1)
        ctx.text(sx + 10, y + 1, big, ctx.f(SERIF_B, 15), fill=RED)
        ctx.text(sx + 10, y + 16, small, ctx.f(SANS_B, 9), fill=INK)
    y += 26
    ctx.line(MX, y, MX + CW, y, fill=INK, w=2)
    y += 6
    # ---- heroes (3 across, art 92px) ----
    hero_w = (CW - 2 * 10) / 3
    hero_h = 202
    hy = y
    for i, (n, kicker, head, body, source) in enumerate(HEROES):
        hx = MX + i * (hero_w + 10)
        art_h = 92
        HERO_ART[n](ctx, hx, hy, hero_w, art_h)
        ty = hy + art_h + 6
        ctx.text(hx, ty + 1, kicker, ctx.f(SANS_B, 9), fill=RED)
        ty += 16
        ty = ctx.para(hx, ty, head, ctx.f(SERIF_B, 18), hero_w, 19.5, max_lines=2)
        ty += 2
        ty = ctx.para(hx, ty, body, ctx.f(SANS, 10.5), hero_w, 12.5, max_lines=3)
        # SOURCE pinned to bottom-left corner of the hero card
        ctx.text(hx, hy + hero_h - 10, f"SOURCE \u00b7 {source}", ctx.f(SANS, 8), fill=GRAY)
        ctx.line(hx, hy + hero_h, hx + hero_w, hy + hero_h, fill=RULE, w=1)
    y = hy + hero_h + 6
    # ---- grid (4 cols x 3 rows, art 56px) ----
    gw = (CW - 3 * 8) / 4
    gh = 135
    for r in range(3):
        for c in range(4):
            n, kicker, head, body, art, source = GRID[r * 4 + c]
            gx = MX + c * (gw + 8)
            gy = y + r * (gh + 6)
            ctx.rrect(gx, gy, gx + gw, gy + gh, 2, fill=WHITE, out=RULE, w=1)
            art_grid(ctx, art, n, LABELS[art], gx + 1, gy + 1, gw - 2, 56)
            ty = gy + 60
            ctx.text(gx + 6, ty + 1, kicker, ctx.f(SANS_B, 7.5), fill=RED)
            ty += 13
            ty = ctx.para(gx + 6, ty, head, ctx.f(SERIF_B, 14), gw - 12, 15, max_lines=2)
            ty += 1
            ty = ctx.para(gx + 6, ty, body, ctx.f(SANS, 9.5), gw - 12, 10.5, max_lines=2)
            # SOURCE pinned to bottom-left corner of the grid card
            ctx.text(gx + 6, gy + gh - 10, f"SOURCE \u00b7 {source}", ctx.f(SANS, 7.5), fill=GRAY)
    y = y + 3 * gh + 2 * 6 + 6
    # ---- briefs (3 cols, grouped by region) — NO MAP STRIP (removed) ----
    ctx.text(MX, y, "ALSO ON WEDNESDAY 18 NOVEMBER", ctx.f(SANS_B, 11), fill=INK)
    ctx.line(MX + 252, y + 6, MX + CW, y + 6, fill=INK, w=1)
    y += 14
    brief_y0 = y
    col_w = (CW - 2 * 14) / 3
    col_bottom = brief_y0
    col_bottoms = []
    for ci, groups in enumerate(BRIEF_COLS):
        bx = MX + ci * (col_w + 14)
        by = brief_y0
        for region, items in groups:
            ctx.text(bx, by, region, ctx.f(SANS_B, 9.5), fill=RED)
            ctx.line(bx + ctx.tlen(region, ctx.f(SANS_B, 9.5)) + 6, by + 5,
                     bx + col_w, by + 5, fill=RULE, w=1)
            by += 14
            for n, txt in items:
                num_s = f"{n}  "
                nw = ctx.tlen(num_s, ctx.f(SANS_B, 10))
                ctx.text(bx, by, str(n), ctx.f(SANS_B, 10), fill=RED)
                yy = ctx.para(bx + nw, by, txt, ctx.f(SANS, 10), col_w - nw, 11, max_lines=2)
                by = yy
            by += 3
        col_bottom = max(col_bottom, by)
        col_bottoms.append(by)
    # ---- map box: below #37 (col 3), beside #27 (col 2), above DATE CHECK ----
    map_x0 = MX + 2 * (col_w + 14)
    map_x1 = MX + CW
    map_y0 = col_bottoms[2] + 4
    map_y1 = col_bottom + 1
    if map_y1 - map_y0 >= 40:
        draw_map_box(ctx, map_x0, map_y0, map_x1 - map_x0, map_y1 - map_y0)
    y = col_bottom + 2
    # ---- date check ----
    dc_y = y
    ctx.rrect(MX, dc_y, MX + CW, dc_y + 36, 3, fill=(250, 238, 232), out=RED, w=1)
    ctx.rrect(MX, dc_y, MX + 108, dc_y + 36, 3, fill=RED)
    ctx.text(MX + 54, dc_y + 18, "38 \u00b7 DATE CHECK", ctx.f(SANS_B, 10), fill=WHITE, anchor="mm")
    ctx.para(MX + 118, dc_y + 3, DATE_CHECK, ctx.f(SANS, 9.5), CW - 128, 11, max_lines=3)
    y = dc_y + 36 + 5
    # ---- footer ----
    ctx.text(MX + CW / 2, y, FOOTER, ctx.f(SANS, 8), fill=GRAY, anchor="ma")
    y += 9
    if y > 1024:
        ctx.warn.append(f"TOTAL HEIGHT {y} > 1024 — overflow by {y - 1024}px")
    print(f"scale={S} final_y={y} warnings={ctx.warn}")
    if fmt == "JPEG":
        ctx.img.save(path, "JPEG", quality=quality, optimize=True, progressive=False)
    else:
        ctx.img.save(path, "PNG", optimize=True)
    return ctx

if __name__ == "__main__":
    import os
    os.makedirs("/home/hatch/workspace/makefun/news18-models", exist_ok=True)
    render(1, "/home/hatch/workspace/makefun/news18-model-b-v15.jpg", "JPEG", quality=93)
    render(2, "/home/hatch/workspace/makefun/news18-model-b-v15-clear.png", "PNG")
    for p in ["/home/hatch/workspace/makefun/news18-model-b-v15.jpg",
              "/home/hatch/workspace/makefun/news18-model-b-v15-clear.png"]:
        data = open(p, "rb").read()
        print(p, len(data), "bytes", hashlib.sha256(data).hexdigest()[:12])
