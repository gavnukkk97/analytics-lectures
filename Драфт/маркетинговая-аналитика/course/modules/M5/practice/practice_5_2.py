# -*- coding: utf-8 -*-
"""Практика 5.2 — Квазиэксперименты: гео-DiD, порог RDD и наивное сравнение (урок 5.2)."""
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
rng = np.random.default_rng(E.SEED + 52)
WEEKS = 26
reg = E.make_registrations(WEEKS, rng)
orders = E.make_geo_pilot(reg, WEEKS, effect=0.10, rng=rng)  # пилот: msk+spb, с недели 14

# %% [markdown]
# Шаг 0. Наивное сравнение «пользовались промо vs нет» (селекция!).

# %%
big_after = orders[orders["after"] == 1]
used = big_after[big_after["promo_city"] & big_after["big_basket"]]["user_id"].unique()
o_used = big_after[big_after["user_id"].isin(used)]
o_rest = big_after[~big_after["user_id"].isin(used)]
print(f"НАИВНО: заказов/юзера у «пользователей промо» {len(o_used)/len(used):.2f} "
      f"vs у остальных {len(o_rest)/o_rest['user_id'].nunique():.2f} → "
      f"«эффект» {(len(o_used)/len(used))/(len(o_rest)/o_rest['user_id'].nunique())-1:+.0%}")
print("(селекция: большие корзины и так заказывают чаще — это не эффект промо)\n")

# %% [markdown]
# Шаг 1. Гео-DiD: ставка заказов на юзеро-неделю, пилот против контроля.

# %%
t = orders.copy()
treated = t["promo_city"]
users = reg["user_id"].nunique()
u_treat = reg[reg["city"].isin(["msk", "spb"])]["user_id"].nunique()
u_ctrl = users - u_treat
pre = t[t["order_week"] < 14]; post = t[t["order_week"] >= 14]
rate_t_pre = len(pre[pre["promo_city"]]) / 14 / u_treat
rate_c_pre = len(pre[~pre["promo_city"]]) / 14 / u_ctrl
rate_t_post = len(post[post["promo_city"]]) / 12 / u_treat
rate_c_post = len(post[~post["promo_city"]]) / 12 / u_ctrl
did = (rate_t_post - rate_t_pre) - (rate_c_post - rate_c_pre)
print(f"ставки заказов/юзеро-нед: пилот {rate_t_pre:.3f}→{rate_t_post:.3f} | "
      f"контроль {rate_c_pre:.3f}→{rate_c_post:.3f}")
print(f"DiD = {did:+.4f} ({did/rate_t_pre:+.1%} к базе) — эффект пилота (вплавлено 10%: проверка)")

# %% [markdown]
# Шаг 2. RDD-окно у порога 3000 ₽ (в пилотных городах после старта).

# %%
pa = orders[(orders["promo_city"] == 1) & (orders["after"] == 1)]
lo, hi = 1600, 2400
below = pa[(pa["revenue"] >= lo) & (pa["revenue"] < 2000)]
above = pa[(pa["revenue"] >= 2000) & (pa["revenue"] <= hi)]
rdd = above["margin"].mean() - below["margin"].mean()
print(f"\nRDD-окно [{lo}, {hi}]: маржа над порогом {above['margin'].mean():.0f} ₽ "
      f"vs под порогом {below['margin'].mean():.0f} ₽ → разрыв {rdd:+.0f} ₽")
print("(порог 3000 даёт скидку над ним — разрыв маржи у границы и есть сигнал механики)")

# %%
fig, ax = plt.subplots(figsize=(8.4, 4.4))
bins = np.arange(1200, 3200, 100)
ax.hist(pa[pa["revenue"] < 4500]["revenue"], bins=bins, color="#4C72B0", alpha=0.85)
ax.axvline(2000, color="#C44E52", ls="--", lw=2, label="порог промо 2000 ₽")
ax.set_title("RDD: плотность корзин у порога — пик справа = подтягивание к порогу")
ax.set_xlabel("сумма корзины, ₽"); ax.legend()
fig.tight_layout(); fig.savefig(OUT / "practice_5_2_rdd.png", bbox_inches="tight")
print("\nГрафик: practice_5_2_rdd.png (пик сразу за порогом — гейминг, обсуждаем смещение окна)")
