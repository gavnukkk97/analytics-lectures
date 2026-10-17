# -*- coding: utf-8 -*-
"""Лекция 03 — Каналы и атрибуция (модули М3–М4 курса, X5-стиль).

Одна дека на две темы: карта каналов / UTM / немаркируемые каналы (М3, компактно)
и сквозная аналитика / 5 моделей атрибуции / ML-атрибуция по статье vc.ru (М4,
финальный фокус). Картинки: course/modules/M3/images/chan_*.png и M4/images/attrib_*.png.

Запуск из корня драфта: python3 presentations/make_lecture_03_04.py
"""
from __future__ import annotations
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from PIL import Image as PILImage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from make_decks_x5 import (BASE, OUT, clone_slide, fill_stmt, fill_bullets,
                           fill_table_lines, fill_stat, set_text,
                           title_font_size, set_pagenum, drop_slide)

IMG_M3 = HERE.parent / "course" / "modules" / "M3" / "images"
IMG_M4 = HERE.parent / "course" / "modules" / "M4" / "images"
EXT = HERE / "assets_lecture03"      # заимствования: статья vc.ru, лекция А. Акимова
SLIDE_W_IN = 20.0


def boxes_by_id(slide):
    return {sh.shape_id: sh for sh in slide.shapes if sh.has_text_frame}


def set_runs_size(shape, pt):
    for p in shape.text_frame.paragraphs:
        for r in p.runs:
            r.font.size = Pt(pt)


def pic_slide(prs, carriers, title, img_path, caption=None):
    """Слайд-картинка на носителе «список»: заголовок сверху, картинка ниже."""
    s = clone_slide(prs, carriers[2])
    b = boxes_by_id(s)
    set_text(b[5], title, size=title_font_size(title, 54))
    set_text(b[6], caption or "", size=20)
    for i in (7, 8, 9, 10, 11):
        set_text(b[i], "")
    w_px, h_px = PILImage.open(img_path).size
    max_h, max_w = 7.15, 18.4
    scale = min(max_h / (h_px / 150.0), max_w / (w_px / 150.0))
    pic_w, pic_h = w_px / 150.0 * scale, h_px / 150.0 * scale
    s.shapes.add_picture(str(img_path), Inches((SLIDE_W_IN - pic_w) / 2),
                         Inches(2.75), width=Inches(pic_w), height=Inches(pic_h))
    return s


def build_lecture():
    prs = Presentation(str(BASE))
    carriers = list(prs.slides)          # 0 титул, 1 тезис, 2 список, 3 число
    made = []

    # --- титул ---
    t = carriers[0]
    sh = next(s for s in t.shapes if s.has_text_frame and s.text_frame.text.strip())
    set_text(sh, ["Лекция 03", "Каналы и атрибуция"],
             size=title_font_size("Каналы и атрибуция", 142))
    tf = sh.text_frame
    p = tf.add_paragraph(); r = p.add_run(); r.text = ""
    p2 = tf.add_paragraph(); r2 = p2.add_run()
    r2.text = "модули 3–4: карта каналов · UTM · сквозная аналитика · модели атрибуции · ML"
    r2.font.size = Pt(28); r2.font.name = "X5 Sans"
    made.append(t)

    def stmt(big, small=None):
        s = clone_slide(prs, carriers[1]); fill_stmt(s, big, small)
        if small:
            set_runs_size(boxes_by_id(s)[7], 26)
        made.append(s)

    def bul(title, bullets, left_head, small=None):
        s = clone_slide(prs, carriers[2])
        fill_bullets(s, title, bullets, left_head=left_head, small=small)
        set_text(boxes_by_id(s)[10], "")          # шаблонный хвост «и список»
        made.append(s)

    def tbl(title, headers, rows, widths=None, note=None):
        """Настоящая таблица PowerPoint: заголовок navy, чередование строк."""
        s = clone_slide(prs, carriers[1])
        b = boxes_by_id(s)
        set_text(b[6], title, size=title_font_size(title, 84))
        set_text(b[7], note or "")
        n_rows, n_cols = len(rows) + 1, len(headers)
        gf = s.shapes.add_table(n_rows, n_cols, Inches(0.6), Inches(5.75),
                                Inches(18.8), Inches(0.52 * n_rows))
        table = gf.table
        table.first_row = True
        table.horz_banding = True
        if widths:
            total = sum(widths)
            for j, w in enumerate(widths):
                table.columns[j].width = Emu(int(Inches(18.8) * w / total))
        for i in range(n_rows):
            table.rows[i].height = Inches(0.52)

        def style_cell(cell, text, *, header=False, first_col=False, odd=False):
            cell.margin_left = Inches(0.12); cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.03); cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = 3  # middle (MSO_ANCHOR.MIDDLE)
            cell.fill.solid()
            if header:
                cell.fill.fore_color.rgb = RGBColor(0x0E, 0x28, 0x41)
            elif odd:
                cell.fill.fore_color.rgb = RGBColor(0xF0, 0xF4, 0xF8)
            else:
                cell.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            r = p.add_run(); r.text = text
            f = r.font
            f.name = "X5 Sans"
            f.size = Pt(16.5 if not header else 17)
            f.bold = header or first_col
            f.color.rgb = (RGBColor(0xFF, 0xFF, 0xFF) if header
                           else RGBColor(0x0E, 0x28, 0x41) if first_col
                           else RGBColor(0x2E, 0x40, 0x55))

        for j, h in enumerate(headers):
            style_cell(table.cell(0, j), h, header=True)
        for i, row in enumerate(rows, 1):
            for j, val in enumerate(row):
                style_cell(table.cell(i, j), str(val), first_col=(j == 0), odd=(i % 2 == 1))
        made.append(s)

    def stat(number, label, note):
        s = clone_slide(prs, carriers[3]); fill_stat(s, number, label, note); made.append(s)

    def pic(title, img, caption=None):
        if img.startswith("ext:"):
            img_path = EXT / img[4:]
        else:
            img_path = (IMG_M3 if img.startswith("chan_") else IMG_M4) / img
        made.append(pic_slide(prs, carriers, title, img_path, caption))

    # ================= ЧАСТЬ 1. КАНАЛЫ (М3) =================
    bul("План на сегодня",
        ["Часть 1 · каналы: карта, метрика, UTM, ТВ без разметки",
         "Часть 2 · сквозная аналитика: сшивка до юнит-таблицы",
         "Финал · атрибуция: 5 моделей и ML по статье vc.ru",
         "Симуляции: одни модели на разных данных",
         "Домашка и что дальше"],
        left_head="Две части")

    stmt("«У нас плохо с трафиком» — не постановка",
         "Каналов десятки: у каждого своя механика, скорость, цена и способ измерения (3.1)")

    tbl("Карта каналов: чем кто измерается",
        ["Группа", "Примеры", "Скорость", "Чем мерить"],
        [["Перформанс", "контекст · таргет · ритейл-медиа", "мгновенно", "UTM→заказ: CAC, ROMI"],
         ["Поиск/SEO", "органика · маркетплейсы", "месяцы–годы", "реферер «organic»"],
         ["Бренд-трафик", "бренд-запросы · direct", "следствие инвестиций", "брендовые запросы"],
         ["Инфлюенсеры", "блогеры · Telegram", "среднее", "UTM-ссылки, промокоды"],
         ["Партнёрки", "CPA-сети · рефералы", "среднее", "партнёрский ID"],
         ["Кросс-промо", "свои базы · пуши", "мгновенно", "deep-links, промокоды"],
         ["Офлайн/медийное", "ТВ · радио · наружка", "недели–месяцы", "НЕ размечается — спецметоды"]],
        widths=[3.4, 5.8, 3.6, 6.0])

    pic("Карта каналов: скорость × измеримость", "chan_01_map.png",
        "Канал, который нельзя разметить, — не «бесплатный»: у него другой способ измерения")

    bul("Тип рекламы → показатель продукта",
        ["Контекст ловит сформированный спрос: конверсия высокая",
         "Медийка формирует спрос: конверсия ниже, объём больше",
         "ТВ/наружка — верх воронки: заказы «через чужую» разметку",
         "Блогеры конвертируют доверием: retention когорт выше",
         "Кросс-промо дёшево — каннибализация баз и усталость"],
        left_head="Как работает реклама",
        small="Одна метрика на все каналы = несправедливость к верху воронки")

    pic("Разные рекламы — на разных этажах воронки", "chan_02_floors.png",
        "Поиск ловит спрос, медийка и ТВ его создают, CRM возвращает — одной метрикой не измерить")

    stmt("Быстрые деньги и игла перформанса",
         "LTV/CAC когорт < 1–3 и растущий CAC при ровном LTV → строить активы (SEO, бренд, рефералы)")

    pic("Игла перформанса", "chan_03_needle.png",
        "Аукцион греется по 3–5% в неделю — смотрите тренд CAC, а не месячный срез")

    tbl("Портфель «ЕдаДома»: месяц, учебные числа",
        ["Канал", "CAC", "LTV/CAC", "Вердикт"],
        [["Контекст", "420 ₽", "1,8", "рабочая лошадка, у потолка объёма"],
         ["Таргет", "610 ₽", "1,1", "на грани — тестировать связки"],
         ["Блогеры", "780 ₽", "1,6", "дорогой вход, дорогой LTV"],
         ["ТВ (2 города)", "≈900 ₽", "—", "растит всё остальное: гео-оценка"]],
        widths=[4.6, 2.2, 2.6, 9.4])

    pic("Портфель «ЕдаДома»", "chan_04_portfolio.png",
        "ТВ хуже по «CAC», но удешевляет брендовые кампании и органику — эффект на весь рынок города")

    stmt("Половина «странного» в отчётах — опечатки в метках",
         "yandex ≠ Yandex, пробел обрезает ссылку: без UTM-дисциплины всё downstream мертво (3.2)")

    tbl("UTM: 5 параметров, 3 обязательны",
        ["Параметр", "Обяз.", "Что кодирует", "Пример"],
        [["utm_source", "✔", "площадка", "yandex · vk · telegram"],
         ["utm_medium", "✔", "тип трафика", "cpc · cpm · email"],
         ["utm_campaign", "✔", "кампания", "spring_delivery_msk"],
         ["utm_content", "—", "креатив", "banner_top · {creative_id}"],
         ["utm_term", "—", "ключевое слово", "{keyword}"]],
        widths=[4.4, 1.6, 5.2, 7.6])

    pic("Анатомия размеченной ссылки", "chan_05_utm_anatomy.png",
        "Макросы {creative_id}, {keyword} дают детализацию до креатива без ручной разметки")

    bul("Гигиена разметки",
        ["Латиница и дефисы; регистр важен: yandex ≠ Yandex",
         "Справочник кампаний: проект_сегмент_гео_месяц",
         "Макросы {creative_id}, {keyword} — ссылки без рутины",
         "Еженедельный аудит; тесты — только с префиксом test_",
         "UTM — буквальные обучающие фичи ML-атрибуции"],
        left_head="Регламент команды",
        small="Аудит 30 ссылок: ~30% месяца — в слепой зоне или с искажениями")

    stat("30%", "бюджета в слепой зоне",
         ["Аудит 30 ссылок «ЕдаДома»: 4 без medium, кириллица, пробелы, регистр-двойники",
          "Чинится за день: справочник + шаблоны"])

    pic("Аудит 30 ссылок", "chan_06_audit.png",
        "Цена невнимания — месяц испорченных решений по бюджету")

    stmt("ТВ не кликается — оно меняет память",
         "Брендовые запросы, direct, установки: эффект без ссылки — нужны косвенные методы (3.3)")

    pic("Пик-анализ: всплески после вылетов", "chan_07_tv_spike.png",
        "Сверяйте с прошлым годом и контрольными гео: сезонность легко «доказывает» что угодно")

    tbl("ТВ-тест «ЕдаДома»: 2 города против 3 контрольных",
        ["Метрика", "Тест", "Контроль"],
        [["Брендовые запросы", "+40%", "+3% (сезон)"],
         ["Direct-заходы", "+12%", "—"],
         ["Новые на 10 тыс. жителей", "+64", "+7"],
         ["DiD-прирост", "+57 новых за 4 недели", "—"],
         ["«CAC ТВ»", "≈940 ₽", "дороже контекста — но растит весь рынок"]],
        widths=[7.6, 5.2, 6.0])

    pic("Гео-тест (DiD): инкрементальность ТВ", "chan_08_geo_did.png",
        "Самый честный из косвенных методов: даёт инкрементальный эффект, а не корреляцию")

    pic("Иерархия доказательств", "chan_09_hierarchy.png",
        "MMM калибруется экспериментами; пик-анализ — всегда, как первый эшелон")

    # ============ ЧАСТЬ 2. СКВОЗНАЯ И АТРИБУЦИЯ (М4) ============
    stmt("«Какой канал приводит людей, которые покупают и остаются?»",
         "Отчёты есть у всех — но каждый врёт по-своему. Сквозная аналитика = дисциплина сшивки (4.1)")

    pic("Сквозная аналитика: слои до user_id", "attrib_07_layers.png",
        "Ключи: yclid/gclid → cookie/device_id → user_id (авторизация) → email/телефон")

    stmt("Юнит-таблица: один пользователь — одна строка — вся история",
         "Все касания (не только первый/последний!), заказы, LTV → CAC, когорты, retention, атрибуция")

    pic("Юнит-таблица: пример", "attrib_09_unit_table.png",
        "Храните все касания, а не только первый и последний: модели атрибуции учатся на полных путях")

    tbl("Где рвётся цепочка",
        ["Разрыв", "Чем чиним"],
        [["Кросс-девайс", "авторизация как ключ сшивки"],
         ["Блокировщики · ATT", "агрегаты, MMM, гео-методы"],
         ["Офлайн-покупки", "CRM/касса — мэтчинг по карте, телефону"],
         ["Окна атрибуции платформ", "хранить сырые касания у себя"]],
        widths=[7.2, 11.6])

    stmt("Кому засчитать заказ: медийка → контекст → письмо → бренд → покупка?",
         "Ответ зависит от модели атрибуции. А бюджет — от ответа (4.2)")

    pic("Один путь — пять мнений", "attrib_08_path.png",
        "Правильной модели не существует: каждое правило — допущение со своим смещением")

    tbl("Пять моделей = пять правил дележа ценности",
        ["Модель", "Правило", "Смещение"],
        [["First-click", "всё первому", "переоценивает верх воронки"],
         ["Last-click", "всё последнему", "переоценивает бренд, direct, ретаргет"],
         ["Linear", "поровну", "«демократия» без различий"],
         ["Time-decay", "экспоненциально к последнему", "сдвиг к финалу, период с потолка"],
         ["U-shaped", "40% + 40% + 20%", "середина всегда «виновата» меньше"]],
        widths=[4.6, 7.4, 6.8])

    pic("Пять дележей одной конверсии", "attrib_01_chain_models.png",
        "Цепочка A → B → C ценностью 1: кто открыл, кто вёл, кто закрыл — модель решает, а не данные")

    pic("Вывод о канале зависит от модели", "attrib_02_channels_heat.png",
        "Бренд под last-click — «герой», под first — почти никто: он закрывает, а не открывает")

    stmt("Last-click ломается системно",
         "Перехват брендом · view-through не виден · кросс-девайс рвёт путь · канал подогревания — «дармоед»")

    bul("Как выбирать модель — честный ответ",
        ["«Что открывает клиентов?» → first / U-shaped",
         "«Что закрывает?» → last · «Как ведёт себя путь?» → linear",
         "Держите 2–3 модели рядом: расхождения — диагностика",
         "Большой first при нулевом last — канал-«открыватель»",
         "Атрибуция отвечает «что было», не «что, если»"],
        left_head="Вопрос → модель")

    stmt("Правила — допущения. Дальше веса считает модель",
         "Ключевой источник: vc.ru — «Решаем проблему атрибуции в digital-маркетинге при помощи ML» (4.3)")

    bul("Размеченные данные — топливо ML",
        ["Веб/моб-аналитика: переходы, поведение, устройства",
         "Кабинеты: показы и клики — включая показы без клика",
         "CRM — источник метки «купил / не купил»",
         "UTM-дисциплина = качество обучающих фич"],
        left_head="Что собираем")

    pic("Пайплайн ML-атрибуции (статья vc.ru)", "ext:vc16_pipeline.png",
        "Собрать цепочки → фичи → модель → вклады касаний → перераспределение бюджета")

    stmt("Вклад касания = ΔP(конверсии): с касанием против без",
         "Обучаем P(конверсия | цепочка); убрали касание — пересчитали; разница прогнозов = вклад")

    pic("Вклад касания = разница прогнозов", "attrib_03_dp_concept.png",
        "Бренд почти не меняет прогноз (перехватчик), медийка поднимает вероятность в разы")

    tbl("Что ML чинит против last-click",
        ["Проблема", "Как обходит ML"],
        [["Кросс-девайс", "сшитые профили + устройство как фича"],
         ["View-through", "показы — полноценные касания"],
         ["Запоздалая конверсия", "вся история касаний с временами"],
         ["Перехват брендом", "ΔP обнуляет мнимый вклад"],
         ["Веса с потолка", "измеренное влияние на вероятность"]],
        widths=[6.4, 12.4])

    stat("+6%", "клиентов · бюджет тот же",
         ["Кейс статьи vc.ru: перераспределение с бренд-кампаний на небренд → корректировка ставок",
          "Практический продукт ML — не «красивые веса», а другие ставки"])

    pic("Результат из статьи vc.ru", "ext:vc10_result.png",
        "Конверсии перетекли с брендовых кампаний на небрендовые — ставки скорректированы, бюджет тот же")

    stmt("DDA платформ видит только свои касания. Своё — Шепли и Марков",
         "Open-source: ChannelAttribution, DP6 Marketing-Attribution-Models; вход — сырые пути из Logs API Метрики")

    pic("Вектор Шепли: делёж без «с потолка»", "ext:akimov25.png",
        "Вклад канала — среднее по всем коалициям с ним и без неё (по лекции Антона Акимова)")

    pic("Пример Шепли на двух цепочках", "ext:akimov26.png",
        "Перебираем коалиции каналов на реальных путях и усредняем вклады — получается честный делёж")

    pic("Цепи Маркова: вклад = remove effect", "ext:akimov27.png",
        "Граф переходов между каналами; вклад — насколько падает вероятность конверсии без этого канала")

    pic("Симуляция 1 · бренд только перехватывает", "attrib_04_sim_intercept.png",
        "Бренд-контекст: 46% в last-click против 12% в ML — треть «заслуг» это перехват чужих путей")

    pic("Симуляция 2 · бренд реально помогает", "attrib_05_sim_brandworks.png",
        "Те же модели на других данных: доля бренда по ML выросла — сначала вопрос «что делает канал»")

    pic("Симуляция 3 · мало данных", "attrib_06_sim_smalldata.png",
        "На подвыборках ML скачет от 3% до 18%: проверяйте устойчивость, прежде чем резать бюджет")

    stmt("Граница доверия: корреляция ≠ причинность",
         "«Что будет, если отключить канал» — только эксперимент (гео-тесты, 5.3). DGA Директа/GA4 — своя экосистема")

    bul("Шпаргалка",
        ["Метрика подбирается под механику канала",
         "UTM-гигиена — фундамент downstream-аналитики",
         "Немаркируемые: пик-анализ → гео/DiD → MMM",
         "Сквозная = юнит-таблица с полной историей касаний",
         "Пять моделей — допущения: держите 2–3 рядом",
         "ML: вклад = ΔP; чинит перехват и view-through",
         "Финальная проверка — только инкрементальность"],
        left_head="Вынести с лекции")

    bul("Что дальше",
        ["Прочитать статью vc.ru про ML-атрибуцию",
         "practice_4.2.py: 5 моделей на одних цепочках",
         "practice_4.3.py: ML против last-click",
         "Вопрос: канал X — first 30%, last 2%. Кто это?",
         "Следующая лекция: промо и квазиэксперименты"],
        left_head="Домашнее задание")

    # финализация: убрать носители, пронумеровать
    for idx in range(3, -1, -1):
        drop_slide(prs, idx)
    for i, s in enumerate(made, 1):
        set_pagenum(s, i)
    path = OUT / "Лекция 03 — Каналы и атрибуция (модули 3–4).pptx"
    prs.save(str(path))
    return path


if __name__ == "__main__":
    print("ok", build_lecture().name)
