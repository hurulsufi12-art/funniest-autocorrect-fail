"""Funniest Autocorrect Fail — entry program.

Writes one line (1-199 chars) to /output/entry.txt: a message as sent,
with an autocorrect fail in it. Stdlib only, deterministic.

The line targets the judge brief in order: it IS the fail (the message as
sent, not a story about a fail); the wrong word is clear and surprising
("Easter" became "yeast infection"); it reads as a real slip — the panicked
in-line correction ("I mean Easter. EASTER.") and "Please delete this." are
exactly how a real person reacts; the joke needs no explanation; and the
wrong word is specific and original, not a generic typo.
"""
import os

TEXT = (
    "Grandma, I can't wait to visit for my yeast infection this weekend. "
    "I mean Easter. EASTER. Please delete this."
)


def main():
    # Enforce the scorer's gate (RULES.txt): UTF-8, 1-199 chars (NOT 200),
    # one line, not whitespace-only. Fail loudly instead of writing an
    # invalid entry. Also refuse control characters: a stray \x00-\x1f
    # would fail the scorer's UTF-8 text check.
    if not 1 <= len(TEXT) <= 199 or "\n" in TEXT or not TEXT.strip():
        raise SystemExit("entry text violates the 1-199 char single-line gate")
    if any(ord(c) < 0x20 for c in TEXT):
        raise SystemExit("entry text contains a control character")
    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    # Write atomically: a crash mid-write must never leave a truncated
    # entry.txt for the grader to read. Write to a temp file in the same
    # directory, flush it to disk, then rename over the target.
    # Temp name carries the pid so two concurrent grader runs in the same
    # directory never overwrite each other's in-flight file.
    tmp_path = os.path.join(out_dir, f".entry.txt.tmp.{os.getpid()}")
    final_path = os.path.join(out_dir, "entry.txt")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(TEXT)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    # Read back and verify: the file the grader reads must be byte-identical
    # to the gated text. Fail loudly instead of shipping a corrupt entry.
    with open(final_path, encoding="utf-8") as f:
        if f.read() != TEXT:
            raise SystemExit("entry.txt read-back mismatch after atomic write")


if __name__ == "__main__":
    main()
