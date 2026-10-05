# -*- coding: utf-8 -*-
"""Практика 2.3 — LTV четырьмя способами на когортах «ЕдаДома» (урок 2.3)."""
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
rng = np.random.default_rng(E.SEED)
reg, orders = E.make_registrations(26, rng), None
orders = E.make_orders(reg, 26, rng)
o = orders.merge(reg[["user_id", "week"]].rename(columns={"week": "reg_week"}), on="user_id")
o["age"] = o["order_week"] - o["reg_week"]

# %% [markdown]
# Шаг 1. Способ 3 (когортный факт): накопленная маржа когорт по возрасту.

# %%
T = 12
ages = np.arange(T)
curve = np.array([o[(o["reg_week"] < 26 - T) & (o["age"] == a)]["margin"].sum() /
                  reg[reg["week"] < 26 - T]["user_id"].nunique() for a in ages])
ltv_fact12 = curve.sum()
print(f"LTV12 когортный факт: {ltv_fact12:,.0f} ₽ (недозревшие когорты исключены)")

# %% [markdown]
# Шаг 2. Способ 1 (прикидка): ARPU(мес) × lifetime × маржа — lifetime из retention.

# %%
act = o.groupby(["user_id", "age"]).size().reset_index()
size = reg["user_id"].nunique()
ret = np.array([(act["age"] == a).sum() / size for a in range(26)])
lifetime = ret.sum() / 4  # недельный retention → месяцы
arpu_month = orders["revenue"].sum() / size / (26 / 4)
ltv_quick = arpu_month * lifetime * 0.25
print(f"LTV прикидка: ARPU {arpu_month:,.0f} ₽/мес × lifetime {lifetime:.1f} мес × 25% = {ltv_quick:,.0f} ₽")

# %% [markdown]
# Шаг 3. Способ 4 (прогноз): факт 12 нед + хвост по форме зрелых когорт.

# %%
mature = o[o["reg_week"] < 10]
mcurve = np.array([mature[mature["age"] == a]["margin"].sum() /
                   reg[reg["week"] < 10]["user_id"].nunique() for a in range(26)])
scale = curve[8] / mcurve[8]  # калибровка хвоста по последним общим точкам
tail = mcurve[T:] * scale
ltv_forecast = ltv_fact12 + tail.sum()
print(f"LTV прогноз 26 нед: {ltv_forecast:,.0f} ₽ (факт 12 нед {ltv_fact12:,.0f} + хвост {tail.sum():,.0f})")

# %% [markdown]
# Шаг 4. Способ 2 (юнит) + сравнение и решение по CAC.

# %%
CAC = 480
ltv_unit = ltv_forecast - CAC
print(f"\nЮнит-прибыль: LTV {ltv_forecast:,.0f} − CAC {CAC} = {ltv_unit:,.0f} ₽ | LTV/CAC = {ltv_forecast/CAC:.2f}")

fig, ax = plt.subplots(figsize=(8.4, 4.4))
ax.plot(np.arange(1, T + 1), np.cumsum(curve), label="факт (когортный)", lw=2, color="#4C72B0")
ax.plot(np.arange(1, 27), np.cumsum(np.r_[curve, tail]), label="прогноз (с хвостом)", lw=2, color="#55A868", ls="--")
ax.axhline(ltv_quick, color="#DD8452", ls=":", lw=2, label=f"прикидка ({ltv_quick:,.0f} ₽)")
ax.axhline(3 * CAC, color="#C44E52", ls=":", lw=1.5, label=f"порог 3×CAC ({3*CAC} ₽)")
ax.set_xlabel("возраст когорты, недель"); ax.set_ylabel("накопленная маржа, ₽")
ax.set_title("LTV тремя способами: прикидка, факт, прогноз — и порог 3×CAC")
ax.legend()
fig.tight_layout(); fig.savefig(OUT / "practice_2_3_ltv.png", bbox_inches="tight")
print("\nГрафик: practice_2_3_ltv.png. Выводы о расхождениях способов — урок 2.3.")
