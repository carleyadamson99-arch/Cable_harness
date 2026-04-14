"""AWG lookup logic for the cable harness prototype."""


def get_awg(current: float) -> str:
    """Return a wire gauge based on the requested current."""
    if not isinstance(current, (int, float)):
        raise TypeError("Current must be a number.")

    if current <= 0:
        raise ValueError("Current must be greater than zero.")

    if current <= 5:
        return "22 AWG"
    if current <= 10:
        return "20 AWG"
    if current <= 15:
        return "18 AWG"
    if current <= 20:
        return "16 AWG"

    return "14 AWG"


def select_awg(current: float) -> str:
    """Backward-compatible wrapper for existing code paths."""
    return get_awg(current).split()[0]


if __name__ == "__main__":
    print(get_awg(3.0))
    print(get_awg(8.5))
    print(get_awg(14.0))
    print(get_awg(19.5))
    print(get_awg(25.0))
