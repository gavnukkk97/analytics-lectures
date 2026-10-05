# -*- coding: utf-8 -*-
"""Практика 5.1 — Экономика промо: наивная оценка против контрфакта (урок 5.1)."""
from __future__ import annotations
import numpy as np

rng = np.random.default_rng(51)

# %% [markdown]
# Синтетика: акция «−20% на всё» в тест-гео (недели 12–15), контроль без акции.
# Инкремент: +12% заказов в акции (новые/дополнительные), каннибализация 60% акционных.

# %%
N_BASE = 100_000                      # «нормальных» заказов за период в каждом гео
INCIDENT = 0.12                       # инкрементальные заказы (доля от базы)
margin_full, discount = 0.25, 0.20

treated_base = int(N_BASE * (1 + rng.normal(0, 0.01)))
extra = int(treated_base * INCIDENT)                    # появились ИЗ-ЗА акции
full_payers = treated_base - extra                      # купили бы и без акции
cannibal = int(full_payers * 0.60)                      # из них воспользовались скидкой
promo_orders = extra + cannibal
control = int(N_BASE * (1 + rng.normal(0, 0.01)))       # контроль: рост сезона ~0
aov = 1500

# наивная оценка
naive_rev_growth = (treated_base / control - 1)
print(f"НАИВНО: заказы теста vs контроля: +{naive_rev_growth:.1%} → «успех»")

# честная экономика: считаем по слагаемым
d_margin = (extra * aov * (1 - discount) * margin_full          # маржа инкрементальных заказов (они со скидкой)
            - cannibal * aov * discount * margin_full)          # потерянная маржа на каннибализированных
print(f"инкрементных заказов: {extra:,}; каннибализировано: {cannibal:,}")
print(f"Δмаржа акции: {d_margin:,.0f} ₽ "
      f"({d_margin / (promo_orders * aov):+.1%} от оборота акции)")
print("→ выручка «росла», маржа в минусе: классика урока 5.1" if d_margin < 0 else "→ акция окупается")

# %% [markdown]
# Нелинейность: отклик на глубину скидки w: f(w) = 15 + 10w − 4w² (насыщение).

# %%
ws = np.linspace(0, 1.25, 6)
f = 15 + 10 * ws - 4 * ws ** 2
best = ws[f.argmax()]
print(f"\nОтклик по глубине: максимум при w = {best:.2f} → дальше насыщение (парабола Купера)")
print("Практика: тестируйте ГЛУБИНУ и ФОРМУ (порог/каскад/кэшбэк) — это разные кривые ответа.")
