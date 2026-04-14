"""AWG lookup logic for the cable harness prototype."""

AWG_ORDER = ["22 AWG", "20 AWG", "18 AWG", "16 AWG", "14 AWG"]


def get_awg(current: float) -> str:
    """Return a wire gauge based on the requested current."""
    if not isinstance(current, (int, float)):
        raise TypeError("Current must be a number.")

    if current <= 0:
        raise ValueError("Current must be greater than zero.")

    # This replaces the manual step of checking a current-vs-AWG reference chart.
    if current <= 5:
        return "22 AWG"
    if current <= 10:
        return "20 AWG"
    if current <= 15:
        return "18 AWG"
    if current <= 20:
        return "16 AWG"

    return "14 AWG"


def bump_awg_size(awg: str) -> str:
    """Return the next larger wire size when available."""
    if awg not in AWG_ORDER:
        raise ValueError(f"Unknown AWG value: {awg}")

    index = AWG_ORDER.index(awg)
    if index == len(AWG_ORDER) - 1:
        return awg

    return AWG_ORDER[index + 1]


def get_design_awg(current: float, length: float) -> tuple[str, str]:
    """Return an AWG recommendation adjusted for longer cable runs."""
    if not isinstance(length, (int, float)):
        raise TypeError("Length must be a number.")

    if length <= 0:
        raise ValueError("Length must be greater than zero.")

    base_awg = get_awg(current)

    # For longer runs, recommend one larger wire size to reduce voltage drop risk.
    if length > 15:
        adjusted_awg = bump_awg_size(base_awg)
        if adjusted_awg != base_awg:
            return adjusted_awg, "AWG increased for longer cable run"

    return base_awg, ""


def select_awg(current: float) -> str:
    """Backward-compatible wrapper for existing code paths."""
    return get_awg(current).split()[0]


if __name__ == "__main__":
    print(get_awg(3.0))
    print(get_awg(8.5))
    print(get_awg(14.0))
    print(get_awg(19.5))
    print(get_awg(25.0))
