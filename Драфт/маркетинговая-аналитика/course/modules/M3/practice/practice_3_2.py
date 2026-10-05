# -*- coding: utf-8 -*-
"""Практика 3.2 — Аудит UTM-ссылок и справочник (урок 3.2)."""
from __future__ import annotations
import re

LINKS = [
    "https://edadoma.ru/?utm_source=yandex&utm_medium=cpc&utm_campaign=spring_msk",
    "https://edadoma.ru/promo?utm_source=Yandex&utm_medium=cpc&utm_campaign=spring_msk",      # регистр
    "https://edadoma.ru/?utm_source=vk&utm_medium=cpm&utm_campaign=акция_апрель",              # кириллица
    "https://edadoma.ru/?utm_source=telegram&utm_medium=cpc&utm_campaign=blog_tour",          # без content — блогер
    "https://edadoma.ru/?utm_source=email&utm_campaign=welcome",                               # нет medium
    "https://edadoma.ru/?utm_source=vk&utm_medium=cpm&utm_campaign=new_promo&utm_content=баннер 1",  # пробел
    "https://edadoma.ru/?utm_source=yandex&utm_medium=cpc&utm_campaign=spring_msk?utm_term=pizza",    # второй ?
    "https://edadoma.ru/?utm_source=bloggers&utm_medium=cpc&utm_campaign=collab&utm_content={creative_id}",  # ок
]

def audit(url: str):
    problems = []
    if url.count("?") > 1:
        problems.append("два '?' — метки после первого '?' сломаны")
    params = dict(re.findall(r"utm_(\w+)=([^&?#]+)", url))
    if not params:
        return ["нет UTM-меток"]
    if "utm_source" not in params: problems.append("нет source (обяз.)")
    if "utm_medium" not in params: problems.append("нет medium (обяз.)")
    if "utm_campaign" not in params: problems.append("нет campaign (обяз.)")
    for k, v in params.items():
        if re.search(r"[а-яА-ЯёЁ]", v): problems.append(f"кириллица в {k}")
        if " " in v: problems.append(f"пробел в {k} (обрежется)")
        if k == "utm_source" and v != v.lower(): problems.append(f"регистр в {k} ('{v}')")
    return problems

print(f"{'№':2} | {'вердикт':6} | замечания")
print("-" * 78)
ok = 0
for i, u in enumerate(LINKS, 1):
    p = audit(u)
    ok += not p
    print(f"{i:2} | {'OK' if not p else 'ОШИБКА':6} | {'; '.join(p) if p else '—'}")
print(f"\nГодных ссылок: {ok}/{len(LINKS)}; слепая зона бюджета ≈ {(len(LINKS)-ok)/len(LINKS):.0%}")

print("""
Справочник UTM «ЕдаДома» (фрагмент):
  source:   yandex | vk | telegram | email | bloggers | partners
  medium:   cpc | cpm | email | referral
  campaign: {product}_{segment}_{geo}_{month}  латиницей: spring_msk_2026-04
  content:  {creative_id} (макрос) или banner_top/button_static
  term:     {keyword} (макрос) — только поисковые кампании
Правила: регистр единый (нижний), дефис/подчёркивание, один '?', test_ префикс для тестов.
""")
