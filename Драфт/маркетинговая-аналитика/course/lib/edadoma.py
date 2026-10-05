# -*- coding: utf-8 -*-
"""Общий генератор синтетических данных «ЕдаДома» для практик и капстоуна.

Один источник правды: практики и капстоун работают на одних данных (seed фиксирован).
Запускать из корня драфта: python3 course/practice_x_y.py
"""
from __future__ import annotations
import numpy as np
import pandas as pd

SEED = 2026

# Каналы привлечения: доля трафика, (доля ядра, p возврата ядра, p 2го заказа случайных), CPO_ядро
CHANNELS = {
    "context":  {"share": 0.42, "core": 0.26, "p_core": 0.55, "p_rand": 0.10, "aov": 1450},
    "target":   {"share": 0.25, "core": 0.20, "p_core": 0.50, "p_rand": 0.07, "aov": 1380},
    "bloggers": {"share": 0.18, "core": 0.22, "p_core": 0.53, "p_rand": 0.09, "aov": 1520},
    "organic":  {"share": 0.15, "core": 0.30, "p_core": 0.60, "p_rand": 0.10, "aov": 1490},
}

def make_registrations(weeks=26, rng=None):
    """Регистрации по неделям и каналам: user_id, week, channel, city, b2b."""
    rng = rng or np.random.default_rng(SEED)
    rows = []
    uid = 0
    for w in range(weeks):
        n = int(rng.normal(1500, 120))
        for ch, p in CHANNELS.items():
            n_ch = int(n * p["share"] + rng.normal(0, 8))
            for _ in range(max(0, n_ch)):
                city = str(rng.choice(["msk", "spb", "ekb", "nsk", "kzn", "sochi"], p=[.3, .2, .15, .15, .1, .1]))
                b2b = rng.random() < 0.07
                rows.append({"user_id": uid, "week": w, "channel": ch, "city": city, "b2b": b2b})
                uid += 1
    return pd.DataFrame(rows)

def make_orders(reg=None, weeks=26, rng=None):
    """Заказы: гетерогенная привычность (ядро/случайные), чек по каналу, маржа 25%."""
    rng = rng or np.random.default_rng(SEED + 1)
    reg = reg if reg is not None else make_registrations(weeks, rng)
    rows = []
    for ch, p in CHANNELS.items():
        ch_u = reg[reg["channel"] == ch]
        is_core = rng.random(len(ch_u)) < p["core"]
        for (uid, w0, city, b2b), core in zip(
                ch_u[["user_id", "week", "city", "b2b"]].itertuples(index=False), is_core):
            ages = np.arange(w0, weeks)
            p_alive = np.where(core, p["p_core"], p["p_rand"] * np.exp(-(ages - w0) / 2.5))
            for age in ages[rng.random(len(ages)) < p_alive]:
                aov = p["aov"] * (1.25 if b2b else 1.0) * rng.normal(1, 0.18)
                rows.append({"user_id": uid, "order_week": int(age), "channel": ch,
                             "city": city, "b2b": b2b, "revenue": round(aov, 2)})
    df = pd.DataFrame(rows).sort_values(["user_id", "order_week"]).reset_index(drop=True)
    df["margin"] = (df["revenue"] * 0.25).round(2)
    return df

def make_touches(n_users=4000, rng=None):
    """Цепочки касаний для атрибуции: показы/клики по каналам + флаг конверсии.

    Каналы: display (view-only, верх), search_nb (небренд), email, search_brand.
    Конверсия зависит от полноты цепочки (в search_nb и display есть реальный вклад).
    """
    rng = rng or np.random.default_rng(SEED + 2)
    chans = ["display", "search_nb", "email", "search_brand"]
    rows = []
    for uid in range(n_users):
        n_t = rng.integers(1, 6)
        seq = list(rng.choice(chans, size=n_t, p=[0.22, 0.33, 0.20, 0.25]))
        # 30% цепочек заканчиваются брендом (перехватчик)
        if rng.random() < 0.30 and seq[-1] != "search_brand":
            seq.append("search_brand")
        has_nb = "search_nb" in seq
        has_disp = "display" in seq
        n_touch = len(seq)
        p_conv = 0.02 + 0.05 * has_nb + 0.04 * has_disp + 0.06 * (n_touch >= 3) + 0.03 * seq.count("email")
        conv = rng.random() < min(p_conv, 0.35)
        for pos, ch in enumerate(seq):
            rows.append({"user_id": uid, "position": pos, "channel": ch,
                         "is_click": int(ch != "display"), "converted": int(conv)})
    return pd.DataFrame(rows)

def make_geo_pilot(reg=None, weeks=26, effect=0.06, rng=None):
    """Гео-пилот промо: с недели 14 в msk/spb действует скидка 15% на заказы от 2000₽.

    Возвращает orders с флагами promo_city (город в пилоте) и после запуска,
    эффект = прирост вероятности заказа в городах пилота после недели 14.
    """
    rng = rng or np.random.default_rng(SEED + 3)
    reg = reg if reg is not None else make_registrations(weeks, rng)
    orders = make_orders(reg, weeks, rng)
    orders["promo_city"] = orders["city"].isin(["msk", "spb"])
    orders["after"] = (orders["order_week"] >= 14).astype(int)
    # инкремент: часть «дополнительных» заказов в пилотных городах после старта
    extra = ((orders["promo_city"] & orders["after"].astype(bool)) &
             (rng.random(len(orders)) < effect))
    orders = pd.concat([orders, orders[extra]], ignore_index=True)
    orders["big_basket"] = orders["revenue"] >= 2000
    orders.loc[orders["promo_city"] & orders["after"].astype(bool) & orders["big_basket"],
               ["revenue", "margin"]] *= 0.85  # скидка на крупные корзины в пилоте
    return orders.sort_values(["user_id", "order_week"]).reset_index(drop=True)

OPEN_END_CATEGORIES = {
    "опоздания":     ["привозят холодное и поздно", "курьер ехал час", "доставка в самый неподходящий момент"],
    "цены":          ["стало дорого", "цены кусаются", "проще приготовить самому"],
    "холодная еда":  ["еда приехала холодная", "суп как лёд", "пицца остыла"],
    "ассортимент":   ["мало ресторанов рядом", "нет любимой сети", "выбор маленький"],
    "конкурент":     ["перешёл в другой сервис", "у конкурентов быстрее", "соседний сервис дешевле"],
}
def make_open_ends(n=300, rng=None):
    """Открытые ответы «что мешает заказывать чаще» + скрытая категория (для разметки и κ)."""
    rng = rng or np.random.default_rng(SEED + 4)
    probs = [0.30, 0.22, 0.20, 0.12, 0.16]
    cats, texts = list(OPEN_END_CATEGORIES), []
    fillers = ["часто", "иногда", "постоянно", "", "в последнее время"]
    for i in range(n):
        c = str(rng.choice(cats, p=probs))
        t = str(rng.choice(OPEN_END_CATEGORIES[c])) + ", " + str(rng.choice(fillers))
        if rng.random() < 0.12:
            t += ", и вообще"
        texts.append(t); cats_true = cats
    df = pd.DataFrame({"respondent": range(n), "answer": texts})
    df["true_category"] = [str(rng.choice(cats_true, p=probs)) for _ in range(n)]
    # заново: категория должна соответствовать тексту
    cat_by_text = {}
    for c, exs in OPEN_END_CATEGORIES.items():
        for e in exs:
            cat_by_text[e] = c
    df["true_category"] = df["answer"].map(lambda t: next(c for c, exs in OPEN_END_CATEGORIES.items()
                                                          if any(e in t for e in exs)))
    return df

GRID_ELEMENTS = ["ЕдаДома", "Агрегатор_1", "Агрегатор_2", "Столовая", "Идеал"]
GRID_CONSTRUCTS = [("быстрая", "небыстрая"), ("доступная", "дорогая"),
                   ("заботится", "безразличная"), ("для семьи", "для одного")]
def make_grid(n_resp=10, rng=None):
    """Мини-репертуарная решётка: оценки элементов (1-7) по конструктам, 10 респондентов."""
    rng = rng or np.random.default_rng(SEED + 5)
    # «истинные» позиции элементов по полюсам (1 = первый полюс)
    pos = {"ЕдаДома": [4, 2, 2, 2], "Агрегатор_1": [2, 5, 6, 6],
           "Агрегатор_2": [3, 4, 5, 5], "Столовая": [5, 1, 4, 3], "Идеал": [1, 2, 1, 3]}
    rows = []
    for r in range(n_resp):
        for el, vals in pos.items():
            for ci, (a, b) in enumerate(GRID_CONSTRUCTS):
                rows.append({"respondent": r, "element": el, "construct": f"{a}—{b}",
                             "rating": int(np.clip(rng.normal(vals[ci], 0.8), 1, 7))})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    r = make_registrations(); o = make_orders(r)
    print("регистраций:", len(r), "| заказов:", len(o))
    print(o.head(3))
