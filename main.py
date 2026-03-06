"""
enigma.py -- Enigma machine simulator.

Configuration from the handwritten diagram:
  Rotor I   : EKMFLGDQVZNTOWYHXUSPAIBRCJ  (notch Q)
  Rotor II  : AJDKSIRUXBLHWTMCQGZNPYFVOE  (notch E)
  Rotor III : BDFHJLCPRTXVZNYEIWGAKMUSQO  (notch V)
  Reflector : YRUHQSLDPXNGOKMIEBFZCWVJAT
  Alphabet  : A-Z (index 0-25)

Stepping mode: standard (historical).
The right rotor steps on every keypress. When it reaches its notch position
it pushes the middle rotor, which in turn pushes the left rotor.
The double-stepping anomaly of the original machine is included.

Because Enigma is its own inverse, encrypt and decrypt are the same operation.
"""

import os

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

ROTOR_I = list("EKMFLGDQVZNTOWYHXUSPAIBRCJ")
ROTOR_II = list("AJDKSIRUXBLHWTMCQGZNPYFVOE")
ROTOR_III = list("BDFHJLCPRTXVZNYEIWGAKMUSQO")
REFLECTOR = list("YRUHQSLDPXNGOKMIEBFZCWVJAT")

NOTCH_I = "Q"  # Rotor I   triggers middle rotor when passing Q
NOTCH_II = "E"  # Rotor II  triggers left   rotor when passing E
NOTCH_III = "V"  # Rotor III triggers middle rotor when passing V

N = 26

# ---------------------------------------------------------------------------
# Rotor stepping
# ---------------------------------------------------------------------------


def _step(pos: list[int]) -> None:
    """
    Advance rotor positions in-place. pos = [left, middle, right].

    Standard Enigma stepping with double-stepping anomaly:
    - Right rotor steps on every keypress.
    - Middle rotor steps when right is at its notch, OR when middle itself
      is at its notch (double-step).
    - Left rotor steps when middle is at its notch.
    """
    at_mid = ALPHABET[pos[1]] == NOTCH_II
    at_right = ALPHABET[pos[2]] == NOTCH_III

    pos[2] = (pos[2] + 1) % N
    if at_right or at_mid:
        pos[1] = (pos[1] + 1) % N
    if at_mid:
        pos[0] = (pos[0] + 1) % N


# ---------------------------------------------------------------------------
# Signal path
# ---------------------------------------------------------------------------


def _forward(rotor: list[str], idx: int, offset: int) -> int:
    """Right-to-left pass through one rotor."""
    return ALPHABET.index(rotor[(idx + offset) % N])


def _backward(rotor: list[str], idx: int, offset: int) -> int:
    """Left-to-right return pass (inverse substitution)."""
    return (rotor.index(ALPHABET[idx]) - offset) % N


def _encipher_char(char: str, pos: list[int]) -> str:
    """Step rotors, then pass the signal through the full machine."""
    _step(pos)

    idx = ALPHABET.index(char)
    idx = _forward(ROTOR_I, idx, pos[0])
    idx = _forward(ROTOR_II, idx, pos[1])
    idx = _forward(ROTOR_III, idx, pos[2])
    idx = ALPHABET.index(REFLECTOR[idx])  # reflect
    idx = _backward(ROTOR_III, idx, pos[2])
    idx = _backward(ROTOR_II, idx, pos[1])
    idx = _backward(ROTOR_I, idx, pos[0])

    return ALPHABET[idx]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def process(message: str, key: str) -> str:
    """
    Encipher or decipher a message (same operation for both).

    Key: first 3 valid letters set the starting position of each rotor
         (left, middle, right).
    Spaces are preserved. Non-alphabet characters are ignored.
    """
    key_letters = [c for c in key.upper() if c in ALPHABET]
    if len(key_letters) < 3:
        raise ValueError("Key must contain at least 3 letters.")

    pos = [ALPHABET.index(k) for k in key_letters[:3]]

    result = []
    for char in message.upper():
        if char == " ":
            result.append(" ")
        elif char in ALPHABET:
            result.append(_encipher_char(char, pos))

    return "".join(result)


# ---------------------------------------------------------------------------
# Colors (ANSI)
# ---------------------------------------------------------------------------


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    YELLOW = "\033[93m"


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

BANNER = r"""
+-----------------------------------------------------------------------+
|                                                                       |
|   +-+-+-+-+-+-+                                                       |
|   |E|N|I|G|M|A|                                                       |
|   +-+-+-+-+-+-+                                                       |
|                                                                       |
|    _______  __    __   __    _______  __   __   __  ______           |
|   |   ____||  \  |  | |  |  /  _____||  \ |  | |  ||      \          |
|   |  |__   |   \ |  | |  | /  /  ___ |   \|  | |  ||   _   \        |
|   |   __|  |  . `|  | |  ||  |  |_  ||  . `  | |  ||  | \   \       |
|   |  |____ |  |\   | |  | \  \__/  / |  |\   | |  ||  |  \   \      |
|   |_______||__| \__| |__|  \_______/  |__| \__| |__||__|   \__/      |
|                                                                       |
|                     C I P H E R   M A C H I N E                      |
+-----------------------------------------------------------------------+
"""


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def banner() -> None:
    print(C.CYAN + C.BOLD + BANNER + C.RESET)


def divider() -> None:
    print(C.GRAY + "\n  " + "-" * 50 + C.RESET)


def info(msg: str) -> None:
    print(C.GRAY + f"  {msg}" + C.RESET)


def warn(msg: str) -> None:
    print(C.YELLOW + f"  ! {msg}" + C.RESET)


def show_error(msg: str) -> None:
    print(C.RED + f"  ! {msg}" + C.RESET)


def success(label: str, value: str) -> None:
    print(
        C.GREEN
        + C.BOLD
        + f"\n  {label}: "
        + C.RESET
        + C.WHITE
        + C.BOLD
        + value
        + C.RESET
    )


def ask_option(label: str) -> str:
    return (
        input(C.CYAN + f"  {label} " + C.GRAY + "> " + C.RESET).strip().lower()
    )


def ask_input(label: str) -> str:
    return input(C.CYAN + f"  {label}: " + C.RESET).strip()


def pause() -> None:
    input(C.GRAY + "\n  [Enter] " + C.RESET)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    while True:
        clear()
        banner()
        divider()
        info("(c) encrypt    (d) decrypt    (q) quit")
        print()

        op = ask_option("Operation")

        if op == "q":
            divider()
            info("Goodbye.")
            print()
            break

        if op not in ("c", "d"):
            warn("Enter c, d, or q.")
            pause()
            continue

        message = ask_input("Message")
        if not message:
            warn("Message cannot be empty.")
            pause()
            continue

        key = ask_input("Key (min. 3 letters)")
        if not key:
            warn("Key cannot be empty.")
            pause()
            continue

        try:
            result = process(message, key)
            label = "Encrypted" if op == "c" else "Decrypted"
            success(label, result)
        except ValueError as e:
            show_error(str(e))

        pause()


if __name__ == "__main__":
    main()
