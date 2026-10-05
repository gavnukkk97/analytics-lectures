# -*- coding: utf-8 -*-
"""Практика 6.1 — Симуляция многоканального хаоса: 5 команд, капы, метрики (урок 6.1)."""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "images"; OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(61)

N = 100_000          # пользователей
WEEKS = 8

# %% [markdown]
# Шаг 1. Хаос: 5 команд независимо шлют сообщения (в среднем по 1,2 на юзера каждая).

# %%
freq = np.zeros((N, WEEKS))
for team in range(5):
    freq += rng.random((N, WEEKS)) < 0.30
per_user = freq.sum(axis=1)
print(f"ХАОС: средняя частота {per_user.mean():.1f} касаний/нед; "
      f"топ-10% получают {np.quantile(per_user, 0.9):.0f}+/нед")

# %% [markdown]
# Шаг 2. Кривая усталости: отклик падает с частотой, отписки растут.

# %%
def response(f):  # CTR сообщения при частоте f
    return np.clip(0.045 * np.exp(-0.18 * np.maximum(f - 1, 0)) + 0.008, 0.008, None)
def unsub(f):     # недельная вероятность отписки
    return np.clip(0.004 + 0.0035 * np.maximum(f - 3, 0) ** 1.3, 0.004, 0.12)

clicks_chaos = float(np.sum(response(freq) * freq))
unsub_chaos = float(np.mean(unsub(per_user)))

# %% [markdown]
# Шаг 3. Оркестрация: суммарный кап 5/нед с приоритетом (беру 5 «лучших» слотов).

# %%
cap = 5
freq_capped = np.minimum(freq, cap)
per_user_c = freq_capped.sum(axis=1)
clicks_cap = float(np.sum(response(freq_capped) * freq_capped))
unsub_cap = float(np.mean(unsub(per_user_c)))

print(f"\nКАП {cap}/нед: касаний −{(1 - freq_capped.sum()/freq.sum()):.0%}, "
      f"кликов −{(1 - clicks_cap/clicks_chaos):.1%} (почти не потеряли)")
print(f"отписки: {unsub_chaos:.1%} → {unsub_cap:.1%} ({(unsub_cap/unsub_chaos-1):+.0%})")

# %% [markdown]
# Шаг 4. Holdout полной тишины: 2% юзеров без коммуникаций — «а нужны ли они вообще».

# %%
# (симметричный пример: у «тихих» retention чуть ниже, но выручка на юзера сопоставима)
quiet_lift = rng.normal(0.004, 0.002)
print(f"\nHOLDOUT ТИШИНЫ: разница выручки/юзера «тихих» против остальных: {quiet_lift:+.1%}"
      " → коммуникации почти не создают ценности, если |эффект| мал: проверяйте своим holdout'ом")

# %%
fig, ax = plt.subplots(figsize=(8.2, 4.3))
fs = np.arange(0, 16)
ax.plot(fs, response(fs) * 100, color="#4C72B0", lw=2, label="CTR сообщения, %")
ax2 = ax.twinx()
ax2.plot(fs, unsub(fs) * 100, color="#C44E52", lw=2, ls="--", label="отписки/нед, %")
ax.axvline(5, color="#55A868", ls=":", lw=2)
ax.text(5.2, 0.16, "кап 5/нед", color="#2d6a4f")
ax.set_xlabel("касаний в неделю на юзера"); ax.set_ylabel("CTR, %"); ax2.set_ylabel("отписки, %")
ax.set_title("Кривая усталости: после 5–6 касаний клики тают, отписки растут")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="center right")
fig.tight_layout(); fig.savefig(OUT / "practice_6_1_fatigue.png", bbox_inches="tight")
print("\nГрафик: practice_6_1_fatigue.png")
