# -*- coding: utf-8 -*-
"""Генерация датасета капстоуна (урок 7.3) из общего генератора курса.

Запуск: python3 course/capstone/generate_capstone.py
Выход: course/capstone/data/*.csv (+ README-описание в README.md урока).
"""
from __future__ import annotations
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
import edadoma as E

OUT = Path(__file__).resolve().parent / "data"
OUT.mkdir(exist_ok=True)

rng = np.random.default_rng(E.SEED)

# 1) регистрации и заказы (26 недель)
reg = E.make_registrations(weeks=26, rng=rng)
orders = E.make_geo_pilot(reg, weeks=26, effect=0.06, rng=rng)

# для капстоуна: открытые ответы только b2b-сегмента (симулируем «офисных»),
# решётка — про обеденный рынок
open_ends = E.make_open_ends(n=300, rng=np.random.default_rng(E.SEED + 40))
grid = E.make_grid(n_resp=10, rng=np.random.default_rng(E.SEED + 41))

reg.to_csv(OUT / "registrations.csv", index=False)
orders.to_csv(OUT / "orders.csv", index=False)
open_ends.to_csv(OUT / "open_ends.csv", index=False)
grid.to_csv(OUT / "grid.csv", index=False)

print("данные капстоуна:")
for f in sorted(OUT.glob("*.csv")):
    print(f"  {f.name}: {sum(1 for _ in open(f)) - 1} строк")
print("\nПодсказки: b2b-флаг в registrations/orders; пилот = city in (msk, spb) и order_week >= 14")
print("скидка 15% на корзины >= 2000 в пилотных городах — эффект вплавлен в заказы (extra 6%).")
