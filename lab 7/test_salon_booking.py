import math

from hypothesis import given, settings, strategies as st
from salon_booking import parse_booking, duration_average, payable_bill


# ---------- Fuzz tests: random / malformed input must never crash ----------

@settings(max_examples=500)
@given(st.text() | st.none())
def test_parse_booking_no_crash(s):
    try:
        parse_booking(s)
    except Exception as e:
        assert False, f"parse_booking crashed on {s!r} with: {type(e).__name__}: {e}"


@settings(max_examples=500)
@given(st.text() | st.none())
def test_duration_average_no_crash(s):
    try:
        duration_average(s)
    except Exception as e:
        assert False, f"duration_average crashed on {s!r} with: {type(e).__name__}: {e}"


@settings(max_examples=500)
@given(st.text() | st.none())
def test_payable_bill_no_crash(s):
    try:
        payable_bill(s)
    except Exception as e:
        assert False, f"payable_bill crashed on {s!r} with: {type(e).__name__}: {e}"


# ---------- Property tests: well-formed input must give sensible results ----------

service_names = st.text(
    alphabet=st.characters(whitelist_categories=("Ll", "Lu"), max_codepoint=127),
    min_size=1,
    max_size=20,
)


@given(service_names, st.integers(min_value=1, max_value=600))
def test_parse_booking_valid_input(service, minutes):
    result = parse_booking(f"{service}:{minutes}")
    assert result == (service.title(), float(minutes))


@given(st.lists(st.integers(min_value=1, max_value=600), min_size=1, max_size=20))
def test_duration_average_valid_input(durations):
    result = duration_average(",".join(map(str, durations)))
    # the average must lie between the smallest and largest duration
    assert min(durations) <= result <= max(durations)
    assert math.isclose(result, sum(durations) / len(durations), abs_tol=0.01)


@given(
    st.integers(min_value=0, max_value=100_000),
    st.integers(min_value=0, max_value=100_000),
)
def test_payable_bill_valid_input(bill, discount):
    result = payable_bill(f"{bill}|{discount}")
    assert result is not None
    assert math.isfinite(result)
    assert result >= 0
