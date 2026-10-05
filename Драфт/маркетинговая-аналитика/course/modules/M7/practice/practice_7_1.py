# -*- coding: utf-8 -*-
"""Практика 7.1 — Конвейер LLM-разметки open-ends с валидацией κ (урок 7.1).

LLM имитируется детерминированным «классификатором» с настроенной долей ошибок:
так воспроизводимы весь конвейер (кодбук → кодирование → κ → правка → финал)
без внешних API.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "lib"))
import edadoma as E

rng = np.random.default_rng(71)
oe = E.make_open_ends(300, rng)

# %% [markdown]
# Шаг 1. «LLM» с кодбуком v1: путает холодную еду с опозданиями (типичная путаница модели).

# %%
CODEBOOK = {"опоздания": ["поздно", "ехал", "момент"],
            "холодная еда": ["холодн", "лёд", "остыл"],
            "цены": ["дорого", "цены", "приготовить"],
            "ассортимент": ["ресторан", "сети", "выбор"],
            "конкурент": ["перешёл", "конкурент", "соседний"]}
def llm_v1(text: str) -> str:
    for cat, keys in CODEBOOK.items():          # «опоздания» стоят раньше «холодной еды»
        if any(k in text for k in keys):
            return cat
    return "другое"

oe["pred_v1"] = oe["answer"].map(llm_v1)

def kappa(a, b):
    tab = pd.crosstab(a, b)
    po = np.trace(tab) / tab.values.sum()
    pe = (tab.sum(axis=1) / tab.values.sum() * tab.sum(axis=0) / tab.values.sum()).sum()
    return (po - pe) / (1 - pe)

k1 = kappa(oe["true_category"], oe["pred_v1"])
acc1 = (oe["true_category"] == oe["pred_v1"]).mean()
print(f"кодбук v1: accuracy {acc1:.1%}, Cohen's κ = {k1:.2f} — ниже порога 0.7")

# %% [markdown]
# Шаг 2. Правка кодбука: уточнили определения (холодная еда выше опозданий + синонимы).

# %%
CODEBOOK_V2 = {"холодная еда": ["холодн", "лёд", "остыл", "как лёд"],   # подняли выше
               "опоздания": ["поздно", "ехал", "момент", "привозят"],
               "цены": ["дорого", "цены", "приготовить"],
               "ассортимент": ["ресторан", "сети", "выбор", "мало"],
               "конкурент": ["перешёл", "конкурент", "соседний", "сервис"]}
oe["pred_v2"] = oe["answer"].map(lambda t: next((c for c, ks in CODEBOOK_V2.items()
                                                 if any(k in t for k in ks)), "другое"))
k2 = kappa(oe["true_category"], oe["pred_v2"])
print(f"кодбук v2: accuracy {(oe['true_category']==oe['pred_v2']).mean():.1%}, κ = {k2:.2f}"
      f" → {'в отчёт' if k2 >= 0.7 else 'ещё править'}")

# %% [markdown]
# Шаг 3. Итог: распределение категорий + слепая подвыборка «руками» (как в реальном конвейере).

# %%
val = oe.sample(30, random_state=1)          # «ручная разметка» = истина (симуляция)
kv = kappa(val["true_category"], val["pred_v2"])
print(f"κ на валидационной подвыборке (n=30): {kv:.2f}")
print("\nРаспределение (v2):")
print(oe["pred_v2"].value_counts().to_string())
print("\nВыводы: качество разметки определяется кодбуком (человеком), а не только моделью;")
print("κ публикуется рядом с результатом; редкие категории при κ<0.7 — на ручную разметку.")
