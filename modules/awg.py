"""AWG lookup logic for the cable harness prototype."""

# Ordered from smallest supported conductor to largest supported conductor.
AWG_ORDER = ["22 AWG", "20 AWG", "18 AWG", "16 AWG", "14 AWG"]

# Phase 3/4 uses the local engineering reference values rather than the
# original placeholder thresholds. If a requested current exceeds the
# largest supported wire in the prototype data, the tool should flag it
# instead of returning a misleading gauge.
AWG_AMPACITY_LIMITS = {
    "22 AWG": 4.5,
    "20 AWG": 6.5,
    "18 AWG": 9.2,
    "16 AWG": 13.0,
    "14 AWG": 19.0,
}


def get_awg(current: float) -> str:
    """Return a wire gauge based on the requested current."""
    if not isinstance(current, (int, float)):
        raise TypeError("Current must be a number.")

    if current <= 0:
        raise ValueError("Current must be greater than zero.")

    # This replaces the manual step of checking a current-vs-AWG reference chart.
    for awg in AWG_ORDER:
        if current <= AWG_AMPACITY_LIMITS[awg]:
            return awg

    max_supported_current = AWG_AMPACITY_LIMITS[AWG_ORDER[-1]]
    raise ValueError(
        "Current exceeds the supported prototype range. "
        f"The largest available wire is 14 AWG at {max_supported_current:.1f} A."
    )


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
    try:
        print(get_awg(25.0))
    except ValueError as error:
        print(error)
