from wishhelper.models import Wish, WishList


def test_wish_defaults():
    w = Wish(title="Bog")
    assert w.title == "Bog"
    assert w.price == 0
    assert w.type == ""
    assert w.note == ""
    assert w.link == ""
    assert w.promise_ok is False
    assert w.promise_reason == ""


def test_wishlist_defaults():
    wl = WishList()
    assert wl.event == ""
    assert wl.year == 0
    assert wl.include_year is True
    assert wl.author == ""
    assert wl.currency == "kr."
    assert wl.wishes == []


def test_wishlist_holds_wishes_in_order():
    wl = WishList(wishes=[Wish(title="A"), Wish(title="B")])
    assert [w.title for w in wl.wishes] == ["A", "B"]


def test_two_wishlists_do_not_share_wishes_list():
    a = WishList()
    b = WishList()
    a.wishes.append(Wish(title="X"))
    assert b.wishes == []
