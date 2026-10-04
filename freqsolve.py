#!/usr/bin/env python3
"""freqsolve.py — frequency analysis toolkit for classical cryptography.

Features
--------
1. Frequency table: counts letters (and optionally bigrams) in a text and
   prints a readable table with counts and percentages.
2. Caesar / shift solver: tries all 26 shifts and scores each against English
   letter frequencies with a chi-squared statistic, returning the best fit.
3. Monoalphabetic substitution starter: builds a first-guess key by matching
   ciphertext letters (most frequent first) to English letters (most frequent
   first), applies it, and prints the result for you to refine by hand.

Intended for breaking classical ciphers, coursework, and puzzle text.
"""

import argparse
import string
import sys
from collections import Counter

# Relative frequency of letters in typical English text, in percent.
ENGLISH_FREQ = {
    'a': 8.17, 'b': 1.49, 'c': 2.78, 'd': 4.25, 'e': 12.70, 'f': 2.23,
    'g': 2.02, 'h': 6.09, 'i': 6.97, 'j': 0.15, 'k': 0.77, 'l': 4.03,
    'm': 2.41, 'n': 6.75, 'o': 7.51, 'p': 1.93, 'q': 0.10, 'r': 5.99,
    's': 6.33, 't': 9.06, 'u': 2.76, 'v': 0.98, 'w': 2.36, 'x': 0.15,
    'y': 1.97, 'z': 0.07,
}

# English letters ordered from most to least frequent — used for the
# substitution first-guess mapping.
ENGLISH_ORDER = "etaoinshrdlcumwfgypbvkjxqz"


def letters_only(text):
    """Return just the alphabetic characters of text, lowercased."""
    return [c.lower() for c in text if c.isalpha()]


def frequency_table(text, top=None):
    """Build a frequency table of single letters.

    Returns a list of (letter, count, percent) sorted by count descending.
    """
    letters = letters_only(text)
    total = len(letters)
    counts = Counter(letters)
    rows = []
    for letter, count in counts.most_common():
        percent = (100.0 * count / total) if total else 0.0
        rows.append((letter, count, percent))
    if top is not None:
        rows = rows[:top]
    return rows, total


def print_frequency_table(text, top=None):
    rows, total = frequency_table(text, top=top)
    print(f"Total letters: {total}")
    print(f"{'char':>4} | {'count':>6} | {'percent':>7} | {'english':>7}")
    print("-" * 36)
    for letter, count, percent in rows:
        eng = ENGLISH_FREQ.get(letter, 0.0)
        print(f"{letter:>4} | {count:>6} | {percent:>6.2f}% | {eng:>6.2f}%")


def bigram_table(text, top=20):
    """Count adjacent letter pairs (within runs of letters)."""
    words = "".join(c.lower() if c.isalpha() else " " for c in text).split()
    counts = Counter()
    for word in words:
        for i in range(len(word) - 1):
            counts[word[i:i + 2]] += 1
    return counts.most_common(top)


def print_bigram_table(text, top=20):
    rows = bigram_table(text, top=top)
    print(f"\nTop {len(rows)} bigrams:")
    for pair, count in rows:
        print(f"  {pair} : {count}")


def shift_text(text, shift):
    """Apply a Caesar shift (decrypt by passing the negative, or 26-shift)."""
    out = []
    for c in text:
        if c.isupper():
            out.append(chr((ord(c) - 65 + shift) % 26 + 65))
        elif c.islower():
            out.append(chr((ord(c) - 97 + shift) % 26 + 97))
        else:
            out.append(c)
    return "".join(out)


def chi_squared(text):
    """Chi-squared distance of text's letter distribution from English.

    Lower is a better match to English.
    """
    letters = letters_only(text)
    total = len(letters)
    if total == 0:
        return float("inf")
    counts = Counter(letters)
    score = 0.0
    for letter in string.ascii_lowercase:
        observed = counts.get(letter, 0)
        expected = ENGLISH_FREQ[letter] / 100.0 * total
        if expected > 0:
            score += (observed - expected) ** 2 / expected
    return score


def solve_caesar(ciphertext):
    """Try all 26 shifts, score each, return (best_shift, best_plaintext, ranked).

    'shift' here is the value applied to the ciphertext to recover plaintext.
    """
    ranked = []
    for shift in range(26):
        candidate = shift_text(ciphertext, shift)
        ranked.append((shift, chi_squared(candidate), candidate))
    ranked.sort(key=lambda r: r[1])
    best_shift, _, best_plain = ranked[0]
    return best_shift, best_plain, ranked


def solve_substitution_by_frequency(ciphertext):
    """First-guess monoalphabetic substitution using frequency ranking.

    Maps the most frequent ciphertext letter to 'e', next to 't', and so on,
    following English letter order. This rarely solves a cipher outright but
    gives a readable starting point you can correct interactively.

    Returns (mapping, plaintext_guess).
    """
    counts = Counter(letters_only(ciphertext))
    cipher_order = [letter for letter, _ in counts.most_common()]

    mapping = {}
    for cipher_letter, plain_letter in zip(cipher_order, ENGLISH_ORDER):
        mapping[cipher_letter] = plain_letter

    out = []
    for c in ciphertext:
        if c.islower():
            out.append(mapping.get(c, c))
        elif c.isupper():
            out.append(mapping.get(c.lower(), c.lower()).upper())
        else:
            out.append(c)
    return mapping, "".join(out)


def read_input(args):
    if args.text is not None:
        return args.text
    if args.file is not None:
        with open(args.file, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    # Fall back to stdin so you can pipe text in.
    return sys.stdin.read()


def main():
    parser = argparse.ArgumentParser(
        description="Frequency analysis and classical-cipher solver."
    )
    parser.add_argument("-t", "--text", help="Text to analyze, inline.")
    parser.add_argument("-f", "--file", help="Read text from a file.")
    parser.add_argument("--top", type=int, default=None,
                        help="Show only the top N letters in the table.")
    parser.add_argument("--bigrams", action="store_true",
                        help="Also show a bigram frequency table.")
    parser.add_argument("--caesar", action="store_true",
                        help="Attempt an automatic Caesar/shift solve.")
    parser.add_argument("--substitution", action="store_true",
                        help="Print a frequency-ranked substitution first guess.")
    args = parser.parse_args()

    text = read_input(args)

    print("=== Letter frequency table ===")
    print_frequency_table(text, top=args.top)

    if args.bigrams:
        print_bigram_table(text)

    if args.caesar:
        print("\n=== Caesar / shift solve ===")
        best_shift, best_plain, ranked = solve_caesar(text)
        print(f"Best shift: {best_shift} (chi^2 = {ranked[0][1]:.2f})")
        print(f"Plaintext:  {best_plain}")
        print("\nRunner-up shifts:")
        for shift, score, _ in ranked[1:4]:
            print(f"  shift {shift:>2}: chi^2 = {score:.2f}")

    if args.substitution:
        print("\n=== Substitution first guess (frequency-ranked) ===")
        mapping, guess = solve_substitution_by_frequency(text)
        shown = ", ".join(f"{c}->{p}" for c, p in sorted(mapping.items()))
        print(f"Mapping: {shown}")
        print(f"\nGuess:\n{guess}")
        print("\nNote: refine the mapping by hand using the table and bigrams.")


if __name__ == "__main__":
    main()
