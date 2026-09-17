# PSD read/write self-iteration

Do not leave retries only in this chat. Attempts that pass the gate must
become an official flag, a written rule, or a usage note.

This file is a generic protocol. It is not tied to any game project.
Never write host-project paths, furniture names, level names, or asset names.

## When it triggers

Run the promotion gate before wrap-up if any of these happened this turn:

- `psd_kit.py` ran 3 or more times
- The same flag family failed or was retried 2 or more times
- Ad-hoc Python or hand-edited binary did work that should be a first-class flag

After 2 failures in the same flag family, reread `SKILL.md` or `--help`
before a third try. Do not guess flags from memory.

## Landing (pick one)

| Landing | When |
|---|---|
| Official CLI flag | Missing a stable verb, structured output, exit code, or reusable layer stats |
| `references/` rule | Format trap, writable bound, color mode |
| This skill `SKILL.md` usage | Triggers, checklist, example commands |

Do not copy the same fact into script comments, a reference, and the README.

## Authorization

After the gate, this skill's `SKILL.md`, `references/`, and `scripts/` may
be updated directly. Host-project skills, a new standalone skill, or writing
business asset names into this repo still need user confirmation.

Keep each `.py` near 250 lines. Split new work by duty. Do not put parsing
into the CLI entry.

## Wrap-up report

Always print these four lines:

```text
PSD read/write self-iteration: <trigger>
Promotion landing: official flag / reference / SKILL.md / none
Files written:
Not written and why:
```

If the gate did not fire, write "No PSD read/write promotion this turn."
