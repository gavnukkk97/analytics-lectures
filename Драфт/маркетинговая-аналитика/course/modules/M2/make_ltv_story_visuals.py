# -*- coding: utf-8 -*-
"""Визуализации к лекции-рассказу «Как считают LTV» (lecture-story-ltv.md).

Запуск: python3 course/modules/M2/make_ltv_story_visuals.py → images/ltv_story_*.png
Стиль курса: заголовок = вывод; числа согласованы с рассказом.

Канон чисел (одинаков во всех картинках и в рассказе):
  маржа когорты по мес, тыс ₽: 320,180,145,90,70,60,52,47,43,40,38,36 (когорта 1000 чел)
  LTV(N), ₽/юзер: 320,500,645,735,805,865,917,964,1007,1047,1085,1121
  «вечный» хвост к 24 мес ≈ 1175; прогноз бутстрапом 12 мес = 1080 ± 90
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(23)

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.grid": True, "grid.alpha": 0.25, "figure.facecolor": "white",
})
C_MAIN, C_ACC, C_TRUE, C_BAD = "#4C72B0", "#DD8452", "#55A868", "#C44E52"

# белая плашка под любой подписью, лежащей поверх сетки/кривых
BB = dict(boxstyle="round,pad=0.28", fc="white", ec="none", alpha=0.88)

def save(fig, name):
    fig.savefig(OUT / name, bbox_inches="tight")
    print("ok", name)

# --- канонические числа рассказа -------------------------------------------
profit_m = np.array([320, 180, 145, 90, 70, 60, 52, 47, 43, 40, 38, 36])  # тыс ₽ маржи когорты
N_COHORT = 1000
ltv_cum = np.cumsum(profit_m) / N_COHORT * 1000          # ₽/юзер: 320..1121
ltv_m = np.concatenate([[0], ltv_cum,
                        ltv_cum[-1] + 55 * (1 - np.exp(-np.arange(1, 13) / 6))])
months = np.arange(0, 25)                                # мес 0..24, «вечный» хвост ≈ 1175

# ============================================================
# 1. Маржа, а не выручка (кейс Dropbox)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
a = axes[0]
a.bar(["Выручка", "Переменные\nзатраты", "Валовая\nмаржа"], [100, 67, 33],
      color=[C_MAIN, C_BAD, C_TRUE], width=0.62)
for i, v in enumerate([100, 67, 33]):
    a.text(i, v + 3, f"{v}%", ha="center", fontweight="bold", fontsize=11)
a.set_ylim(0, 120); a.set_yticks(range(0, 101, 20)); a.set_ylabel("% от выручки")
a.set_title("Dropbox, 2015: 67% выручки — переменные затраты")
b = axes[1]
b.bar(["Выручка", "Маржа 25%"], [1200, 300], color=[C_MAIN, C_TRUE], width=0.5)
for i, v in enumerate([1200, 300]):
    b.text(i, v + 30, f"{v} ₽", ha="center", fontweight="bold", fontsize=11)
b.set_ylim(0, 1400); b.set_yticks(range(0, 1401, 200)); b.set_ylabel("₽ на заказ («ЕдаДома»)")
b.set_title("Наш пример: маржа 25% — LTV считают от неё")
fig.tight_layout(); save(fig, "ltv_story_01_margin.png")

# ============================================================
# 2. LTV — кривая, а не число
# ============================================================
fig, ax = plt.subplots(figsize=(9, 4.4))
ax.plot(months, ltv_m, lw=2.5, color=C_MAIN)
pts = [(1, 320, "LTV 1 мес\n≈ 320 ₽", C_ACC, (1.9, 120)),
       (3, 645, "LTV 3 мес\n= 645 ₽", C_TRUE, (4.6, 430)),
       (12, 1121, "LTV 12 мес\n≈ 1120 ₽", C_MAIN, (7.6, 1180)),
       (24, 1175, "«вечный LTV» ≈ 1175?\nстоп-машина", C_BAD, (14.5, 1330))]
for m, v, label, c, (tx, ty) in pts:
    ax.scatter([m], [v], s=60, color=c, zorder=5)
    ax.annotate(label, xy=(m, v), xytext=(tx, ty), fontsize=9.5, color=c,
                fontweight="bold", ha="left", bbox=BB,
                arrowprops=dict(arrowstyle="-", color=c, lw=1.1, shrinkB=4))
ax.set_xlim(0, 25.5); ax.set_ylim(0, 1500)
ax.set_xlabel("возраст когорты, месяцев"); ax.set_ylabel("накопленная маржа на юзера, ₽")
ax.set_title("LTV — кривая, а не число: сначала выбираем горизонт")
fig.tight_layout(); save(fig, "ltv_story_02_curve.png")

# ============================================================
# 3. Почему lifetime — «мифический»
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
a = axes[0]
m = np.arange(0, 13)
ret = 0.42 * np.exp(-m / 1.8) + 0.22
a.plot(m, ret * 100, lw=2.5, color=C_MAIN)
a.fill_between(m, ret * 100, alpha=0.15, color=C_MAIN)
a.axvline(6, color=C_BAD, ls="--", lw=1.6)
a.text(5.6, 41, "где резать\nплощадь?", color=C_BAD, fontsize=10,
       fontweight="bold", ha="right", bbox=BB)
a.set_xlim(0, 12.6); a.set_ylim(0, 70)
a.set_xlabel("месяц жизни"); a.set_ylabel("retention, %")
a.set_title("Площадь под retention: где обрывать кривую?")
b = axes[1]
ages = ["1-й мес", "3-й мес", "6-й мес", "12-й мес"]
churn = [35, 22, 12, 5]
b.bar(ages, churn, color=[C_BAD, C_ACC, C_MAIN, C_TRUE], width=0.6)
for i, v in enumerate(churn):
    b.text(i, v + 1.2, f"{v}%", ha="center", fontweight="bold")
b.set_ylim(0, 42); b.set_ylabel("churn, % в месяц")
b.set_title("Churn зависит от возраста: «средний» — мусор")
fig.tight_layout(); save(fig, "ltv_story_03_lifetime.png")

# ============================================================
# 4. Исторический vs когортный
# ============================================================
fig, ax = plt.subplots(figsize=(9, 4.6))
mm = np.arange(0, 13)
ax.plot(mm, ltv_m[:13], lw=2.5, color=C_TRUE, label="когорта 12 мес назад (зрелая)")
ax.plot(mm[:4], ltv_m[:4], lw=2.5, color=C_ACC, ls="--", label="когорта 3 мес назад (недозревшая)")
ax.axhline(1400, color=C_BAD, ls=":", lw=2, label="«средний LTV по базе» = 1400 ₽")
ax.scatter([3], [645], s=70, color=C_ACC, zorder=5)
ax.annotate("факт молодого: 645 ₽", xy=(3, 645), xytext=(4.6, 380), fontsize=10,
            color=C_ACC, fontweight="bold", bbox=BB,
            arrowprops=dict(arrowstyle="-", color=C_ACC, lw=1.1, shrinkB=4))
ax.set_xlim(0, 12.6); ax.set_ylim(0, 1750)
ax.set_xlabel("возраст когорты, месяцев"); ax.set_ylabel("LTV (кумулятивно), ₽")
ax.set_title("«Средняя по базе» — это вчерашние клиенты: сегодня другие")
ax.legend(loc="lower right")
fig.tight_layout(); save(fig, "ltv_story_04_base_vs_cohort.png")

# ============================================================
# 5. Когортный метод за 4 шага
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(11, 6.8))
x12 = np.arange(1, 13)
a = axes[0, 0]
a.bar(x12, profit_m, color=C_MAIN)
a.set_xlim(0.4, 12.6); a.set_xticks(range(2, 13, 2))
a.set_ylim(0, 350); a.set_yticks(range(0, 351, 50))
a.set_title("Шаг 1–2. Валовая маржа когорты по месяцам")
a.set_xlabel("месяц жизни"); a.set_ylabel("маржа, тыс ₽")
b = axes[0, 1]
cum = np.cumsum(profit_m)
b.plot(x12, cum, lw=2.5, color=C_MAIN)
b.fill_between(x12, cum, alpha=0.15, color=C_MAIN)
b.set_xlim(0.4, 12.6); b.set_xticks(range(2, 13, 2))
b.set_ylim(0, 1250); b.set_yticks(range(0, 1201, 200))
b.set_title("Шаг 3. Кумулятив: месяц N = сумма 0..N")
b.set_xlabel("месяц жизни"); b.set_ylabel("Σ маржи, тыс ₽")
c = axes[1, 0]
c.plot(x12, cum / N_COHORT * 1000, lw=2.5, color=C_TRUE)
c.scatter([3], [645], s=70, color=C_ACC, zorder=5)
c.annotate("LTV3 = 645 ₽", xy=(3, 645), xytext=(5.4, 380),
           color=C_ACC, fontweight="bold", fontsize=10, bbox=BB,
           arrowprops=dict(arrowstyle="->", color=C_ACC, lw=1.5, shrinkB=4))
c.set_xlim(0.4, 12.6); c.set_xticks(range(2, 13, 2))
c.set_ylim(0, 1250); c.set_yticks(range(0, 1201, 200))
c.set_title("Шаг 4. Делим на размер когорты → кривая LTV")
c.set_xlabel("месяц жизни"); c.set_ylabel("LTV, ₽/юзер")
d = axes[1, 1]
d.axis("off")
d.set_title("Правила чтения кривой")
rules = [("наклон = деньги сейчас", C_MAIN, 0.74),
         ("плато = «ядро» ценности", C_TRUE, 0.55),
         ("срезы по каналам — где польза", C_ACC, 0.36),
         ("цена метода: ждать горизонт", C_BAD, 0.17)]
for text, color, y in rules:
    d.text(0.03, y, text, fontsize=12, color=color, fontweight="bold", va="center")
fig.tight_layout(h_pad=2.2); save(fig, "ltv_story_05_cohort_steps.png")

# ============================================================
# 6. Прогноз-эвристика: пороги
# ============================================================
fig, ax = plt.subplots(figsize=(9, 4.6))
days = np.arange(0, 31)
def curve(a, b): return 380 * (1 - np.exp(-days / b)) * a
for mult, b, fate in [(0.78, 5, "стоп"), (0.95, 6, "стоп"),
                      (1.08, 7, "оставить"), (1.25, 5, "масштабировать"),
                      (1.4, 6, "масштабировать")]:
    y = curve(mult, b)
    color = C_BAD if fate == "стоп" else (C_TRUE if fate == "масштабировать" else C_MAIN)
    ax.plot(days, y, lw=2, color=color, alpha=0.9)
ax.axhline(380, color="#333", ls="--", lw=2)
ax.text(29.5, 400, "порог LTV30 = 380 ₽ (выучен по истории)", fontsize=10,
        fontweight="bold", ha="right", bbox=BB)
ax.text(8, 105, "кампании ниже порога →\nвыключаем", color=C_BAD, fontsize=10,
        fontweight="bold", bbox=BB)
ax.text(5.5, 560, "на уровне или выше →\nоставляем / масштабируем", color=C_TRUE,
        fontsize=10, fontweight="bold", bbox=BB)
ax.set_xlim(0, 30); ax.set_ylim(0, 680)
ax.set_xlabel("дней с запуска кампании"); ax.set_ylabel("LTV кумулятивно, ₽")
ax.set_title("Эвристика: не ждать год — сравнить с порогом на раннем горизонте")
fig.tight_layout(); save(fig, "ltv_story_06_thresholds.png")

# ============================================================
# 7. Прогноз-модели: бутстрап-хвост и BG/NBD+GG
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.6))
a = axes[0]
mm12 = np.arange(0, 13)
zrel = ltv_m[3:13] - ltv_m[3]                      # прирост зрелой кривой с 3 мес
tails = np.array([ltv_m[3] + zrel * rng.normal(0.92, 0.115) for _ in range(400)])
lo, hi = np.percentile(tails, [5, 95], axis=0)
a.plot(mm12, ltv_m[:13], lw=2, color=C_TRUE, label="хвост по зрелым когортам (бутстрап)")
a.fill_between(mm12[3:], lo, hi, color=C_TRUE, alpha=0.2, label="90% интервал")
a.plot(mm12[:4], ltv_m[:4], lw=3, color=C_MAIN, label="факт (3 мес)")
a.scatter([12], [1083], s=80, color=C_ACC, zorder=5)
a.annotate("прогноз 12 мес:\n1080 ± 90 ₽", xy=(12, 1083), xytext=(6.2, 700),
           color=C_ACC, fontweight="bold", fontsize=10, bbox=BB,
           arrowprops=dict(arrowstyle="->", color=C_ACC, lw=1.4, shrinkB=5))
a.set_xlim(0, 12.6); a.set_ylim(0, 1450)
a.set_xlabel("месяц жизни"); a.set_ylabel("LTV, ₽")
a.set_title("Бутстрап: недозревшую когорту достраиваем похожими")
a.legend(loc="lower right", fontsize=9)
b = axes[1]
b.axis("off")
b.set_title("BG/NBD + Gamma-Gamma: неконтрактные продукты")
boxes = [
    (0.03, 0.62, "клиент: частота,\nдавность,\nвозраст (F/R/T)", C_MAIN),
    (0.36, 0.62, "BG/NBD:\nсколько ещё\nпокупок", C_ACC),
    (0.03, 0.18, "чеки клиента", C_MAIN),
    (0.36, 0.18, "Gamma-Gamma:\nсредний чек", C_ACC),
    (0.72, 0.40, "LTV на горизонт\n(F × M)", C_TRUE),
]
for x, y, t, c in boxes:
    b.add_patch(plt.Rectangle((x, y), 0.26, 0.22, fc=c, alpha=0.18, ec=c, lw=2))
    b.text(x + 0.13, y + 0.11, t, ha="center", va="center", fontsize=9.5, fontweight="bold")
for (x1, y1), (x2, y2) in [((0.29, 0.73), (0.36, 0.73)), ((0.29, 0.29), (0.36, 0.29)),
                           ((0.62, 0.73), (0.78, 0.62)), ((0.62, 0.29), (0.78, 0.46))]:
    b.annotate("", xy=(x2, y2), xytext=(x1, y1),
               arrowprops=dict(arrowstyle="-|>", lw=2, color="#333"))
b.text(0.5, 0.04, "лимит: предпосылки + валидация на когортах с известным фактом",
       ha="center", fontsize=9.5, color=C_BAD, fontweight="bold")
fig.tight_layout(); save(fig, "ltv_story_07_models.png")

# ============================================================
# 8. Лесница методов
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))
ax.axis("off")
steps = [
    ("1. Салфетка", "ARPU × Lifetime", "цена ошибки: бюджеты на мусоре", "#B9C4D6"),
    ("2. Исторический", "Σ фактов клиента", "LTV старых о новых", "#7C93B8"),
    ("3. Когортный факт", "кумулятив маржи / размер", "ждать горизонт", C_MAIN),
    ("4. Эвристика", "пороги LTV7/LTV30", "порог из другой эпохи", "#8FBF9F"),
    ("5. Модель", "бутстрап, BG/NBD, ML", "невалидированная модель", C_TRUE),
]
right_edges = []
for i, (name, how, cost, c) in enumerate(steps):
    y = 0.07 + i * 0.18
    w = 0.78 - i * 0.12          # пирамида: внизу широкая «салфетка», наверху узкая «модель»
    right_edges.append(0.04 + w)
    ax.add_patch(plt.Rectangle((0.04, y), w, 0.15, fc=c, alpha=0.85, ec="white", lw=2))
    ax.text(0.07, y + 0.095, name, fontsize=13, fontweight="bold", color="white", va="center")
    ax.text(0.07, y + 0.038, how, fontsize=9.5, color="white", va="center")
    ax.text(0.06 + w + 0.02, y + 0.075, cost, fontsize=9.5, color="#333", va="center")
# стрелка «выше — точнее»: вертикально справа от пирамиды, мимо всех ступеней
ax.annotate("", xy=(0.92, 0.90), xytext=(0.92, 0.20),
            arrowprops=dict(arrowstyle="-|>", lw=2.5, color=C_ACC))
ax.text(0.92, 0.965, "точность ↑ · сложность ↑ · терпение ↓", fontsize=10.5,
        color=C_ACC, fontweight="bold", ha="center")
ax.set_xlim(0, 1.05); ax.set_ylim(0, 1.02)
ax.set_title("Лестница методов LTV: чем выше — тем точнее и дороже")
fig.tight_layout(); save(fig, "ltv_story_08_ladder.png")

# ============================================================
# 9. Три вопроса к любому числу LTV
# ============================================================
fig, ax = plt.subplots(figsize=(10, 3.8))
ax.axis("off")
qs = [("«От маржи\nили от выручки?»", C_TRUE),
      ("«Какой горизонт\nи какие когорты?»", C_MAIN),
      ("«Факт или прогноз?\nКак валидирован?»", C_ACC)]
for i, (q, c) in enumerate(qs):
    x = 0.02 + i * 0.33
    ax.add_patch(plt.Rectangle((x, 0.16), 0.30, 0.60, fc=c, alpha=0.15, ec=c, lw=2.5))
    ax.text(x + 0.15, 0.46, q, ha="center", va="center", fontsize=12, fontweight="bold")
    ax.text(x + 0.15, 0.86, f"вопрос {i + 1}", ha="center", fontsize=10, color=c, fontweight="bold")
ax.text(0.5, 0.04, "нет ответов — число можно не слушать", ha="center",
        fontsize=11, color=C_BAD, fontweight="bold")
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_title("Три вопроса к любому числу LTV")
fig.tight_layout(); save(fig, "ltv_story_09_questions.png")

print("Готово: 9 картинок в", OUT)
