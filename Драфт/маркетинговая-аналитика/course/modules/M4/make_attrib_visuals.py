# -*- coding: utf-8 -*-
"""Визуализации к лекции «Каналы и атрибуция» (модули М3–М4, финальный блок ML).

Запуск: python3 course/modules/M4/make_attrib_visuals.py → images/attrib_*.png
Палитра X5 (navy/orange), заголовок = вывод, числа согласованы с уроками 4.2–4.3.
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

OUT = Path(__file__).resolve().parent / "images"
OUT.mkdir(exist_ok=True)
SEED = 2026

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
# 1. Одна цепочка A→B→C: делёж ценности по 5 моделям
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.6))
models = ["First-click", "Last-click", "Linear", "Time-decay", "U-shaped 40/40/20"]
shares = {  # A, B, C из урока 4.2
    "First-click": [1.00, 0.00, 0.00],
    "Last-click": [0.00, 0.00, 1.00],
    "Linear": [1/3, 1/3, 1/3],
    "Time-decay": [0.15, 0.30, 0.55],
    "U-shaped 40/40/20": [0.40, 0.20, 0.40],
}
colors = [NAVY, GREY, ORANGE]
y = np.arange(len(models))[::-1]
for i, m in enumerate(models):
    left = 0.0
    for j, (v, c) in enumerate(zip(shares[m], colors)):
        ax.barh(y[i], v, left=left, color=c, height=0.62,
                edgecolor="white", lw=1.5)
        if v >= 0.08:
            ax.text(left + v / 2, y[i], f"{v * 100:.0f}%", ha="center", va="center",
                    color="white", fontweight="bold", fontsize=10)
        left += v
ax.set_yticks(y); ax.set_yticklabels(models, fontsize=11)
ax.set_xlim(0, 1.0); ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
ax.set_xlabel("доля ценности конверсии")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c, label=l) for c, l in
                   zip(colors, ["A — медийка (открыл)", "B — контекст (вёл)", "C — бренд (закрыл)"])],
          loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=3, frameon=False)
ax.set_title("Пять моделей — пять дележей одной и той же конверсии")
fig.tight_layout(); save(fig, "attrib_01_chain_models.png")

# ============================================================
# 2. «ЕдаДома»: вклады каналов по 5 моделям (heatmap из урока 4.2)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.8))
cols = ["First", "Last", "Linear", "Time-decay", "U-shaped"]
rows = ["Медийка (просмотры)", "Контекст небренд", "Бренд-контекст",
        "Email/CRM", "Органика/direct"]
data = np.array([
    [28, 4, 16, 9, 20],
    [22, 31, 26, 27, 24],
    [8, 34, 15, 24, 20],
    [3, 18, 13, 17, 8],
    [39, 13, 30, 23, 28],
], dtype=float)
im = ax.imshow(data, cmap="Blues", vmin=0, vmax=42, aspect="auto")
for i in range(len(rows)):
    for j in range(len(cols)):
        v = data[i, j]
        ax.text(j, i, f"{v:.0f}%", ha="center", va="center", fontsize=10.5,
                color="white" if v > 24 else "#0E2841", fontweight="bold")
ax.set_xticks(range(len(cols))); ax.set_xticklabels(cols, fontsize=10.5)
ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows, fontsize=10.5)
ax.set_title("Вывод о канале зависит от модели, а не от канала")
# рамки вокруг «историй» last-click + подпись под графиком вместо стрелок
for (cx, cy) in [(1, 2), (1, 0)]:
    ax.add_patch(plt.Rectangle((cx - 0.5, cy - 0.5), 1, 1, fill=False,
                                edgecolor=ORANGE, lw=2.8, zorder=5))
ax.set_xlabel("оранжевые рамки — как канал выглядит в last-click: бренд «герой», медийка «дармоед»",
              fontsize=10, color=ORANGE, fontweight="bold")
ax.grid(False)
fig.tight_layout(); save(fig, "attrib_02_channels_heat.png")

# ============================================================
# 3. Концепция ML: вклад касания = ΔP (пример из урока 4.3)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4.2))
labels = ["полная цепочка:\nмедийка → контекст → бренд",
          "убрали бренд-касание\n(«перехватчик»)",
          "убрали медийку\n(«открыватель»)"]
vals = [0.081, 0.078, 0.049]
cols3 = [NAVY, GREY, ORANGE]
bars = ax.barh([2, 1, 0], vals, color=cols3, height=0.58)
for yy, v in zip([2, 1, 0], vals):
    ax.text(v + 0.002, yy, f"P = {v:.3f}", va="center", fontsize=11, fontweight="bold",
            color="#0E2841")
ax.text(0.081 / 2, 2.62, "вклад брендa = 0.081 − 0.078 = 0.003 — почти ничего",
        ha="center", fontsize=10, color=GREY, fontweight="bold", bbox=BB)
ax.text(0.049 / 2, -0.62, "вклад медийки = 0.081 − 0.049 = 0.032 — подняла вероятность в разы",
        ha="center", fontsize=10, color=ORANGE, fontweight="bold", bbox=BB)
ax.set_yticks([2, 1, 0]); ax.set_yticklabels(labels, fontsize=10.5)
ax.set_xlim(0, 0.105); ax.set_ylim(-1.0, 3.1)
ax.set_xlabel("предсказанная P(конверсия) — логрегрессия на цепочках касаний")
ax.set_title("Вклад касания = насколько падает прогноз без него")
fig.tight_layout(); save(fig, "attrib_03_dp_concept.png")

# ============================================================
# Симилятор цепочек (как edadoma.make_touches, с ручками) + логрегрессия
# ============================================================
CH = ["display", "search_nb", "email", "search_brand"]
RUS = {"display": "медийка", "search_nb": "контекст небренд",
       "email": "email/CRM", "search_brand": "бренд-контекст"}

def gen_touches(rng, n_users, brand_effect=0.0, brand_end=0.30):
    rows = []
    for uid in range(n_users):
        n_t = int(rng.integers(1, 6))
        seq = list(rng.choice(CH, size=n_t, p=[0.22, 0.33, 0.20, 0.25]))
        if rng.random() < brand_end and seq[-1] != "search_brand":
            seq.append("search_brand")
        has_nb, has_disp = "search_nb" in seq, "display" in seq
        p = (0.02 + 0.05 * has_nb + 0.04 * has_disp + 0.06 * (len(seq) >= 3)
             + 0.03 * seq.count("email") + brand_effect * seq.count("search_brand"))
        conv = rng.random() < min(p, 0.35)
        for pos, ch in enumerate(seq):
            rows.append({"user_id": uid, "position": pos, "channel": ch, "converted": int(conv)})
    return pd.DataFrame(rows)

def fit_attribution(t):
    X = (t.groupby("user_id")["channel"].value_counts().unstack(fill_value=0)
         .reindex(columns=CH, fill_value=0))
    X["n_touches"] = t.groupby("user_id").size()
    y = t.groupby("user_id")["converted"].first()
    def sigmoid(z): return 1 / (1 + np.exp(-np.clip(z, -30, 30)))
    Xa = np.c_[np.ones(len(X)), X.values.astype(float)]
    ya = y.values.astype(float)
    w = np.zeros(Xa.shape[1])
    for _ in range(4000):
        p = sigmoid(Xa @ w)
        w -= 0.1 * (Xa.T @ (p - ya) / len(ya) + 1e-3 * np.r_[0, w[1:]])
    feat = X.values.astype(float); cols = list(X.columns)
    idx_ch = {c: cols.index(c) for c in CH}; idx_n = cols.index("n_touches")
    def p_with(row): return float(sigmoid(np.concatenate([[1.0], row]) @ w))
    contrib = {c: 0.0 for c in CH}
    for row in feat:
        if row.sum() == 0: continue
        p0 = p_with(row)
        for c in CH:
            i = idx_ch[c]
            if row[i] > 0:
                ri = row.copy(); ri[i] -= 1; ri[idx_n] -= 1
                contrib[c] += p0 - p_with(ri)
    total = max(y.sum(), 1)
    ml = {c: contrib[c] / total * 100 for c in CH}
    last = (t.sort_values("position").groupby("user_id")["channel"].last()[y == 1]
            .value_counts(normalize=True) * 100)
    return ml, {c: float(last.get(c, 0.0)) for c in CH}

def share_bars(ax, ml, last, title):
    x = np.arange(len(CH))
    ax.bar(x - 0.2, [last[c] for c in CH], 0.38, color=GREY, label="last-click")
    ax.bar(x + 0.2, [ml[c] for c in CH], 0.38, color=NAVY, label="ML (ΔP)")
    for xi, c in zip(x, CH):
        ax.text(xi - 0.2, last[c] + 1, f"{last[c]:.0f}%", ha="center", fontsize=9.5,
                color="#5a6b7d", fontweight="bold")
        ax.text(xi + 0.2, ml[c] + 1, f"{ml[c]:.0f}%", ha="center", fontsize=9.5,
                color=NAVY, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels([RUS[c] for c in CH], fontsize=10)
    ax.set_ylim(0, 58); ax.set_ylabel("доля конверсий, %")
    ax.legend(frameon=False, loc="upper left")
    ax.set_title(title)

# --- симуляция 1: сильный бренд-перехват (данные практики 4.3) --------------
rng = np.random.default_rng(SEED)
ml1, last1 = fit_attribution(gen_touches(rng, 6000, brand_effect=0.0))
print("sim1 last:", {RUS[c]: round(last1[c]) for c in CH},
      "ml:", {RUS[c]: round(ml1[c]) for c in CH})
fig, ax = plt.subplots(figsize=(10, 4.6))
share_bars(ax, ml1, last1, "Симуляция 1 · бренд только перехватывает: last-click врёт в 4 раза")
ax.text(1.15, 42, "бренд-контекст: 46% в last-click против 12% в ML —\nтреть его «заслуг» — перехват чужих путей; медийка, наоборот,\nнедооценена last-click'ом (её касания без клика он не видит)",
        color=ORANGE, fontsize=9.5, fontweight="bold", ha="left", va="top", bbox=BB)
fig.tight_layout(); save(fig, "attrib_04_sim_intercept.png")

# --- симуляция 2: бренд реально помогает (взял эффект в данные) --------------
rng = np.random.default_rng(SEED + 7)
ml2, last2 = fit_attribution(gen_touches(rng, 6000, brand_effect=0.09))
print("sim2 last:", {RUS[c]: round(last2[c]) for c in CH},
      "ml:", {RUS[c]: round(ml2[c]) for c in CH})
fig, ax = plt.subplots(figsize=(10, 4.6))
share_bars(ax, ml2, last2, "Симуляция 2 · бренд реально помогает: ML это видит")
ax.text(0.98, 0.94, "те же модели, другие данные: доля бренда по ML выросла вдвое.\nРасхождение моделей — не ошибка, а вопрос «что делает канал»",
        transform=ax.transAxes, ha="right", va="top", fontsize=9.5, color=GREEN,
        fontweight="bold", bbox=BB)
fig.tight_layout(); save(fig, "attrib_05_sim_brandworks.png")

# --- симуляция 3: мало данных — ML зашумлён ---------------------------------
rng0 = np.random.default_rng(SEED)
full = gen_touches(rng0, 6000, brand_effect=0.0)
vals = []
all_users = full["user_id"].unique()
for k in range(8):
    rng_k = np.random.default_rng(500 + k)
    chosen = rng_k.choice(all_users, size=max(int(0.07 * len(all_users)), 50), replace=False)
    part = full[full["user_id"].isin(chosen)]
    ml_k, last_k = fit_attribution(part)
    vals.append(ml_k["search_brand"])
print("sim3 ml brand по подвыборкам:", [f"{v:.0f}" for v in vals])
ml_full, last_full = fit_attribution(full)
fig, ax = plt.subplots(figsize=(10, 4.6))
ax.scatter(range(1, 9), vals, s=90, color=NAVY, zorder=5, label="ML (ΔP) на подвыборках ~7% данных")
ax.axhline(ml_full["search_brand"], color=NAVY, lw=2, ls="--",
           label=f"ML на полных данных: {ml_full['search_brand']:.0f}%")
ax.axhline(last_full["search_brand"], color=ORANGE, lw=2,
           label=f"last-click: {last_full['search_brand']:.0f}% (стабилен, но слеп)")
for k, v in enumerate(vals, 1):
    ax.text(k, v + 1.3, f"{v:.0f}%", ha="center", fontsize=9.5, color=NAVY, fontweight="bold")
ax.set_xticks(range(1, 9)); ax.set_xlabel("случайная подвыборка (мало конверсий)")
ax.set_ylabel("доля бренд-контекста, %")
ax.set_ylim(0, 55)
ax.legend(frameon=False, loc="upper right", fontsize=9)
ax.set_title("Симуляция 3 · мало данных: ML скачет — проверяйте устойчивость")
fig.tight_layout(); save(fig, "attrib_06_sim_smalldata.png")

print("Готово: 6 картинок в", OUT)
