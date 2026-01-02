import pytest

from gridironlabs.ui.widgets.rating_bars import RatingBarRow


@pytest.mark.qt
def test_rating_bar_row_single_and_dual_variants_have_stable_height(qtbot):
    single = RatingBarRow(label="Stuff", current=60)
    dual = RatingBarRow(label="Movement", current=65, potential=70)
    qtbot.addWidget(single)
    qtbot.addWidget(dual)

    assert single.property("ratingVariant") == "single"
    assert dual.property("ratingVariant") == "dual"
    assert single.height() == dual.height()

    dual.set_rating(current=40, potential=80)
    assert dual.property("ratingVariant") == "dual"
