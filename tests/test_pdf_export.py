from reportlab.platypus import Paragraph, Table

from wishhelper.exporters.pdf import build_story, export_pdf
from wishhelper.models import Wish, WishList


def _paragraph_texts(story):
    texts = []
    for flowable in story:
        if isinstance(flowable, Paragraph):
            texts.append(flowable.text)
        elif isinstance(flowable, Table):
            for row in flowable._cellvalues:
                for cell in row:
                    items = cell if isinstance(cell, list) else [cell]
                    for item in items:
                        if isinstance(item, Paragraph):
                            texts.append(item.text)
    return texts


def sample():
    return WishList(event="jul", year=2026, include_year=True, currency="kr.",
                    author="Mikkel Kjær Jensen", wishes=[
        Wish(title="Tastatur", price=899, type="Elektronik",
             note="Brune switches", link="https://example.com/kb"),
        Wish(title="Spil", price=0, type="Spil",
             promise_ok=True, promise_reason="udkommer i marts 2027"),
    ])


def test_story_contains_heading():
    texts = " ".join(_paragraph_texts(build_story(sample())))
    assert "Ønskeseddel til jul for 2026" in texts


def test_story_renders_link_as_anchor():
    texts = " ".join(_paragraph_texts(build_story(sample())))
    assert '<a href="https://example.com/kb"' in texts
    assert "Tastatur" in texts


def test_story_inline_note_present():
    texts = " ".join(_paragraph_texts(build_story(sample())))
    assert "Brune switches" in texts


def test_story_unknown_price_is_question_mark():
    texts = " ".join(_paragraph_texts(build_story(sample())))
    assert "?" in texts


def test_story_promise_marker_present():
    texts = " ".join(_paragraph_texts(build_story(sample())))
    assert "(løfte er fint — udkommer i marts 2027)" in texts


def test_export_pdf_writes_valid_pdf(tmp_path):
    path = tmp_path / "wishes.pdf"
    export_pdf(sample(), str(path))
    data = path.read_bytes()
    assert data[:5] == b"%PDF-"
    assert len(data) > 1000
