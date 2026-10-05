# -*- coding: utf-8 -*-
"""Практика 2.1 — Карта метрик: дерево GMV и декомпозиция (урок 2.1).

Запуск: python3 course/modules/M2/practice/practice_2_1.py
"""
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

reg = E.make_registrations(26, rng)
orders = E.make_orders(reg, 26, rng)

# %% [markdown]
# Шаг 1. Декомпозиция GMV по месяцам: MAU × заказы/юзер × средний чек.

# %%
df = orders.copy()
df["month"] = df["order_week"] // 4
g = df.groupby("month").agg(orders=("user_id", "count"),
                            users=("user_id", "nunique"),
                            gmv=("revenue", "sum"))
g["orders_per_user"] = g["orders"] / g["users"]
g["aov"] = g["gmv"] / g["orders"]
print(g.round(2).to_string())

# вклад сомножителей в изменение GMV (месяц 6 против 3)
def decomp(a, b):
    dg = b.gmv / a.gmv - 1
    d_m = b.orders_per_user / a.orders_per_user - 1
    d_a = b.aov / a.aov - 1
    return dg, d_m, d_a
dg, dop, daov = decomp(g.loc[3], g.loc[6])
print(f"\nΔGMV мес6/мес3 = {dg:+.1%} | раскладка: заказы/юзер {dop:+.1%}, чек {daov:+.1%}")

# %%
# (пользователи растут с registries — добавим их в декомпозицию для полноты)
mau = df.groupby("month")["user_id"].nunique()
print(f"MAU мес3={mau[3]:,} → мес6={mau[6]:,} ({mau[6]/mau[3]-1:+.1%})")

# %% [markdown]
# Шаг 2. Ловушка Гудхарта: «оптимизируем» CTR баннера — и смотрим контр-метрию.

# %%
n = 200_000
see_old, see_new = rng.random(n) < 0.30, rng.random(n) < 0.42   # показы
click_old = see_old & (rng.random(n) < 0.020)                    # честный баннер
click_new = see_new & (rng.random(n) < 0.028)                    # кликбейт: CTR выше
conv_old = click_old & (rng.random(n) < 0.35)                   # конверсия клика в заказ
conv_new = click_new & (rng.random(n) < 0.18)                    # но качество клика хуже
print(f"старый: CTR={click_old.sum()/see_old.sum():.2%}, CR={conv_old.sum()/click_old.sum():.0%}")
print(f"новый:  CTR={click_new.sum()/see_new.sum():.2%}, CR={conv_new.sum()/click_new.sum():.0%}")
print(f"заказов: старый {conv_old.sum()} vs новый {conv_new.sum()} → "
      f"{'Гудхарт: кликов больше, заказов меньше' if conv_new.sum() < conv_old.sum() else 'ок'}")

fig, ax = plt.subplots(figsize=(8, 4.2))
x = np.arange(2)
ax.bar(x - 0.18, [click_old.sum()/see_old.sum()*100, click_new.sum()/see_new.sum()*100],
       0.34, label="CTR, %", color="#4C72B0")
ax.bar(x + 0.18, [conv_old.sum()/see_old.sum()*100, conv_new.sum()/see_new.sum()*100],
       0.34, label="заказы на показ, %", color="#DD8452")
ax.set_xticks(x); ax.set_xticklabels(["честный баннер", "кликбейт"])
ax.set_title("Гудхарт: CTR вырос — заказы на показ упали")
ax.legend()
fig.tight_layout(); fig.savefig(OUT / "practice_2_1_goodhart.png", bbox_inches="tight")
print("\nВыводы — в уроке 2.1. График: practice_2_1_goodhart.png")
