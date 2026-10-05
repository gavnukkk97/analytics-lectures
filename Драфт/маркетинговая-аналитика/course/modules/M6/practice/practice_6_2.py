# -*- coding: utf-8 -*-
"""Практика 6.2 — Мини-репертуарная решётка: триады → матрица → карта восприятия (урок 6.2)."""
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
grid = E.make_grid(12)

# %% [markdown]
# Шаг 1. Матрица решётки: элементы × конструкты (средние по респондентам, 1 = первый полюс).

# %%
piv = grid.pivot_table(index="element", columns="construct", values="rating").round(2)
print(piv.to_string(), "\n")

# %% [markdown]
# Шаг 2. «Анализ» решётки: какие конструкты различают элементы (дисперсия = информативность),
# и корреляции конструктов (похожие оси можно объединить).

# %%
info = piv.var(axis=0).sort_values(ascending=False)
print("Информативность конструктов (дисперсия оценок):")
print(info.round(2).to_string(), "\n")
corr = piv.corr().round(2)
print("Корреляции конструктов (|r|>0.7 — оси дублируют друг друга):")
print(corr.to_string(), "\n")

# %% [markdown]
# Шаг 3. Карта восприятия: два самых информативных конструкта как оси.

# %%
c1, c2 = info.index[0], info.index[1]
fig, ax = plt.subplots(figsize=(7.6, 5.6))
xs, ys = piv[c1], piv[c2]
ax.scatter(xs, ys, s=160, color="#4C72B0")
for el in piv.index:
    ax.annotate(el, (xs[el], ys[el]), xytext=(7, 5), fontsize=11)
ax.axvline(4, color="grey", ls=":"); ax.axhline(4, color="grey", ls=":")
ax.set_xlabel(f"{c1}  (1 ← полюс → 7)")
ax.set_ylabel(f"{c2}  (1 ← полюс → 7)")
ax.invert_xaxis()  # чтобы «хорошие» полюса (1) смотрели вправо-вверх
ax.set_title("Карта восприятия рынка: оси из самих респондентов (решётка Келли)")
fig.tight_layout(); fig.savefig(OUT / "practice_6_2_grid_map.png", bbox_inches="tight")

empty = "позиция, где нет ни одного бренда (право-верх) — свободна" \
        if not ((xs < 3) & (ys < 3)).sum() else "занята"
print(f"Оси карты: «{c1}» × «{c2}». Клетка «оба хороших полюса» — {empty}.")
print("Идеал всегда в хорошем углу; сравните, кто ближе всех к нему — и кто дальше.")
print("\nГрафик: practice_6_2_grid_map.png")
