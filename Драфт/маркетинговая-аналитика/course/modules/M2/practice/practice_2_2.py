# -*- coding: utf-8 -*-
"""Практика 2.2 — Когортный анализ и виды retention (кейс «ЕдаДома»).

Что делаем:
1) Генерируем лайф-цикл: регистрации по неделям и каналам, заказы с гетерогенной
   «привычностью» (ядро + случайные пользователи).
2) Когортная таблица retention (classic) + heatmap.
3) Classic vs unbounded vs bracket на одной когорте.
4) Ошибка новичка: календарный расчёт без вычета новичков.
5) Срез retention по каналам (W1 vs плато).

Запуск: python3 course/modules/M2/practice/practice_2_2.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

rng = np.random.default_rng(22)
OUT = Path(__file__).resolve().parents[1] / "images"
OUT.mkdir(exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.grid": True, "grid.alpha": 0.25, "figure.facecolor": "white",
})
C_MAIN, C_ACC, C_TRUE, C_BAD = "#4C72B0", "#DD8452", "#55A868", "#C44E52"

WEEKS = 26
CHANNELS = {"context": 0.42, "bloggers": 0.33, "organic": 0.25}  # доли трафика
# качество каналов: (доля ядра, p возвращения ядра, p второго заказа случайных)
QUALITY = {
    "context":  (0.24, 0.55, 0.10),
    "bloggers": (0.20, 0.50, 0.06),
    "organic":  (0.30, 0.60, 0.08),
}

# %% [markdown]
# Шаг 1. Синтетические регистрации и заказы.

# %%
reg_rows = []
for w in range(WEEKS):
    n_new = int(rng.normal(1500, 120))
    for ch, share in CHANNELS.items():
        n_ch = rng.multinomial(n_new, list(CHANNELS.values()))
        reg_rows.append({"week": w, "channel": ch, "n": n_ch[list(CHANNELS).index(ch)]})
reg = pd.DataFrame([{"week": w, "channel": ch, "n": n}
                    for w in range(WEEKS)
                    for ch, n in zip(CHANNELS,
                                     rng.multinomial(int(rng.normal(1500, 120)),
                                                     list(CHANNELS.values())))])
reg["user_id"] = np.arange(len(reg))
reg = reg.loc[reg.index.repeat(reg["n"])].reset_index(drop=True)
reg["user_id"] = np.arange(len(reg))
print("пользователей:", len(reg), "| по каналам:\n", reg["channel"].value_counts(), sep="")

# заказы: у каждого юзера биполярная «привычность»
order_rows = []
for ch, (p_core, p_core_ret, p_rand) in QUALITY.items():
    ch_users = reg[reg["channel"] == ch]
    is_core = rng.random(len(ch_users)) < p_core
    for (uid, w0), core in zip(ch_users[["user_id", "week"]].itertuples(index=False), is_core):
        weeks_alive = np.arange(w0, WEEKS)
        p_alive = np.where(core, p_core_ret, p_rand * np.exp(-(weeks_alive - w0) / 2.5))
        active = rng.random(len(weeks_alive)) < p_alive
        for w in weeks_alive[active]:
            order_rows.append({"user_id": uid, "order_week": int(w)})
orders = pd.DataFrame(order_rows)
print("заказов:", len(orders))

# %%
# первая активность = неделя регистрации (W0): гарантируем заказ в неделю входа
first = orders.groupby("user_id")["order_week"].min().rename("first_order")
reg = reg.merge(first, left_on="user_id", right_index=True, how="left")
# часть пользователей «зарегистрировалась и не купила» — так и в жизни; оставляем их в когорте

# %% [markdown]
# Шаг 2. Когортная таблица retention (classic) + heatmap.

# %%
df = orders.merge(reg[["user_id", "week", "channel"]], on="user_id")
df["age"] = df["order_week"] - df["week"]
pt = df.pivot_table(index="week", columns="age", values="user_id",
                    aggfunc=pd.Series.nunique)
cohort_size = reg.groupby("week")["user_id"].nunique()
ret = pt.div(cohort_size, axis=0)

fig, ax = plt.subplots(figsize=(9.5, 6.5))
im = ax.imshow(ret.values * 100, cmap="Blues", aspect="auto", vmin=0, vmax=45)
ax.set_xlabel("возраст когорты, недель (W0 = неделя регистрации)")
ax.set_ylabel("когорта (неделя регистрации)")
ax.set_title("Когортная таблица retention (classic): каждая строка — своя когорта")
for i in range(ret.shape[0]):
    for j in range(ret.shape[1]):
        if not np.isnan(ret.values[i, j]):
            v = ret.values[i, j] * 100
            ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                    fontsize=7, color="white" if v > 28 else "#333")
fig.colorbar(im, label="retention, %")
fig.tight_layout()
fig.savefig(OUT / "practice_2_2_cohorts.png", bbox_inches="tight")
print("W1 retention по последним когортам:", (ret[1].tail(5) * 100).round(1).tolist())

# %% [markdown]
# Шаг 3. Три вида retention на одной когорте.

# %%
target_cohort = 10
co = df[df["week"] == target_cohort]
size = cohort_size[target_cohort]
ages = np.arange(0, WEEKS - target_cohort)
classic = np.array([(co["age"] == a).sum() / size for a in ages])
unbounded = np.array([co.loc[co["age"] <= a, "user_id"].nunique() / size for a in ages])
W = 4  # bracket-окно
bracket = np.array([co.loc[(co["age"] > a - W) & (co["age"] <= a), "user_id"].nunique() / size
                    for a in ages])

fig, ax = plt.subplots(figsize=(8.6, 4.6))
ax.plot(ages, classic * 100, label="classic (ровно в неделю N)", color=C_MAIN, lw=2)
ax.plot(ages, unbounded * 100, label="unbounded (хотя бы раз до N)", color=C_TRUE, lw=2)
ax.plot(ages[W:], bracket[W:] * 100, label=f"bracket (окно {W} нед.)", color=C_ACC, lw=2, ls="--")
ax.set_xlabel("возраст когорты, недель")
ax.set_ylabel("retention, %")
ax.set_title(f"Три вида retention на одной когорте: unbounded в ~{unbounded[4]/classic[4]:.1f} раза «оптимистичнее» classic")
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "practice_2_2_retention_types.png", bbox_inches="tight")
print(f"W4: classic={classic[4]:.0%}, unbounded={unbounded[4]:.0%}")

# %% [markdown]
# Шаг 4. Ошибка новичка: календарный расчёт без вычета новичков.

# %%
# «retention» как доля активных недели w, кто активен на w+1 — НЕ вычитая новичков
cal_rows = []
for w in range(WEEKS - 1):
    a0 = set(df.loc[df["order_week"] == w, "user_id"])
    a1 = set(df.loc[df["order_week"] == w + 1, "user_id"])
    if a0:
        cal_rows.append(a0 & a1 and len(a0 & a1) / len(a0) or 0)
cal = np.nanmean(cal_rows)
# честный unbounded для сравнения — усредним по когортам полного возраста
fair = ret[1].mean()
print(f"календарный «retention» без вычета новичков: {cal:.0%}")
print(f"честный classic W1 по когортам:             {fair:.0%}")
print("→ завышение из-за притока новичков:", f"{cal/fair:.1f}x")

# %% [markdown]
# Шаг 5. Срез по каналам: W1 против плато.

# %%
fig, ax = plt.subplots(figsize=(8.6, 4.6))
for ch, color in zip(CHANNELS, [C_MAIN, C_ACC, C_TRUE]):
    d = df[df["channel"] == ch]
    p = d.pivot_table(index="week", columns="age", values="user_id",
                      aggfunc=pd.Series.nunique).div(
        reg[reg["channel"] == ch].groupby("week")["user_id"].nunique(), axis=0)
    ax.plot(p.mean(axis=0) * 100, label=ch, color=color, lw=2)
ax.set_xlabel("возраст когорты, недель")
ax.set_ylabel("retention, % (среднее по когортам)")
ax.set_title("Срез по каналам: у блогеров ниже W1, но плато почти одинаковое")
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "practice_2_2_channels.png", bbox_inches="tight")

print("\nВыводы: см. урок 2.2 «Разбор на данных». Графики в", OUT)
