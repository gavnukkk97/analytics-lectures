# -*- coding: utf-8 -*-
"""Практика 3.3 — Пик-анализ брендовых запросов и гео-DiD немаркируемых кампаний (урок 3.3)."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import edadoma as E

OUT = Path(__file__).resolve().parents[1] / "images"; OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(E.SEED + 9)
WEEKS = 26

# %% [markdown]
# Шаг 1. Пик-анализ: брендовые запросы вокруг вылетов ТВ (недели 10 и 18).

# %%
base = 4000 * (1 + 0.002 * np.arange(WEEKS))            # тренд
season = 400 * np.sin(np.arange(WEEKS) / 13)            # лёгкая сезонность
tv = np.zeros(WEEKS)
for launch, spike in [(10, 0.42), (18, 0.35)]:          # два вылета с затуханием
    for k in range(6):
        if launch + k < WEEKS:
            tv[launch + k] += spike * np.exp(-k / 2.2)
brand = base + season + tv * base + rng.normal(0, 90, WEEKS)
print(f"брендовые запросы: неделя 9 (до) = {brand[9]:,.0f}, неделя 11 (пик) = {brand[11]:,.0f} "
      f"({brand[11]/brand[9]-1:+.0%})")
print("затухание к неделе +4 после вылета:", f"{(brand[14]/brand[11]-1):+.0%}")

# %% [markdown]
# Шаг 2. Гео-DiD: новые пользователи/10к жителей, пилот (ТВ) против контроля.

# %%
n_t, n_c = 6_000_000, 9_000_000                          # население пилот/контрольных гео
pre_t, pre_c = 62.0, 61.5                                # новых на 10к/нед до
growth = 1.0 + 0.04 + 0.002 * np.arange(12)              # общий рост рынка
post_t = (pre_t * growth) * (1 + 0.11)                   # + эффект ТВ 11%
post_c = pre_c * growth
did = float(np.mean((post_t - pre_t) - (post_c - pre_c)))
extra_new = did * (n_t / 10_000) * 12                    # за 12 недель
spend = 18_000_000
print(f"DiD = {did:.1f} новых/10к/нед → приростных новых за 12 нед: {extra_new:,.0f}")
print(f"«CAC ТВ» = расходы/прирост = {spend/extra_new:,.0f} ₽")
naive = float(np.mean(pre_t * growth * (1 + 0.11)) - pre_t)
print(f"без контроля наивная оценка завысила бы эффект: {naive / did:.1f}×")

# %%
fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].plot(brand, color="#4C72B0", lw=2)
for l in (10, 18): axes[0].axvline(l, color="#C44E52", ls="--", lw=1.5)
axes[0].set_title("Пик-анализ: брендовые запросы; пунктир — вылеты ТВ")
axes[0].set_xlabel("неделя"); axes[0].set_ylabel("запросов/нед")
wk = np.arange(-6, 12)
axes[1].plot(wk, np.r_[np.full(6, pre_t), post_t], label="пилот (ТВ)", color="#DD8452", lw=2)
axes[1].plot(wk, np.r_[np.full(6, pre_c), post_c], label="контроль", color="#4C72B0", lw=2)
axes[1].axvline(0, color="grey", ls=":"); axes[1].set_title("Гео-DiD: разность разностей")
axes[1].set_xlabel("недели от запуска"); axes[1].legend()
fig.tight_layout(); fig.savefig(OUT / "practice_3_3_tv.png", bbox_inches="tight")
print("\nГрафик: practice_3_3_tv.png")
