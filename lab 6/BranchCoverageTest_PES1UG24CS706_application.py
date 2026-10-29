"""Branch coverage tests for salon_booking.py.

Goal: every if/else decision in salon_booking.py goes both ways
(True and False) at least once.
"""
import pytest
from salon_booking import extra_time_charge, can_book, arrival_status


# ---------- extra_time_charge ----------

def test_unknown_service_raises():
    # service not in INCLUDED_MIN -> True
    with pytest.raises(ValueError):
        extra_time_charge("nails", 30, "junior", False)


def test_negative_duration_raises():
    # duration_min < 0 -> True
    with pytest.raises(ValueError):
        extra_time_charge("haircut", -5, "junior", False)


def test_within_included_time():
    # extra <= 0 -> True
    assert extra_time_charge("haircut", 20, "junior", False) == 0


def test_member_non_spa_gets_bonus():
    # is_member and service != "spa" -> True; 45 included, 5 extra x 10
    assert extra_time_charge("haircut", 50, "junior", True) == 50


def test_member_spa_gets_no_bonus():
    # is_member True but service is spa -> False; 90 included, 10 extra x 10
    assert extra_time_charge("spa", 100, "junior", True) == 100


def test_mid_level_under_60_extra():
    # not junior -> rate 18; extra > 60 -> False; 10 extra x 18
    assert extra_time_charge("colour", 70, "mid", False) == 180


def test_senior_over_60_extra():
    # extra > 60 -> True, senior -> True; 70 extra x (18 + 8 + 4)
    assert extra_time_charge("haircut", 100, "senior", False) == 2100


def test_junior_over_60_extra():
    # extra > 60 -> True, senior -> False; 70 extra x (10 + 8)
    assert extra_time_charge("haircut", 100, "junior", False) == 1260


# ---------- can_book ----------

def test_walk_in_small_party():
    # is_walk_in -> True, party <= 2
    assert can_book(2, 1, True) is True


def test_walk_in_large_party():
    # is_walk_in -> True, party > 2
    assert can_book(3, 1, True) is False


def test_party_too_large():
    # party_size > 4 -> True
    assert can_book(5, 1, False) is False


def test_can_book():
    # party_size > 4 -> False, services <= 2
    assert can_book(2, 1, False) is True


def test_too_many_services():
    # party_size > 4 -> False, services > 2
    assert can_book(2, 3, False) is False


# ---------- arrival_status ----------

def test_colour_weekday_open():
    # is_colour -> True, is_weekend -> False, >= cutoff -> True
    assert arrival_status(10, True, False) == "open"


def test_colour_weekday_late():
    # cutoff 10, 0 >= -5 -> late
    assert arrival_status(0, True, False) == "late"


def test_non_colour_late():
    # is_colour -> False, cutoff 5, 0 >= -10 -> late
    assert arrival_status(0, False, False) == "late"


def test_closed():
    # both checks False -> closed
    assert arrival_status(-20, False, False) == "closed"


def test_weekend_open():
    # is_weekend -> True, cutoff 15
    assert arrival_status(15, False, True) == "open"


def test_weekend_colour_closed():
    # cutoff 20, -10 < 5 -> closed
    assert arrival_status(-10, True, True) == "closed"
