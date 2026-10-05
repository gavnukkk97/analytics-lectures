# -*- coding: utf-8 -*-
"""Практика 4.3 — Мини-модель ML-атрибуции: вклад касания = ΔP(конверсии) (урок 4.3)."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import edadoma as E

rng = np.random.default_rng(E.SEED)
t = E.make_touches(6000, rng)
CH = ["display", "search_nb", "email", "search_brand"]

# фичи: счётчики касаний по каналам + длина пути
X = pd.get_dummies(t.groupby("user_id")["channel"].value_counts().unstack(fill_value=0)
                   .reindex(columns=CH, fill_value=0))
X["n_touches"] = t.groupby("user_id").size()
y = t.groupby("user_id")["converted"].first()

# логрегрессия «вручную» (градиентный спуск), без sklearn
def sigmoid(z): return 1 / (1 + np.exp(-z))
Xa = np.c_[np.ones(len(X)), X.values]
ya = y.values.astype(float)
w = np.zeros(Xa.shape[1])
for _ in range(4000):
    p = sigmoid(Xa @ w)
    grad = Xa.T @ (p - ya) / len(ya) + 1e-3 * np.r_[0, w[1:]]
    w -= 0.1 * grad
names = ["intercept"] + list(X.columns)
print("модель P(конверсия | цепочка): обучена (логрегрессия, вручную)")
print(f"AUC-прокси: средний P у конвертировавших {sigmoid(Xa[ya==1]@w).mean():.3f} "
      f"vs у остальных {sigmoid(Xa[ya==0]@w).mean():.3f}\n")

feat = X.values.astype(float)              # колонки: каналы + n_touches
cols = list(X.columns)
idx_ch = {c: cols.index(c) for c in CH}
idx_n = cols.index("n_touches")

def p_with(row):
    x = np.concatenate([[1.0], row]); return float(sigmoid(x @ w))

# вклад канала = суммарная ΔP при удалении одного касания (канал −1, длина пути −1)
contrib = {c: 0.0 for c in CH}
for row in feat:
    if row.sum() == 0: continue
    p0 = p_with(row)
    for c in CH:
        i = idx_ch[c]
        if row[i] > 0:
            row_i = row.copy(); row_i[i] -= 1; row_i[idx_n] -= 1
            contrib[c] += p0 - p_with(row_i)
total_conv = y.sum()
ml_share = {c: contrib[c] / total_conv * 100 for c in CH}

# last-click для сравнения
last = t.sort_values("position").groupby("user_id")["channel"].last()
last_share = last[y == 1].value_counts(normalize=True) * 100

print(f"{'канал':13} | {'ML (ΔP), %':>10} | {'last-click, %':>12}")
print("-" * 45)
for c in CH:
    print(f"{c:13} | {ml_share[c]:10.1f} | {last_share.get(c, 0):12.1f}")

print("\nЧтение: бренд-поиск в last-click — фаворит (46%!), а в ML-атрибуции — 12%:")
print("треть его «заслуг» — перехват чужих путей; display, наоборот, недооценён last-click'ом.")
print("Граница: это корреляционная модель — «что, если отключить» проверяет только гео-тест (урок 5.3).")
