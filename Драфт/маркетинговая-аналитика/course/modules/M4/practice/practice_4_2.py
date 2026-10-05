# -*- coding: utf-8 -*-
"""Практика 4.2 — Пять моделей атрибуции на одних цепочках касаний (урок 4.2)."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import edadoma as E

rng = np.random.default_rng(E.SEED)
t = E.make_touches(4000, rng)
conv = t[t["converted"] == 1]
chains = conv.groupby("user_id")["channel"].apply(list)
n_conv = len(chains)
print(f"конверсий: {n_conv:,} | средняя длина цепочки: {chains.str.len().mean():.1f}\n")

def linear(ch): return {c: 1 / len(ch) for c in ch}
def first(ch):  return {ch[0]: 1.0}
def last(ch):   return {ch[-1]: 1.0}
def u_shape(ch):
    w = {c: 0.0 for c in ch}
    if len(ch) == 1: return {ch[0]: 1.0}
    w[ch[0]] += 0.4; w[ch[-1]] += 0.4
    mid = 0.2 / max(len(ch) - 2, 1)
    for c in ch[1:-1]: w[c] += mid
    return w
def time_decay(ch, half=7.0):
    n = len(ch)
    raw = [2 ** (-max(0, n - 1 - i) / 1.0) for i in range(n)]
    s = sum(raw)
    return {c: raw[i] / s for i, c in enumerate(ch)}

models = {"first": first, "last": last, "linear": linear, "U-shaped": u_shape, "time-decay": time_decay}
table = pd.DataFrame(0.0, index=models, columns=sorted(t["channel"].unique()))
for name, fn in models.items():
    for ch in chains:
        for c, w in fn(ch).items():
            table.loc[name, c] += w
share = table.div(table.sum(axis=1), axis=0) * 100
print("Доли конверсий по каналам, %:")
print(share.round(1).to_string())

d = share.copy()
print("\nДиагностика ролей (урок 4.2):")
for ch in share.columns:
    spread = d.loc["first", ch] - d.loc["last", ch]
    role = "ОТКРЫВАТЕЛЬ (верх воронки)" if spread > 8 else \
           "ЗАКРЫВАТЕЛЬ/перехватчик" if spread < -8 else "середина пути"
    print(f"  {ch:13}: first {d.loc['first', ch]:4.1f}% vs last {d.loc['last', ch]:4.1f}% → {role}")
print("\nМораль: last-click систематически отдаёт конверсии бренд-поиску (перехват),")
print("а 'бесплатным дармоедом' делает display — канал, который только открывает пути.")
