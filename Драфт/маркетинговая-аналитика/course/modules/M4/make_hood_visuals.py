# -*- coding: utf-8 -*-
"""«Под капотом» ML-атрибуции: три картинки для лекции 03 (модули 3–4).

Числа — реальный расчёт по practice_4_3 (edadoma.make_touches, SEED=2026,
логрегрессия вручную): веса, log-loss 0.69→0.37, разбор юзера 1001.

Запуск: python3 course/modules/M4/make_hood_visuals.py → images/hood_*.png
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)
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
# 1. Цепочки → матрица признаков
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.6))
cols = ["user_id", "путь касаний", "медийка", "контекст", "email", "бренд", "длина", "купил?"]
rows = [
    ["1001", "медийка→контекст→бренд", "1", "1", "0", "1", "3", "1"],
    ["1002", "контекст", "0", "1", "0", "0", "1", "0"],
    ["1003", "бренд→бренд", "0", "0", "0", "2", "2", "0"],
    ["1004", "медийка→email→контекст", "1", "1", "1", "0", "3", "1"],
]
tbl = ax.table(cellText=rows, colLabels=cols, cellLoc="center", loc="center",
               colWidths=[0.09, 0.30, 0.09, 0.09, 0.08, 0.08, 0.08, 0.09])
tbl.auto_set_font_size(False); tbl.set_fontsize(10.5); tbl.scale(1, 2.1)
for j in range(len(cols)):
    tbl[0, j].set_facecolor(NAVY)
    tbl[0, j].get_text().set_color("white")
    tbl[0, j].get_text().set_fontweight(True)
for i in range(1, len(rows) + 1):
    tbl[i, 1].set_text_props(ha="left")
    for j in range(len(cols)):
        tbl[i, j].set_edgecolor("#c9d2da")
        if j == 7:
            v = rows[i - 1][7]
            tbl[i, j].set_facecolor("#E8F3EC" if v == "1" else "#F7ECEC")
ax.text(0.5, 0.06, "…всего 6000 юзеров × 5 фич + метка «купил» из CRM — это и есть размеченные данные",
        transform=ax.transAxes, ha="center", fontsize=10, color=NAVY, fontweight="bold")
ax.axis("off"); ax.grid(False)
ax.set_title("Под капотом · шаг 1: цепочки превращаем в матрицу признаков")
fig.tight_layout(); save(fig, "hood_01_features.png")

# ============================================================
# 2. Обучение: P = σ(w·x), веса из данных
# ============================================================
fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.4), width_ratios=[1.05, 1])
a.axis("off"); a.grid(False)
a.text(0.02, 0.93, "P(конверсия) = σ(w·x)", fontsize=15, fontweight="bold", color=NAVY, va="top")
a.text(0.02, 0.74, "σ(z) = 1 / (1 + e⁻ᶻ)", fontsize=12, color="#5a6b7d", va="top")
a.text(0.02, 0.55,
       "z = w₀ + w₁·медийка + w₂·контекст\n"
       "    + w₃·email + w₄·бренд + w₅·длина\n\n"
       "подбираем w так, чтобы P выросла\n"
       "у купивших и упала у остальных:",
       fontsize=11, color="#16324a", va="top", linespacing=1.5)
a.text(0.02, 0.16, "градиентный спуск, 4000 шагов\nlog-loss: 0.693 → 0.366",
       fontsize=11, color=GREEN, fontweight="bold", va="top", linespacing=1.5)
w_labels = ["длина пути", "медийка", "email", "контекст\nнебренд", "бренд\nконтекст"]
w_vals = [0.269, 0.176, 0.137, 0.022, -0.065]
colors = [GREEN if v > 0.1 else (GREY if v > 0 else RED) for v in w_vals]
y = np.arange(len(w_vals))[::-1]
b.barh(y, w_vals, color=colors, height=0.6)
for yi, v in zip(y, w_vals):
    b.text(v + (0.012 if v >= 0 else -0.012), yi, f"{v:+.3f}",
           va="center", ha="left" if v >= 0 else "right",
           fontsize=10.5, fontweight="bold", color="#16324a")
b.axvline(0, color="#333", lw=1.2)
b.set_yticks(y); b.set_yticklabels(w_labels, fontsize=10.5)
b.set_xlim(-0.13, 0.36)
b.set_xlabel("вес w (в логитах) — чему модель поверила")
b.set_title("веса выучены из данных, а не заданы")
fig.suptitle("Под капотом · шаг 2: логрегрессия учится", fontweight="bold", fontsize=13)
fig.tight_layout(rect=(0, 0, 1, 0.93)); save(fig, "hood_02_train.png")

# ============================================================
# 3. Разбор юзера: z → P → вклад ΔP
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.8))
labels = ["полная цепочка 1001:\nмедийка → контекст → бренд",
          "убрали бренд-касание\n(«перехватчик»)",
          "убрали медийку\n(«открыватель»)"]
vals = [10.8, 9.0, 7.2]
cols3 = [NAVY, GREY, ORANGE]
ax.barh([2, 1, 0], vals, color=cols3, height=0.58)
for yy, v in zip([2, 1, 0], vals):
    ax.text(v + 0.18, yy, f"P = {v:.1f}%", va="center", fontsize=11,
            fontweight="bold", color="#16324a")
ax.text(5.6, 2.66, "z = −3.06 + 0.18(медийка) + 0.02(контекст) − 0.07(бренд) + 3×0.27(длина) = −2.12;   P = σ(−2.12) = 10.8%",
        fontsize=9.5, color=NAVY, fontweight="bold", bbox=BB)
ax.text(12.7, 1.55, "вклад брендa = 10.8 − 9.0 = +1.8 п.п.\nстоял рядом, почти не влияя",
        fontsize=9.5, color=GREY, fontweight="bold", bbox=BB, va="center")
ax.text(12.7, 0.45, "вклад медийки = 10.8 − 7.2 = +3.6 п.п.\nудвоила шанс купить",
        fontsize=9.5, color=ORANGE, fontweight="bold", bbox=BB, va="center")
ax.set_yticks([2, 1, 0]); ax.set_yticklabels(labels, fontsize=10.5)
ax.set_xlim(0, 17.4); ax.set_ylim(-0.65, 3.05)
ax.set_xlabel("предсказанная P(конверсия), %")
ax.text(0.5, -0.30, "далее: вклады всех 6000 юзеров суммируем по каналам и делим на 757 конверсий → доли ML (симуляции впереди)",
        transform=ax.transAxes, ha="center", fontsize=9.5, color=GREEN, fontweight="bold")
ax.set_title("Под капотом · шаг 3: вклад касания = ΔP прогноза")
fig.tight_layout(); save(fig, "hood_03_example.png")

print("Готово: 3 картинки в", OUT)
