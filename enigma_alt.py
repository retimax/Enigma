"""
enigma.py -- Enigma machine simulator.

Configuration from the handwritten diagram:
  Rotor I   : EKMFLGDQVZNTOWYHXUSPAIBRCJ  (notch Q)
  Rotor II  : AJDKSIRUXBLHWTMCQGZNPYFVOE  (notch E)
  Rotor III : BDFHJLCPRTXVZNYEIWGAKMUSQO  (notch V)
  Reflector : YRUHQSLDPXNGOKMIEBFZCWVJAT

Stepping mode: notch-by-value.
A rotor advances when the letter it outputs matches its notch.
Because this stepping mode is not its own inverse, decryption searches
all possible plaintexts and picks the one with the best letter frequency score.
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

NOTCH_I = "Q"
NOTCH_II = "E"
NOTCH_III = "V"

N = 26

# English letter frequencies for scoring decryption candidates
EN_FREQ = {
    "E": 0.127,
    "T": 0.091,
    "A": 0.082,
    "O": 0.075,
    "I": 0.070,
    "N": 0.067,
    "S": 0.063,
    "H": 0.061,
    "R": 0.060,
    "D": 0.043,
    "L": 0.040,
    "C": 0.028,
    "U": 0.028,
    "M": 0.024,
    "W": 0.024,
    "F": 0.022,
    "G": 0.020,
    "Y": 0.020,
    "P": 0.019,
    "B": 0.015,
    "V": 0.010,
    "K": 0.008,
    "J": 0.002,
    "X": 0.002,
    "Q": 0.001,
    "Z": 0.001,
}

# ---------------------------------------------------------------------------
# Core cipher
# ---------------------------------------------------------------------------


def _advance_if_match(pos: int, letter: str, notch: str) -> int:
    return (pos + 1) % N if letter == notch else pos


def _encipher_char(char: str, pos: list[int]) -> str:
    """
    Encipher one character (notch-by-value stepping).
    pos is modified in-place as rotors advance.
    """
    # Forward pass: Rotor I -> II -> III
    x = (ALPHABET.index(char) + pos[0]) % N
    v = ROTOR_I[x]
    pos[0] = _advance_if_match(pos[0], v, NOTCH_I)

    x = (ALPHABET.index(v) + pos[1]) % N
    v = ROTOR_II[x]
    pos[1] = _advance_if_match(pos[1], v, NOTCH_II)

    x = (ALPHABET.index(v) + pos[2]) % N
    v = ROTOR_III[x]
    pos[2] = _advance_if_match(pos[2], v, NOTCH_III)

    # Reflect
    v = REFLECTOR[ALPHABET.index(v)]

    # Backward pass: Rotor III -> II -> I
    # If a rotor advances here, the updated position is used immediately.
    x = ROTOR_III.index(v)
    pos[2] = _advance_if_match(pos[2], v, NOTCH_III)
    x = (x - pos[2]) % N
    v = ALPHABET[x]

    x = ROTOR_II.index(v)
    pos[1] = _advance_if_match(pos[1], v, NOTCH_II)
    x = (x - pos[1]) % N
    v = ALPHABET[x]

    x = ROTOR_I.index(v)
    pos[0] = _advance_if_match(pos[0], v, NOTCH_I)
    x = (x - pos[0]) % N

    return ALPHABET[x]


def _key_positions(key: str) -> list[int]:
    letters = [c for c in key.upper() if c in ALPHABET]
    if len(letters) < 3:
        raise ValueError("Key must contain at least 3 letters.")
    return [ALPHABET.index(k) for k in letters[:3]]


# ---------------------------------------------------------------------------
# Encrypt
# ---------------------------------------------------------------------------


def encrypt(message: str, key: str) -> str:
    """Encipher a message. Spaces are preserved; non-alphabet chars are ignored."""
    pos = _key_positions(key)
    result = []
    for char in message.upper():
        if char == " ":
            result.append(" ")
        elif char in ALPHABET:
            result.append(_encipher_char(char, pos))
    return "".join(result)


# ---------------------------------------------------------------------------
# Decrypt (brute-force search + frequency scoring)
# ---------------------------------------------------------------------------


def decrypt(ciphertext: str, key: str) -> str:
    """
    Decipher a message.

    Because notch-by-value stepping is not its own inverse, we search all
    possible plaintexts recursively and return the one that best matches
    English letter frequencies.
    """
    pos_init = _key_positions(key)
    chars = [c for c in ciphertext.upper() if c in ALPHABET]
    spaces = {i: c for i, c in enumerate(ciphertext.upper()) if c == " "}

    candidates: list[str] = []

    def search(idx: int, pos: list[int], current: str) -> None:
        if idx == len(chars):
            candidates.append(current)
            return
        target = chars[idx]
        for p in ALPHABET:
            pos_try = list(pos)
            if _encipher_char(p, pos_try) == target:
                search(idx + 1, pos_try, current + p)

    search(0, pos_init, "")

    if not candidates:
        return ""

    best = max(candidates, key=lambda s: sum(EN_FREQ.get(c, 0.001) for c in s))

    # Re-insert spaces at their original positions
    result = list(best)
    for i, sp in sorted(spaces.items()):
        result.insert(i, sp)
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
            if op == "c":
                result = encrypt(message, key)
                success("Encrypted", result)
            else:
                result = decrypt(message, key)
                if result:
                    success("Decrypted", result)
                else:
                    show_error("Could not decrypt message.")
        except ValueError as e:
            show_error(str(e))

        pause()


if __name__ == "__main__":
    main()
