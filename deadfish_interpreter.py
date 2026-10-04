"""
Deadfish esolang interpreter.

Commands (all other characters in the source are ignored, so whitespace,
comments, newlines etc. are safe):
  i - increment accumulator
  d - decrement accumulator
  s - square accumulator
  o - output accumulator (collected as a number; also attempted as ASCII)

Classic Deadfish rule: after ANY i/d/s operation, if the accumulator
becomes -1 or 256, it resets to 0. This prevents negative numbers and
caps overflow. Getting this exactly right matters -- miss it and your
decoded numbers (and therefore ASCII string) will desync from the
correct values.

Usage: python3 deadfish_interpreter.py <path_to_codex_file>
"""
import sys

def run_deadfish(source):
    x = 0
    outputs = []
    for ch in source:
        if ch == 'i':
            x += 1
        elif ch == 'd':
            x -= 1
        elif ch == 's':
            x = x * x
        elif ch == 'o':
            outputs.append(x)
            continue  # output doesn't change x, skip the reset check below
        else:
            continue  # ignore any non-command character

        # classic Deadfish overflow/underflow reset rule
        if x == -1 or x == 256:
            x = 0

    return outputs

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 deadfish_interpreter.py <path_to_codex_file>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        source = f.read()

    outputs = run_deadfish(source)

    print(f"Number of 'o' (output) commands executed: {len(outputs)}")
    print(f"Raw output values: {outputs}")
    print()

    # Attempt 1: treat each output value directly as an ASCII code
    ascii_attempt = ''
    for v in outputs:
        if 0 <= v <= 1114111:  # valid unicode codepoint range, generous
            try:
                ascii_attempt += chr(v)
            except ValueError:
                ascii_attempt += '?'
        else:
            ascii_attempt += '?'
    print(f"Attempt A -- each output value as a direct ASCII/unicode char:")
    print(f"  {ascii_attempt!r}")
    print()

    # Attempt 2: just print the numbers space-separated, in case the
    # flag is literally the numbers themselves or needs another decode step
    print(f"Attempt B -- raw numbers space-separated (in case further decoding needed):")
    print(' '.join(str(v) for v in outputs))

if __name__ == '__main__':
    main()
