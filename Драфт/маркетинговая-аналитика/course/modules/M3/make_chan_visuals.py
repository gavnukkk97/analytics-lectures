# -*- coding: utf-8 -*-
"""Визуализации к лекции «Каналы и атрибуция», часть 1 — каналы (модуль М3).

Запуск: python3 course/modules/M3/make_chan_visuals.py → images/chan_*.png
Палитра X5, заголовок = вывод, числа согласованы с уроками 3.1–3.3.
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(11)

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.grid": True, "grid.alpha": 0.25, "figure.facecolor": "white",
})
NAVY, ORANGE, GREY = "#0E2841", "#E97132", "#8C9BAB"
GREEN, RED = "#55A868", "#C44E52"
BB = dict(boxstyle="round,pad=0.28", fc="white", ec="none", alpha=0.88)

def save(fig, name):
    fig.savefig(OUT / name, bbox_inches="tight")
    print("ok", name)

# ============================================================
# 1. Карта каналов: скорость × измеримость
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))
chans = [
    # название, x-категория (0 мгновенно, 1 недели, 2 месяцы–годы), измеримость, dx, dy, цвет
    ("Контекст",            0, 0.93, 0.10, 0.030, GREEN),
    ("Кросс-промо · пуши",  0, 0.80, 0.10, 0.030, GREEN),
    ("Таргет · медийка",    0, 0.62, 0.10, 0.030, GREEN),
    ("Партнёрки · CPA",     1, 0.78, 0.00, 0.035, GREEN),
    ("Агрегаторы",          1, 0.60, 0.00, 0.035, NAVY),
    ("Блогеры · Telegram",  1, 0.40, 0.00, 0.035, NAVY),
    ("SEO · органика",      2, 0.66, 0.00, 0.035, NAVY),
    ("PR · СМИ",            2, 0.42, 0.00, 0.035, NAVY),
    ("Бренд-запросы · direct", 2, 0.26, 0.00, 0.035, ORANGE),
    ("ТВ · радио · наружка",   2, 0.08, 0.00, 0.035, RED),
]
for name, xc, meas, dx, dy, c in chans:
    x = xc + rng.uniform(-0.13, 0.13)
    ax.scatter([x], [meas], s=240, color=c, alpha=0.85, edgecolor="white", lw=2, zorder=5)
    ax.text(x + dx, meas + dy, name, fontsize=10, va="center", color="#16324a",
            fontweight="bold", bbox=BB)
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(["мгновенно", "недели", "месяцы–годы"], fontsize=11)
ax.set_xlim(-0.55, 2.75); ax.set_ylim(-0.05, 1.08)
ax.set_ylabel("измеримость напрямую")
ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_yticklabels(["нет (спецметоды)", "низкая", "средняя", "высокая", "полная"])
ax.set_title("Карта каналов: скорость эффекта × измеримость")
ax.annotate("ТВ нельзя разметить:\nоцениваем косвенно (3.3)", xy=(2.02, 0.08),
            xytext=(0.62, 0.13), color=RED, fontsize=9.5, fontweight="bold",
            ha="left", bbox=BB,
            arrowprops=dict(arrowstyle="->", color=RED, lw=1.4))
fig.tight_layout(); save(fig, "chan_01_map.png")

# ============================================================
# 2. Этажи воронки: кто что делает
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.6))
floors = [
    ("СОЗДАЮТ спрос", "ТВ · медийка · PR · блогеры", "охват · брендовые запросы · direct", NAVY, 0.66),
    ("ЛОВЯТ спрос", "контекст · SEO · агрегаторы", "конверсия · CAC · CPO", GREEN, 0.40),
    ("ВОЗВРАЩАЮТ", "email · пуши · CRM · рефералы", "retention · LTV · частота", ORANGE, 0.14),
]
for name, who, metric, c, y in floors:
    ax.add_patch(plt.Rectangle((0.03, y), 0.94, 0.18, fc=c, alpha=0.16, ec=c, lw=2.5))
    ax.text(0.06, y + 0.115, name, fontsize=13, fontweight="bold", color=c, va="center")
    ax.text(0.30, y + 0.115, who, fontsize=11, va="center", color="#16324a")
    ax.text(0.66, y + 0.115, "метрики: " + metric, fontsize=9.5, va="center", color="#5a6b7d")
for y0, y1 in [(0.62, 0.60), (0.36, 0.34)]:
    ax.annotate("", xy=(0.5, y1), xytext=(0.5, y0 + 0.02),
                arrowprops=dict(arrowstyle="-|>", lw=2.5, color=GREY))
ax.text(0.545, 0.60, "спрос созрел", fontsize=9, color=GREY, va="center", style="italic")
ax.text(0.545, 0.34, "купил — вернём", fontsize=9, color=GREY, va="center", style="italic")
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); ax.grid(False)
ax.set_title("Разные рекламы — на разных этажах воронки")
fig.tight_layout(); save(fig, "chan_02_floors.png")

# ============================================================
# 3. Игла перформанса: CAC греется, LTV стоит
# ============================================================
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))
mo = np.arange(0, 25)
cac = 420 * (1 + 0.55 * (1 - np.exp(-mo / 10)))
ltv = np.full_like(mo, 780.0, dtype=float)
a.plot(mo, cac, lw=2.5, color=RED, label="CAC контекста")
a.plot(mo, ltv, lw=2.5, color=GREEN, ls="--", label="LTV12 когорт")
a.set_xlim(0, 24); a.set_xticks(range(0, 25, 4))
a.set_ylim(0, 900); a.set_yticks(range(0, 901, 150))
a.set_xlabel("месяц закупки"); a.set_ylabel("₽")
a.set_title("аукцион греется молча")
a.legend(frameon=False, fontsize=9, loc="center right")
b.plot(mo, ltv / cac, lw=2.5, color=NAVY)
b.axhspan(0, 1.5, color=RED, alpha=0.10)
b.axhline(1.5, color=RED, ls=":", lw=2)
b.text(23.5, 1.28, "зона «слезать с иглы»:\nстроить активы (SEO, бренд, рефералы)",
       ha="right", fontsize=9, color=RED, fontweight="bold", bbox=BB)
b.set_xlim(0, 24); b.set_xticks(range(0, 25, 4))
b.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
b.set_xlabel("месяц закупки"); b.set_ylabel("LTV / CAC")
b.set_ylim(0, 2.1)
b.set_title("окупаемость ползёт вниз")
fig.suptitle("Игла перформанса: CAC растёт — LTV/CAC падает", fontweight="bold", fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.94)); save(fig, "chan_03_needle.png")

# ============================================================
# 4. Портфель «ЕдаДома»: CAC и окупаемость
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.2))
rows = [("Контекст", 420, "LTV/CAC 1,8 — рабочая лошадка", GREEN),
        ("Таргет", 610, "LTV/CAC 1,1 — на грани, тестировать связки", ORANGE),
        ("Блогеры", 780, "LTV/CAC 1,6 — дорогой вход, дорогой LTV", NAVY),
        ("ТВ (2 города)", 900, "«CAC» через гео-оценку — растит весь рынок", GREY)]
y = np.arange(len(rows))[::-1]
for yi, (name, cac, verdict, c) in zip(y, rows):
    ax.barh(yi, cac, color=c, alpha=0.85, height=0.58)
    ax.text(cac - 18, yi, f"{cac} ₽", va="center", ha="right", fontsize=11,
            fontweight="bold", color="white")
    ax.text(12, yi, name, va="center", fontsize=11, color="white", fontweight="bold")
    ax.text(1000, yi, verdict, va="center", fontsize=9, color="#5a6b7d")
ax.set_yticks([]); ax.set_xlim(0, 1750); ax.set_xticks(range(0, 1001, 250))
ax.set_xlabel("CAC, ₽ (учебные числа, месяц)")
ax.grid(axis="y", alpha=0)
ax.set_title("Портфель «ЕдаДома»: цена входа и окупаемость каналов")
fig.tight_layout(); save(fig, "chan_04_portfolio.png")

# ============================================================
# 5. Анатомия размеченной ссылки
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.4))
lines = [
    ("https://edadoma.ru/?utm_source=yandex", "площадка — обязательно", NAVY, True),
    ("&utm_medium=cpc", "тип трафика — обязательно", NAVY, True),
    ("&utm_campaign=spring_delivery_msk", "кампания — обязательно", NAVY, True),
    ("&utm_content=banner_top|{creative_id}", "креатив — опционально", GREY, False),
    ("&utm_term={keyword}", "ключевое слово — опционально", GREY, False),
]
for i, (code, note, c, req) in enumerate(lines):
    yi = 4 - i
    ax.text(0.02, yi, code, fontfamily="monospace", fontsize=11.5, color=c,
            fontweight="bold", va="center")
    ax.text(0.60, yi, note, fontsize=10, va="center", color="#5a6b7d")
    if req:
        ax.text(0.505, yi, "✔", fontsize=10, color=GREEN, va="center", fontweight="bold")
ax.text(0.02, -0.55, "правила: латиница · регистр важен · дефисы вместо пробелов · один «?» · макросы из рекламных систем",
        fontsize=9.5, color=ORANGE, fontweight="bold", bbox=BB)
ax.set_xlim(0, 1.02); ax.set_ylim(-1.0, 4.8); ax.axis("off"); ax.grid(False)
ax.set_title("Анатомия размеченной ссылки: 5 параметров")
fig.tight_layout(); save(fig, "chan_05_utm_anatomy.png")

# ============================================================
# 6. Аудит 30 ссылок: waffle 30%
# ============================================================
fig, ax = plt.subplots(figsize=(10, 3.8))
def cell_color(i):                       # первые 9 клеток — «слепая зона» (30%)
    if i < 4: return RED                 # без utm_medium
    if i < 6: return ORANGE              # кириллица в campaign
    if i < 9: return "#B98A5A"           # пробелы и регистр-двойники
    return "#C9DCD2"                     # размечены чисто
for i in range(30):
    r, c = divmod(i, 10)
    x, y = c * 1.0, -r * 1.0
    color = cell_color(i)
    ax.add_patch(plt.Rectangle((x, y), 0.86, 0.86, fc=color, ec="white", lw=2))
    ax.text(x + 0.43, y + 0.43, str(i + 1), ha="center", va="center", fontsize=8,
            color="#16324a" if i >= 9 else "white", fontweight="bold")
from matplotlib.patches import Patch
ax.legend(handles=[
    Patch(color="#C9DCD2", label="размечены чисто (21 из 30)"),
    Patch(color=RED, label="без utm_medium — сольётся в «не определён» (4)"),
    Patch(color=ORANGE, label="кириллица в campaign — потеряется (2)"),
    Patch(color="#B98A5A", label="пробелы и регистр-двойники (3)"),
], loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False, fontsize=9)
ax.set_xlim(-0.1, 9.95); ax.set_ylim(-2.2, 1.0)
ax.set_aspect("equal"); ax.axis("off"); ax.grid(False)
ax.set_title("Аудит 30 ссылок: ~30% месяца — в тумане")
fig.tight_layout(); save(fig, "chan_06_audit.png")

# ============================================================
# 7. Пик-анализ: брендовые запросы после вылетов
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.4))
wk = np.arange(1, 17)
base = 4.0 + 0.03 * (wk - 1) + rng.normal(0, 0.06, len(wk))
spike = base.copy()
spike[5] = 5.6; spike[6] = 5.1; spike[7] = 4.7        # вылет 1 (неделя 6)
spike[9] = 5.05; spike[10] = 4.75; spike[11] = 4.5    # вылет 2 (неделя 10)
ax.plot(wk, spike, lw=2.5, color=NAVY, marker="o", ms=5, label="брендовые запросы, тыс/нед")
ax.axhline(4.0, color=GREY, ls=":", lw=2, label="базовая линия 4,0 тыс")
for w in (6, 10):
    ax.axvline(w, color=ORANGE, ls="--", lw=1.6)
ax.text(6.15, 3.45, "вылет ролика", color=ORANGE, fontsize=9, rotation=90, va="bottom")
ax.text(10.15, 3.45, "повтор", color=ORANGE, fontsize=9, rotation=90, va="bottom")
ax.annotate("+40% к базе", xy=(6, 5.6), xytext=(7.2, 5.62), color=GREEN,
            fontsize=10.5, fontweight="bold", bbox=BB,
            arrowprops=dict(arrowstyle="->", color=GREEN, lw=1.4))
ax.text(13.6, 4.32, "затухание ≈ 3 нед:\n«период полураспа́да памяти»", fontsize=9,
        color="#5a6b7d", ha="center", bbox=BB)
ax.set_xticks(range(2, 17, 2)); ax.set_ylim(3.2, 6.0)
ax.set_xlabel("неделя"); ax.set_ylabel("тыс. запросов")
ax.legend(frameon=False, fontsize=9, loc="lower right")
ax.set_title("Пик-анализ: брендовые запросы вспыхивают после вылетов")
fig.tight_layout(); save(fig, "chan_07_tv_spike.png")

# ============================================================
# 8. Гео-тест (DiD)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.4))
wk = np.arange(1, 17)
test = np.where(wk < 9, 200 + (wk - 1) * 0.4, 202.8 + (wk - 9) * 8.0)
ctrl = np.where(wk < 9, 197 + (wk - 1) * 0.4, 198.6 + (wk - 9) * 0.875)
ax.plot(wk, test, lw=2.5, color=ORANGE, label="тестовые гео (ТВ был)")
ax.plot(wk, ctrl, lw=2.5, color=GREY, ls="--", label="контрольные гео (без ТВ)")
ax.axvline(9, color="#333", ls=":", lw=1.6)
ax.text(9.2, 199.6, "запуск ТВ", fontsize=9.5, rotation=90, va="bottom")
ax.annotate("", xy=(16.4, test[-1]), xytext=(16.4, ctrl[-1]),
            arrowprops=dict(arrowstyle="<->", color=GREEN, lw=2))
ax.text(15.8, (test[-1] + ctrl[-1]) / 2, "DiD:\n(+64) − (+7)\n= +57 новых\nна 10 тыс.",
        ha="right", va="center", fontsize=9.5, color=GREEN, fontweight="bold", bbox=BB)
ax.set_xlim(1, 16); ax.set_xticks(range(2, 17, 2))
ax.set_ylim(194, 272); ax.set_yticks(range(200, 271, 20))
ax.set_xlabel("неделя"); ax.set_ylabel("новых пользователей на 10 тыс. жителей")
ax.legend(frameon=False, fontsize=9, loc="upper left")
ax.set_title("Гео-тест (DiD): инкрементальный эффект ТВ")
fig.tight_layout(); save(fig, "chan_08_geo_did.png")

# ============================================================
# 9. Иерархия доказательств
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.2))
levels = [
    ("Гео / АБ-эксперименты", "инкрементальность — золото, когда возможно", GREEN, 0.07, 0.30),
    ("MMM — media mix modeling", "все каналы сразу, история 1–2 года, Robyn/Meridian", NAVY, 0.38, 0.54),
    ("Пик-анализ + опросы/промокоды", "быстро и дёшево — первый эшелон", ORANGE, 0.69, 0.78),
]
for name, note, c, y, w in levels:
    ax.add_patch(plt.Rectangle((0.05, y), w, 0.19, fc=c, alpha=0.16, ec=c, lw=2.5))
    ax.text(0.08, y + 0.125, name, fontsize=12, fontweight="bold", color=c, va="center")
    ax.text(0.08, y + 0.052, note, fontsize=9.5, color="#5a6b7d", va="center")
ax.annotate("", xy=(0.965, 0.28), xytext=(0.965, 0.86),
            arrowprops=dict(arrowstyle="-|>", lw=2.5, color=NAVY))
ax.text(0.935, 0.56, "дороже · дольше · честнее", rotation=90, va="center",
        fontsize=9.5, color=NAVY, fontweight="bold")
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); ax.grid(False)
ax.set_title("Иерархия доказательств для немаркируемых каналов")
fig.tight_layout(); save(fig, "chan_09_hierarchy.png")

print("Готово: 9 картинок в", OUT)
