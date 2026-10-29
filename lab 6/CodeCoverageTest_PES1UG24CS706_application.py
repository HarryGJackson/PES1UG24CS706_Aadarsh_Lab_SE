"""Code (line) coverage tests for salon_booking.py.

Goal: every line in salon_booking.py runs at least once.
"""
import pytest
from salon_booking import extra_time_charge, can_book, arrival_status


# ---------- extra_time_charge ----------

def test_unknown_service_raises():
    with pytest.raises(ValueError):
        extra_time_charge("nails", 30, "junior", False)


def test_negative_duration_raises():
    with pytest.raises(ValueError):
        extra_time_charge("haircut", -5, "junior", False)


def test_within_included_time():
    assert extra_time_charge("haircut", 20, "junior", False) == 0


def test_member_junior_small_extra():
    # member gets +15 min: 30 + 15 = 45 included, 5 extra x 10
    assert extra_time_charge("haircut", 50, "junior", True) == 50


def test_senior_over_60_extra():
    # 70 extra, rate 18 + 8 + 4 = 30
    assert extra_time_charge("haircut", 100, "senior", False) == 2100


# ---------- can_book ----------

def test_walk_in_small_party():
    assert can_book(2, 1, True) is True


def test_party_too_large():
    assert can_book(5, 1, False) is False


def test_can_book():
    assert can_book(2, 1, False) is True


# ---------- arrival_status ----------

def test_colour_weekday_open():
    assert arrival_status(10, True, False) == "open"


def test_non_colour_late():
    assert arrival_status(0, False, False) == "late"


def test_closed():
    assert arrival_status(-20, False, False) == "closed"


def test_weekend_open():
    assert arrival_status(15, False, True) == "open"
