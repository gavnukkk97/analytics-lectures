# -*- coding: utf-8 -*-
"""Визуализации к лекции-рассказу «Как считают LTV» (lecture-story-ltv.md).

Запуск: python3 course/modules/M2/make_ltv_story_visuals.py → images/ltv_story_*.png
Стиль курса: заголовок = вывод; числа согласованы с рассказом.
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

def save(fig, name):
    fig.savefig(OUT / name, bbox_inches="tight")
    print("ok", name)

# ============================================================
# 1. Маржа, а не выручка (кейс Dropbox)
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
a = axes[0]
a.bar(["Выручка", "Переменные\nзатраты", "Валовая\nмаржа"], [100, 67, 33],
      color=[C_MAIN, C_BAD, C_TRUE], width=0.62)
for i, v in enumerate([100, 67, 33]):
    a.text(i, v + 2, f"{v}%", ha="center", fontweight="bold", fontsize=11)
a.set_ylim(0, 112); a.set_ylabel("% от выручки")
a.set_title("Dropbox, 2015: 67% выручки съедали переменные затраты")
b = axes[1]
b.bar(["Выручка", "Маржа 25%"], [1200, 300], color=[C_MAIN, C_TRUE], width=0.5)
for i, v in enumerate([1200, 300]):
    b.text(i, v + 25, f"{v} ₽", ha="center", fontweight="bold", fontsize=11)
b.set_ylabel("₽ на заказ («ЕдаДома»)")
b.set_title("LTV считают от маржи — выручка врёт в 4 раза")
fig.tight_layout(); save(fig, "ltv_story_01_margin.png")

# ============================================================
# 2. LTV — кривая, а не число
# ============================================================
months = np.arange(0, 25)
ltv = 1100 * (1 - np.exp(-months / 4.2))
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot(months, ltv, lw=2.5, color=C_MAIN)
for m, label, c in [(1, "LTV 1 мес\n≈ 290 ₽", C_ACC), (3, "LTV 3 мес\n= 645 ₽", C_TRUE),
                    (12, "LTV 12 мес\n≈ 1100 ₽", C_MAIN), (24, "«вечный LTV»?\nстоп-машина", C_BAD)]:
    ax.scatter([m], [ltv[m]], s=60, color=c, zorder=5)
    ax.annotate(label, (m, ltv[m]), xytext=(m - 0.5, ltv[m] + 90), fontsize=9.5,
                color=c, fontweight="bold", ha="center")
ax.set_xlabel("возраст когорты, месяцев"); ax.set_ylabel("накопленная маржа на юзера, ₽")
ax.set_title("LTV — кривая, а не число: сначала решаем, какой горизонт нам нужен")
fig.tight_layout(); save(fig, "ltv_story_02_curve.png")

# ============================================================
# 3. Почему lifetime — «мифический»
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4))
a = axes[0]
m = np.arange(0, 13)
ret = 0.42 * np.exp(-m / 1.8) + 0.22
a.plot(m, ret * 100, lw=2.5, color=C_MAIN)
a.fill_between(m, ret * 100, alpha=0.15, color=C_MAIN)
a.axvline(6, color=C_BAD, ls="--", lw=1.6)
a.text(6.2, 34, "где резать\nплощадь?", color=C_BAD, fontsize=10, fontweight="bold")
a.set_xlabel("месяц жизни"); a.set_ylabel("retention, %")
a.set_title("Площадь под retention: у кривой плато — где её кончать?")
b = axes[1]
ages = ["1-й мес", "3-й мес", "6-й мес", "12-й мес"]
churn = [35, 22, 12, 5]
b.bar(ages, churn, color=[C_BAD, C_ACC, C_MAIN, C_TRUE], width=0.6)
for i, v in enumerate(churn):
    b.text(i, v + 1, f"{v}%", ha="center", fontweight="bold")
b.set_ylabel("churn, % в месяц")
b.set_title("Churn зависит от возраста: 1/churn по «среднему» — мусор на входе")
fig.tight_layout(); save(fig, "ltv_story_03_lifetime.png")

# ============================================================
# 4. Исторический vs когортный
# ============================================================
fig, ax = plt.subplots(figsize=(9, 4.4))
mm = np.arange(0, 13)
ax.plot(mm, ltv[:13], lw=2.5, color=C_TRUE, label="когорта 12 мес назад (зрелая)")
ax.plot(mm[:4], ltv[:4], lw=2.5, color=C_ACC, ls="--", label="когорта 3 мес назад (недозревшая)")
ax.axhline(1400, color=C_BAD, ls=":", lw=2, label="«средний LTV по базе» = 1400 ₽ (старые клиенты)")
ax.scatter([3], [645], s=70, color=C_ACC, zorder=5)
ax.annotate("факт молодого: 645 ₽", (3, 645), xytext=(4.2, 430), fontsize=10,
            color=C_ACC, fontweight="bold")
ax.set_xlabel("возраст когорты, месяцев"); ax.set_ylabel("LTV (кумулятивно), ₽")
ax.set_title("«Средняя по базе» — это вчерашние клиенты: сегодня другие")
ax.legend(loc="lower right")
fig.tight_layout(); save(fig, "ltv_story_04_base_vs_cohort.png")

# ============================================================
# 5. Когортный метод за 4 шага
# ============================================================
fig, axes = plt.subplots(2, 2, figsize=(10.5, 6.4))
profit_m = np.array([120, 65, 50, 41, 35, 31, 28, 26, 24, 23, 22, 21])  # тыс ₽ маржи когорты
n = 1000
a = axes[0, 0]
a.bar(np.arange(1, 13), profit_m, color=C_MAIN)
a.set_title("Шаг 1–2. Валовая маржа когорты по месяцам")
a.set_xlabel("месяц жизни"); a.set_ylabel("маржа, тыс ₽")
b = axes[0, 1]
cum = np.cumsum(profit_m)
b.plot(np.arange(1, 13), cum, lw=2.5, color=C_MAIN)
b.fill_between(np.arange(1, 13), cum, alpha=0.15, color=C_MAIN)
b.set_title("Шаг 3. Кумулятив: месяц N = сумма 0..N")
b.set_xlabel("месяц жизни"); b.set_ylabel("Σ маржи, тыс ₽")
c = axes[1, 0]
c.plot(np.arange(1, 13), cum / n * 1000, lw=2.5, color=C_TRUE)
c.scatter([3], [cum[2] / n * 1000], s=70, color=C_ACC, zorder=5)
c.annotate(f"LTV3 = {cum[2]} ₽", (3, cum[2]), xytext=(4.5, cum[2] - 180),
           color=C_ACC, fontweight="bold", fontsize=10)
c.set_title("Шаг 4. Делим на размер когорты → кривая LTV")
c.set_xlabel("месяц жизни"); c.set_ylabel("LTV, ₽/юзер")
d = axes[1, 1]
d.axis("off")
d.set_title("Правила чтения кривой")
d.text(0.02, 0.72, "наклон = деньги сейчас", fontsize=12, color=C_MAIN, fontweight="bold")
d.text(0.02, 0.5, "плато = «ядро» ценности", fontsize=12, color=C_TRUE, fontweight="bold")
d.text(0.02, 0.28, "срезы по каналам — где польза", fontsize=12, color=C_ACC, fontweight="bold")
d.text(0.02, 0.08, "цена метода: ждать горизонт", fontsize=12, color=C_BAD, fontweight="bold")
fig.tight_layout(); save(fig, "ltv_story_05_cohort_steps.png")

# ============================================================
# 6. Прогноз-эвристика: пороги
# ============================================================
fig, ax = plt.subplots(figsize=(9, 4.4))
days = np.arange(0, 31)
def curve(a, b): return 380 * (1 - np.exp(-days / b)) * a
for i, (mult, b, fate) in enumerate([(0.78, 5, "стоп"), (0.95, 6, "стоп"),
                                     (1.08, 7, "оставить"), (1.25, 5, "масштабировать"),
                                     (1.4, 6, "масштабировать")]):
    y = curve(mult, b)
    color = C_BAD if fate == "стоп" else (C_TRUE if fate == "масштабировать" else C_MAIN)
    ax.plot(days, y, lw=2, color=color, alpha=0.9)
ax.axhline(380, color="#333", ls="--", lw=2)
ax.text(0.5, 400, "порог LTV30 = 380 ₽ (выучен по истории)", fontsize=10.5, fontweight="bold")
ax.text(16, 300, "кампании ниже порога →\nвыключаем", color=C_BAD, fontsize=10, fontweight="bold")
ax.text(16, 480, "на уровне или выше →\nоставляем / масштабируем", color=C_TRUE,
        fontsize=10, fontweight="bold")
ax.set_xlabel("дней с запуска кампании"); ax.set_ylabel("LTV кумулятивно, ₽")
ax.set_title("Эвристика: не ждать год — сравнить с порогом на раннем горизонте")
fig.tight_layout(); save(fig, "ltv_story_06_thresholds.png")

# ============================================================
# 7. Прогноз-модели: бутстрап-хвост и BG/NBD+GG
# ============================================================
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
a = axes[0]
mm12 = np.arange(0, 13)
fact = ltv[:4]
ltv12 = ltv[:13]
tails = []
for k in range(200):
    scale_k = rng.normal(1.0, 0.06)
    tails.append(ltv12[3] + (ltv12[3:] - ltv12[3]) * scale_k)
tails = np.array(tails)
lo, hi = np.percentile(tails, [5, 95], axis=0)
a.plot(mm12, ltv12, lw=2, color=C_TRUE, label="хвост по зрелым когортам (бутстрап)")
a.fill_between(mm12[3:], lo, hi, color=C_TRUE, alpha=0.2, label="90% интервал")
a.plot(mm12[:4], fact, lw=3, color=C_MAIN, label="факт (3 мес)")
a.scatter([12], [1080], s=80, color=C_ACC, zorder=5)
a.annotate("прогноз 12 мес:\n1080 ± 90 ₽", (12, 1080), xytext=(7.6, 700),
           color=C_ACC, fontweight="bold", fontsize=10)
a.set_xlabel("месяц жизни"); a.set_ylabel("LTV, ₽")
a.set_title("Бутстрап: недозревшую когорту достраиваем похожими")
a.legend(loc="lower right", fontsize=9)
b = axes[1]
b.axis("off")
b.set_title("BG/NBD + Gamma-Gamma: для «неконтрактных» (ушёл ≠ наблюдаем)")
boxes = [
    (0.03, 0.62, "клиент: частота,\nдавность, возраст (F/R/T)", C_MAIN),
    (0.36, 0.62, "BG/NBD:\nсколько ещё покупок", C_ACC),
    (0.03, 0.18, "чеки клиента", C_MAIN),
    (0.36, 0.18, "Gamma-Gamma:\nсредний чек", C_ACC),
    (0.72, 0.40, "LTV на горизонт\n(× )", C_TRUE),
]
for x, y, t, c in boxes:
    b.add_patch(plt.Rectangle((x, y), 0.26, 0.22, fc=c, alpha=0.18, ec=c, lw=2))
    b.text(x + 0.13, y + 0.11, t, ha="center", va="center", fontsize=9.5, fontweight="bold")
for (x1, y1), (x2, y2) in [((0.29, 0.73), (0.36, 0.73)), ((0.29, 0.29), (0.36, 0.29)),
                           ((0.62, 0.73), (0.78, 0.62)), ((0.62, 0.29), (0.78, 0.40))]:
    b.annotate("", xy=(x2, y2), xytext=(x1, y1),
               arrowprops=dict(arrowstyle="-|>", lw=2, color="#333"))
b.text(0.5, 0.02, "лимит: предпосылки + валидация на когортах с известным фактом",
        ha="center", fontsize=9.5, color=C_BAD, fontweight="bold")
fig.tight_layout(); save(fig, "ltv_story_07_models.png")

# ============================================================
# 8. Лестница методов
# ============================================================
fig, ax = plt.subplots(figsize=(10, 5))
ax.axis("off")
steps = [
    ("5. Модель", "бутстрап / BG/NBD / ML", "невалидированная\nмодель", C_TRUE),
    ("4. Эвристика", "пороги LTV7/LTV30", "порог из другой\nэпохи", "#8FBF9F"),
    ("3. Когортный факт", "кумулятив маржи / размер", "ждать горизонт", C_MAIN),
    ("2. Исторический", "Σ фактов клиента", "LTV старых\nо новых", "#7C93B8"),
    ("1. Салфетка", "ARPU × Lifetime", "бюджеты на мусоре", "#B9C4D6"),
]
for i, (name, how, cost, c) in enumerate(steps):
    y = 0.06 + i * 0.18
    w = 0.24 + i * 0.135
    ax.add_patch(plt.Rectangle((0.04, y), w, 0.15, fc=c, alpha=0.85, ec="white", lw=2))
    ax.text(0.07, y + 0.095, name, fontsize=13, fontweight="bold", color="white", va="center")
    ax.text(0.07, y + 0.038, how, fontsize=9.5, color="white", va="center")
    ax.text(0.06 + w + 0.02, y + 0.075, f"цена ошибки: {cost}", fontsize=9.5,
            color="#333", va="center")
ax.annotate("", xy=(0.86, 0.95), xytext=(0.5, 0.5),
            arrowprops=dict(arrowstyle="-|>", lw=2.5, color=C_ACC))
ax.text(0.64, 0.86, "точность ↑ · сложность ↑ · терпение ↓", rotation=0, fontsize=10.5,
        color=C_ACC, fontweight="bold")
ax.set_xlim(0, 1.05); ax.set_ylim(0, 1.02)
ax.set_title("Лестница методов LTV: чем выше — тем точнее и дороже")
fig.tight_layout(); save(fig, "ltv_story_08_ladder.png")

# ============================================================
# 9. Три вопроса к любому числу LTV
# ============================================================
fig, ax = plt.subplots(figsize=(10, 3.6))
ax.axis("off")
qs = [("«От маржи или от выручки?»", C_TRUE),
      ("«Какой горизонт и какие когорты?»", C_MAIN),
      ("«Факт или прогноз? Как валидирован?»", C_ACC)]
for i, (q, c) in enumerate(qs):
    x = 0.02 + i * 0.33
    ax.add_patch(plt.Rectangle((x, 0.18), 0.30, 0.55, fc=c, alpha=0.15, ec=c, lw=2.5))
    ax.text(x + 0.15, 0.45, q, ha="center", va="center", fontsize=12.5, fontweight="bold", wrap=True)
    ax.text(x + 0.15, 0.85, f"вопрос {i + 1}", ha="center", fontsize=10, color=c, fontweight="bold")
ax.text(0.5, 0.03, "нет ответов — число можно не слушать", ha="center",
        fontsize=11, color=C_BAD, fontweight="bold")
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_title("Три вопроса к любому числу LTV")
fig.tight_layout(); save(fig, "ltv_story_09_questions.png")

print("Готово: 9 картинок в", OUT)
