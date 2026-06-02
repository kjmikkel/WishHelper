"""ReportLab PDF exporter for a WishList. Qt-free.

Inline notes (style B1): each item's note is shown under its name in a smaller,
muted paragraph. A `link` turns the item name into a clickable hyperlink. The
promise marker is appended inline after the name.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from wishhelper.formatting import format_price, heading, promise_marker
from wishhelper.i18n import t
from wishhelper.models import WishList

_styles = getSampleStyleSheet()

_TITLE = ParagraphStyle("WishTitle", parent=_styles["Title"], alignment=TA_CENTER)
_SUBTITLE = ParagraphStyle(
    "WishSubtitle", parent=_styles["Normal"], alignment=TA_CENTER,
    fontName="Helvetica-Oblique", textColor=colors.HexColor("#444444"),
    spaceAfter=14,
)
_ITEM = ParagraphStyle("WishItem", parent=_styles["Normal"], fontSize=11, leading=14)
_NOTE = ParagraphStyle(
    "WishNote", parent=_styles["Normal"], fontSize=9, leading=11,
    fontName="Helvetica-Oblique", textColor=colors.HexColor("#555555"),
    leftIndent=2,
)
_CELL = ParagraphStyle("WishCell", parent=_styles["Normal"], fontSize=11, leading=14)
_HEADER = ParagraphStyle(
    "WishHeader", parent=_styles["Normal"], fontSize=9,
    fontName="Helvetica-Bold", textColor=colors.HexColor("#666666"),
)


def _name_cell(wish: Wish) -> list:
    """Build the name cell: linked/plain title + promise marker, then note."""
    safe_title = escape(wish.title)
    if wish.link:
        # escape() already handles & < > ; the extra map adds " -> &quot; for the attribute value
        safe_link = escape(wish.link, {'"': "&quot;"})
        name_html = f'<a href="{safe_link}" color="#1558b0">{safe_title}</a>'
    else:
        name_html = safe_title
    name_html += escape(promise_marker(wish))
    flowables = [Paragraph(name_html, _ITEM)]
    if wish.note:
        flowables.append(Paragraph(escape(wish.note), _NOTE))
    return flowables


def build_story(wishlist: WishList) -> list:
    """Return the ordered list of ReportLab flowables for the document."""
    story = [
        Paragraph(escape(heading(wishlist)), _TITLE),
        Paragraph(escape(t("intro_line")), _SUBTITLE),
    ]
    if wishlist.author:
        story.append(Paragraph(escape(wishlist.author), _SUBTITLE))

    header = [
        Paragraph(escape(t("col_number")), _HEADER),
        Paragraph(escape(t("col_name")), _HEADER),
        Paragraph(escape(t("col_type")), _HEADER),
        Paragraph(escape(t("col_price")), _HEADER),
    ]
    rows = [header]
    for index, wish in enumerate(wishlist.wishes, start=1):
        rows.append([
            Paragraph(str(index), _CELL),
            _name_cell(wish),
            Paragraph(escape(wish.type), _CELL),
            Paragraph(escape(format_price(wish.price, wishlist.currency)), _CELL),
        ])

    table = Table(rows, colWidths=[1.2 * cm, 9.5 * cm, 3.5 * cm, 2.8 * cm])
    table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 1.2, colors.HexColor("#333333")),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, colors.HexColor("#e0e0e0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(Spacer(1, 6))
    story.append(table)
    return story


def export_pdf(wishlist: WishList, path: str) -> None:
    """Render the wishlist to a PDF file at `path`."""
    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=heading(wishlist),
        author=wishlist.author or "WishHelper",
    )
    doc.build(build_story(wishlist))
