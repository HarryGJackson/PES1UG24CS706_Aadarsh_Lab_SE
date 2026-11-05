import math

MAX_MINUTES = 24 * 60        # a single booking can't be longer than a day
MAX_AMOUNT = 10_000_000      # upper limit for a bill or discount
MAX_INPUT_LEN = 10_000       # reject absurdly long input (DoS protection)
GST_RATE = 1.18


def _to_number(text):
    """Convert text to a finite float, or return None if it isn't a valid number."""
    try:
        value = float(text.strip())
    except (ValueError, OverflowError):
        return None
    if not math.isfinite(value):  # rejects 'nan', 'inf', '-inf'
        return None
    return value


def _is_valid_text(text):
    return isinstance(text, str) and 0 < len(text) <= MAX_INPUT_LEN


def parse_booking(text):
    """Parse 'service:minutes' into (Service, minutes). Returns None if invalid."""
    if not _is_valid_text(text) or text.count(':') != 1:
        return None

    service, minutes = text.split(':')
    service = service.strip()
    if not service:
        return None

    minutes = _to_number(minutes)
    if minutes is None or not (0 < minutes <= MAX_MINUTES):
        return None

    return service.title(), minutes


def duration_average(durations_csv):
    """Average of comma-separated whole-minute durations. Returns None if invalid."""
    if not _is_valid_text(durations_csv):
        return None

    values = []
    for part in durations_csv.split(','):
        part = part.strip()
        # only plain ASCII digits, so things like '١٢', '1_0' or '+5' are rejected
        if not (part.isascii() and part.isdigit()):
            return None
        value = int(part)
        if not (0 < value <= MAX_MINUTES):
            return None
        values.append(value)

    if not values:
        return None
    return round(sum(values) / len(values), 2)


def payable_bill(text):
    """Bill with 18% GST minus discount, never below 0. Returns None if invalid."""
    if not _is_valid_text(text) or text.count('|') != 1:
        return None

    bill, discount = text.split('|')
    bill = _to_number(bill)
    discount = _to_number(discount)
    if bill is None or discount is None:
        return None
    if not (0 <= bill <= MAX_AMOUNT and 0 <= discount <= MAX_AMOUNT):
        return None

    total = bill * GST_RATE - discount
    return round(max(total, 0), 2)


def main():
    print("==== Running parse_booking ====")
    user_input = input("Enter service:duration in min (e.g. haircut:45): ")
    result = parse_booking(user_input)
    if result is None:
        print("Invalid input. Use the format service:minutes, e.g. haircut:45")
    else:
        print("Service and Duration:", result)

    print("\n==== Running duration_average ====")
    user_input = input("Enter durations as CSV (e.g. 30,45,60): ")
    result = duration_average(user_input)
    if result is None:
        print("Invalid input. Use positive whole numbers separated by commas, e.g. 30,45,60")
    else:
        print("Average Duration:", result)

    print("\n==== Running payable_bill ====")
    user_input = input("Enter bill|discount (e.g. 800|100): ")
    result = payable_bill(user_input)
    if result is None:
        print("Invalid input. Use the format bill|discount with non-negative numbers, e.g. 800|100")
    else:
        print("Payable Bill:", result)


if __name__ == "__main__":
    main()
