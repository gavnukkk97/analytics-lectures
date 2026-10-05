# -*- coding: utf-8 -*-
"""Практика 5.3 — Аллокация бюджета: средний vs маржинальный CAC (урок 5.3)."""
from __future__ import annotations
import numpy as np

rng = np.random.default_rng(53)

# Кривые насыщения каналов: новые_клиенты(x) = cap * (1 − exp(−k·x)), x — млн ₽
CHANNELS = {
    "контекст":    {"cap": 40_000, "k": 0.28, "ltv": 1900},
    "таргет":      {"cap": 30_000, "k": 0.30, "ltv": 1500},
    "блогеры":     {"cap": 12_000, "k": 0.45, "ltv": 2100},
    "рефералка":   {"cap": 20_000, "k": 0.20, "ltv": 1800},
}
BUDGET = 10.0  # млн ₽

def customers(ch, x):  # x млн ₽ → клиентов
    return ch["cap"] * (1 - np.exp(-ch["k"] * x))

# %% [markdown]
# Шаг 1. Текущая раскладка «по среднему CAC лучшего канала»: всё в контекст.

# %%
x_now = {"контекст": BUDGET, "таргет": 0, "блогеры": 0, "рефералка": 0}
for name, x in x_now.items():
    n = customers(CHANNELS[name], x)
    print(f"{name:10}: {n:8,.0f} клиентов | средний CAC {x*1e6/n:6.0f} ₽")
n_now = sum(customers(CHANNELS[c], x) for c, x in x_now.items())

# %% [markdown]
# Шаг 2. Жадная аллокация по МАРЖИНАЛЬНОМУ CAC: шагами по 0,5 млн.

# %%
x = {c: 0.0 for c in CHANNELS}
step = 0.5
marginal_cac = lambda name, x0: (step * 1e6) / max(customers(CHANNELS[name], x0 + step)
                                                   - customers(CHANNELS[name], x0), 1)
for _ in range(int(BUDGET / step)):
    best = max(CHANNELS, key=lambda c: CHANNELS[c]["ltv"] / max(marginal_cac(c, x[c]), 1))
    x[best] += step

print("\nОптимум по маржиналам:")
total_ltv = 0
for name, xi in x.items():
    n = customers(CHANNELS[name], xi)
    mcac = marginal_cac(name, xi - step)
    total_ltv += n * CHANNELS[name]["ltv"]
    print(f"{name:10}: {xi:4.1f} млн → {n:7,.0f} клиентов | марж. CAC на краю ≈ {mcac:6.0f} ₽")
n_opt = sum(customers(CHANNELS[c], xi) for c, xi in x.items())
print(f"\nитого клиентов: «всё в контекст» {n_now:,.0f} vs аллокация {n_opt:,.0f} "
      f"({n_opt/n_now-1:+.1%} при том же бюджете)")
print(f"марж. LTV/CAC на краях уравнены ≈ {total_ltv and CHANNELS['контекст']['ltv']/marginal_cac('контекст', x['контекст']-step):.2f}")

# %% [markdown]
# Шаг 3. Инкрементальная поправка: у таргета треть атрибуционного эффекта — самоперехват.

# %%
CHANNELS["таргет"]["k"] *= 0.67  # реальный вклад ниже атрибуционного
x2 = {c: 0.0 for c in CHANNELS}
for _ in range(int(BUDGET / step)):
    best = max(CHANNELS, key=lambda c: CHANNELS[c]["ltv"] / max(marginal_cac(c, x2[c]), 1))
    x2[best] += step
shift = {c: x2[c] - x[c] for c in CHANNELS if abs(x2[c] - x[c]) > 1e-9}
print("\nПосле инкрементальной поправки таргета переток:", {c: f"{d:+.1f} млн" for c, d in shift.items()})
print("Мораль урока 5.3: realloc — по маржиналам и инкрементальности, не по отчётам атрибуции.")
