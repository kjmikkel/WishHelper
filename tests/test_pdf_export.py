"""PDF export tests that assert on the *rendered* PDF (via pypdf) rather than
ReportLab's private flowable internals, so they survive ReportLab refactors."""

from io import BytesIO

from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate

from wishhelper.exporters.pdf import build_story, export_pdf
from wishhelper.models import Wish, WishList


def _render(wishlist) -> bytes:
    """Render the document's story to in-memory PDF bytes."""
    buf = BytesIO()
    SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    ).build(build_story(wishlist))
    return buf.getvalue()


def _pdf_text(wishlist) -> str:
    """Extracted, whitespace-normalized text from every page."""
    reader = PdfReader(BytesIO(_render(wishlist)))
    raw = " ".join(page.extract_text() or "" for page in reader.pages)
    return " ".join(raw.split())


def _pdf_uris(wishlist) -> list[str]:
    """URIs from link annotations (an <a href> renders as an annotation, not
    extractable text)."""
    reader = PdfReader(BytesIO(_render(wishlist)))
    uris = []
    for page in reader.pages:
        for annot in page.get("/Annots") or []:
            action = annot.get_object().get("/A")
            if action and action.get("/S") == "/URI":
                uris.append(action.get("/URI"))
    return uris


def sample():
    return WishList(event="jul", year=2026, include_year=True, currency="kr.",
                    author="Mikkel Kjær Jensen", wishes=[
        Wish(title="Tastatur", price=899, type="Elektronik",
             note="Brune switches", link="https://example.com/kb"),
        Wish(title="Spil", price=0, type="Spil",
             promise_ok=True, promise_reason="udkommer i marts 2027"),
    ])


def test_pdf_contains_heading():
    assert "Ønskeseddel til jul for 2026" in _pdf_text(sample())


def test_pdf_renders_link_as_annotation():
    assert "https://example.com/kb" in _pdf_uris(sample())
    assert "Tastatur" in _pdf_text(sample())


def test_pdf_inline_note_present():
    assert "Brune switches" in _pdf_text(sample())


def test_pdf_unknown_price_is_question_mark():
    assert "?" in _pdf_text(sample())


def test_pdf_promise_marker_present():
    assert "(løfte er fint — udkommer i marts 2027)" in _pdf_text(sample())


def test_export_pdf_writes_valid_pdf(tmp_path):
    path = tmp_path / "wishes.pdf"
    export_pdf(sample(), str(path))
    data = path.read_bytes()
    assert data[:5] == b"%PDF-"
    assert len(data) > 1000


def test_empty_wishlist_still_builds_pdf(tmp_path):
    # A wishlist with no items should still produce a valid PDF (header only).
    wl = WishList(event="jul", year=2026, include_year=True)
    assert "Ønskeseddel til jul for 2026" in _pdf_text(wl)
    path = tmp_path / "empty.pdf"
    export_pdf(wl, str(path))
    assert path.read_bytes()[:5] == b"%PDF-"
