# -*- coding: utf-8 -*-
"""Генератор презентаций в корпоративном стиле X5 (по шаблону X5Digital).

База: /tmp/x5_base.pptx (4 слайда-носителя из шаблона, пережато до ~5 МБ):
  0 — титул (X5 Sans Medium 142pt)
  1 — заголовок + пояснение (84pt / 36pt)      → слайды-тезисы и «таблицы строками»
  2 — текст и список (две колонки)             → списки, открывашка, финал «Что дальше»
  3 — важное число (132pt)                     → большие числа

Запуск: python3 presentations/make_decks_x5.py → presentations_x5/Урок *.pptx
Контент переиспользуется из make_decks.py (DECKS).
"""
from __future__ import annotations
import copy
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from make_decks import DECKS  # контент уроков

BASE = next(iter(sorted(HERE.glob("x5_base.pptx"))), None) or Path("/tmp/x5_base.pptx")
OUT = HERE.parent / "presentations"
OUT.mkdir(exist_ok=True)

NAVY, ORANGE = "0E2841", "E97132"

# ---------------------------------------------------------------- клонирование
def clone_slide(prs, src):
    dest = prs.slides.add_slide(src.slide_layout)
    for sp in list(dest.shapes._spTree):
        if sp.tag.split("}")[-1] in ("sp", "pic", "graphicFrame", "grpSp", "cxnSp"):
            dest.shapes._spTree.remove(sp)
    for shp in src.shapes._spTree:
        if shp.tag.split("}")[-1] in ("sp", "pic", "graphicFrame", "grpSp", "cxnSp"):
            dest.shapes._spTree.append(copy.deepcopy(shp))
    # rels: переносим связи с картинками (нумерация обычно совпадает, но страхуемся ремапом)
    for rId, rel in list(src.part.rels.items()):
        if rel.reltype == RT.SLIDE_LAYOUT:
            continue
        if rel.is_external:
            new_id = dest.part.rels.get_or_add_ext_rel(rel.reltype, rel.target_ref)
        else:
            new_id = dest.part.relate_to(rel.target_part, rel.reltype)
        if new_id != rId:  # двухфазный ремап r:embed/r:id внутри клонированного XML
            token = "~~RMAP~~"
            xml = dest.shapes._spTree
            for el in xml.iter():
                for attr in list(el.attrib):
                    if el.attrib[attr] == rId:
                        el.attrib[attr] = token
            for el in xml.iter():
                for attr in list(el.attrib):
                    if el.attrib[attr] == token:
                        el.attrib[attr] = new_id
    return dest

# ---------------------------------------------------------------- заполнение
def _norm(s):
    return s.replace("\x0b", "").replace("\r", "").strip()

def set_text(shape, text, size=None, grow=None):
    tf = shape.text_frame
    lines = text if isinstance(text, list) else [text]
    # первый параграф-носитель форматирования
    proto = None
    for p in tf.paragraphs:
        if p.runs:
            proto = p
            break
    for p in list(tf.paragraphs):
        p._p.getparent().remove(p._p)
    for i, ln in enumerate(lines):
        p = tf.add_paragraph()
        if proto is not None and i == 0 and proto.runs:
            p.alignment = proto.alignment
        r = p.add_run(); r.text = ln
        if proto is not None and proto.runs:
            pr = proto.runs[0]
            r.font.name = pr.font.name
            if size:
                r.font.size = Pt(size)
            elif pr.font.size:
                r.font.size = pr.font.size
            r.font.bold = bool(pr.font.bold)
            try:
                if pr.font.color and pr.font.color.rgb:
                    r.font.color.rgb = pr.font.color.rgb
            except Exception:
                pass
        elif size:
            r.font.size = Pt(size)
            r.font.name = "X5 Sans"

def title_font_size(text, base_pt):
    n = max(len(l) for l in text.split("\n"))
    if n <= 14: return base_pt
    if n <= 24: return int(base_pt * 0.66)
    if n <= 34: return int(base_pt * 0.5)
    return int(base_pt * 0.4)

def fill_title(slide, deck_no, title, subtitle):
    sh = next(s for s in slide.shapes if s.has_text_frame and s.text_frame.text.strip())
    lines = [f"Урок {deck_no}", title.replace(" — ", "\n")]
    set_text(sh, lines, size=title_font_size(lines[1] if len(lines) > 1 else lines[0], 142))
    # подзаголовок пишем вторым блоком? на титуле один бокс — складываем в него же
    if subtitle:
        tf = sh.text_frame
        p = tf.add_paragraph()
        r = p.add_run(); r.text = ""
        p2 = tf.add_paragraph()
        r2 = p2.add_run(); r2.text = subtitle
        r2.font.size = Pt(28); r2.font.name = "X5 Sans"

def fill_stmt(slide, big, small=None):
    boxes = [s for s in slide.shapes if s.has_text_frame and s.text_frame.text.strip()]
    head, note = boxes[0], boxes[1] if len(boxes) > 1 else None
    txt = big.replace("\n", " ¶ ")
    set_text(head, [l.strip() for l in big.split("\n")], size=title_font_size(txt, 84))
    if note is not None:
        if small:
            set_text(note, small, size=30)
        else:
            set_text(note, "")

def fill_table_lines(slide, title, headers, rows):
    boxes = [s for s in slide.shapes if s.has_text_frame and s.text_frame.text.strip()]
    head, note = boxes[0], boxes[1]
    set_text(head, title, size=title_font_size(title, 84))
    # расширяем блок пояснения под «строки таблицы»
    note.left, note.top = Inches(0.6), Inches(2.6)
    note.width, note.height = Inches(18.8), Inches(7.6)
    lines = [" · ".join(headers)] if len(headers) <= 4 else []
    for row in rows:
        lines.append("  |  ".join(str(c) for c in row))
    set_text(note, lines, size=22)

def fill_bullets(slide, title, bullets, left_head=None, small=None):
    boxes = {s.shape_id: s for s in slide.shapes if s.has_text_frame and s.text_frame.text.strip()}
    # идентификаторы из шаблона: 5 title, 6 subtitle, 7 left-head, 8 left-body, 9 right-head, 11 right-list
    set_text(boxes[5], title, size=title_font_size(title, 54))
    set_text(boxes[6], small.split("\n")[0] if small else "", size=22)
    set_text(boxes[7], left_head or "", size=28)
    set_text(boxes[8], "", size=20)
    set_text(boxes[9], "", size=28)
    box = boxes[11]
    box.top, box.height = Inches(4.6), Inches(5.6)
    items = [b if len(b) <= 56 else b[:53] + "…" for b in bullets][:7]
    set_text(box, items, size=22)
    return box

def fill_stat(slide, number, label, note):
    boxes = {s.shape_id: s for s in slide.shapes if s.has_text_frame and s.text_frame.text.strip()}
    set_text(boxes[4], label if len(label) <= 26 else label[:24] + "…", size=54 if len(label) <= 16 else 40)
    set_text(boxes[5], note[0] if note else "", size=24)
    set_text(boxes[6], number, size=132 if len(number) <= 12 else 96)
    tail = [n for n in (note[1:] if note else [])][:3]
    set_text(boxes[7], tail, size=28)

def set_pagenum(slide, n):
    for sh in slide.shapes:
        if sh.has_text_frame and _norm(sh.text_frame.text).isdigit():
            set_text(sh, str(n))

def drop_slide(prs, idx):
    sld = list(prs.slides._sldIdLst)[idx]
    prs.part.drop_rel(sld.get(qn("r:id")))
    prs.slides._sldIdLst.remove(sld)

# ---------------------------------------------------------------- сборка
def build(num, title, subtitle, opener, slides, homework):
    prs = Presentation(str(BASE))
    carriers = list(prs.slides)          # 0 титул, 1 тезис, 2 список, 3 число

    made = []
    made.append(("title", carriers[0]))
    if opener:
        s = clone_slide(prs, carriers[2])
        fill_bullets(s, "Как прошла неделя?", opener, left_head="Что запомнили?")
        made.append(("bul", s))
    for sl in slides:
        kind = sl[0]
        if kind == "stmt":
            s = clone_slide(prs, carriers[1])
            fill_stmt(s, sl[1], sl[2] if len(sl) > 2 else None)
        elif kind == "stat":
            s = clone_slide(prs, carriers[3])
            fill_stat(s, sl[1], sl[2], sl[3] if len(sl) > 3 else None)
        elif kind == "bul":
            s = clone_slide(prs, carriers[2])
            foc = sl[3] if len(sl) > 3 else None
            fill_bullets(s, sl[1], sl[2], left_head=(foc[0] if foc else None),
                         small=(foc[1] if foc else None))
        elif kind == "tbl":
            s = clone_slide(prs, carriers[1])
            fill_table_lines(s, sl[1], sl[2], sl[3])
        else:
            continue
        made.append((kind, s))
    closing = clone_slide(prs, carriers[2])
    fill_bullets(closing, "Что дальше", homework, left_head="Домашнее задание")
    made.append(("bul", closing))

    # удаляем 4 оригинала-носителя (они в начале, индексы 0..3, клонов не касаемся:
    # клоны добавлены в конец) и выставляем порядок
    for idx in range(3, -1, -1):
        drop_slide(prs, idx)
    # порядок уже хронологический: title, opener, content..., closing
    for i, (_, s) in enumerate(made, 1):
        set_pagenum(s, i)
    path = OUT / f"Урок {num} — {title.split(' — ')[0].split(':')[0][:48]}.pptx"
    prs.save(str(path))
    return path

if __name__ == "__main__":
    for num, title, subtitle, opener, slides, hw in DECKS:
        print("ok", build(num, title, subtitle, opener, slides, hw).name)
    print("Готово:", len(DECKS), "презентаций X5 в", OUT)
