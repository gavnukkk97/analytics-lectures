# -*- coding: utf-8 -*-
"""Эталонные числа капстоуна (для ревьюера). Запуск из корня драфта:
python3 course/capstone/solutions/check.py
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

D = Path(__file__).resolve().parents[1] / "data"
reg = pd.read_csv(D / "registrations.csv")
orders = pd.read_csv(D / "orders.csv")
open_ends = pd.read_csv(D / "open_ends.csv")
grid = pd.read_csv(D / "grid.csv")

print("=" * 70)
print("ЭТАП 2. Когорты и LTV (b2b vs b2c), горизонт 12 недель жизни")
print("=" * 70)
o = orders.merge(reg[["user_id", "week"]].rename(columns={"week": "reg_week"}), on="user_id")
o["age"] = o["order_week"] - o["reg_week"]
o12 = o[(o["age"] >= 0) & (o["age"] < 12)]
for seg, g in o12.groupby("b2b"):
    size = reg[reg["b2b"] == seg]["user_id"].nunique()
    ltv_margin = g["margin"].sum() / size
    ret4 = g[g["age"] == 4]["user_id"].nunique() / size
    print(f"сегмент {'b2b ' if seg else 'b2c'}: LTV12(маржа) = {ltv_margin:,.0f} ₽ | retention W4 = {ret4:.1%} | n={size}")

print()
print("=" * 70)
print("ЭТАП 3. Гео-пилот: DiD по городам (заказы/неделю на юзера)")
print("=" * 70)
treat_cities = ["msk", "spb"]
t = orders.copy()
t["promo_city"] = t["city"].isin(treat_cities)
t["after"] = t["order_week"] >= 14
weeks_pre, weeks_post = 14, 12  # симметричные окна
pre = t[t["order_week"].between(14 - weeks_pre, 13)]
post = t[t["order_week"].between(14, 14 + weeks_post - 1)]
for name, df in [("pre", pre), ("post", post)]:
    per = df.groupby("promo_city")["order_week"].count()
    print(f"{name}: заказов пилот={per.get(True, 0):,} / контроль={per.get(False, 0):,}")
did = ((post["promo_city"].mean() - pre["promo_city"].mean()))
# корректный DiD по ставке заказов на юзеро-неделю
u_t_pre = pre[pre["promo_city"]]["user_id"].nunique(); u_c_pre = pre[~pre["promo_city"]]["user_id"].nunique()
u_t_post = post[post["promo_city"]]["user_id"].nunique(); u_c_post = post[~post["promo_city"]]["user_id"].nunique()
rate_t_pre = len(pre[pre["promo_city"]]) / max(u_t_pre * weeks_pre, 1)
rate_c_pre = len(pre[~pre["promo_city"]]) / max(u_c_pre * weeks_pre, 1)
rate_t_post = len(post[post["promo_city"]]) / max(u_t_post * weeks_post, 1)
rate_c_post = len(post[~post["promo_city"]]) / max(u_c_post * weeks_post, 1)
did_rate = (rate_t_post - rate_t_pre) - (rate_c_post - rate_c_pre)
print(f"DiD ставки заказов (пилот − контроль): {did_rate:+.4f} заказа/юзеро-неделю "
      f"({did_rate / rate_t_pre:+.1%} к базовой ставке)")

print()
print("=" * 70)
print("ЭТАП 4а. Open-ends: распределение категорий (истина — для валидации студенческой разметки)")
print("=" * 70)
print(open_ends["true_category"].value_counts().to_string())

print()
print("=" * 70)
print("ЭТАП 4б. Решётка: средние позиции элементов (1 = первый полюс конструкта)")
print("=" * 70)
piv = grid.pivot_table(index="element", columns="construct", values="rating")
print(piv.round(1).to_string())
print("\nИнсайт для проверки: «Идеал» близок к полюсам быстрая/заботится/доступная;")
print("свободная позиция «быстрая + заботится» (Агрегатор_1 — быстрая, но безразличная).")
