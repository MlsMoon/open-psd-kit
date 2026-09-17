# PSD read/write self-iteration

Do not leave retries only in this chat. Attempts that pass the gate must
become an official flag, a written rule, or a usage note.

This file is a generic protocol. It is not tied to any game project.
Never write host-project paths, furniture names, level names, or asset names.

## When to evaluate

Run the gate before wrap-up if any of these happened this turn.
Also run it at the end of a durable-task stage.

- `psd_kit.py` ran 3 or more times
- The same flag family failed or was retried 2 or more times
- Ad-hoc Python, a one-off Pillow script, or a hand-edited binary did
  work that should be a first-class flag
- This skill or `--help` disagrees with the actual CLI result

If none of these happened, write "No PSD read/write promotion this turn."
Do not invent a candidate.

In-session: after 2 failures in the same flag family, reread `SKILL.md`
or `--help` before a third try. Do not guess flags from memory.

## Gate

All of these must be true:

1. Verified with a real CLI result: exit 0, or a stable non-zero reason
   on stderr
2. Reusable: a future similar task will need it, or this turn only
   succeeded after repeating the same exploration 2 or more times
3. Can be written as one stable intent with no session file names,
   PIDs, or drive-letter paths
4. An existing flag, `references/` rule, or `SKILL.md` usage does not
   already cover it correctly

Skip and write nowhere if any of these is true:

- One-off debug, unverified guess, or chat log
- A transient retry that then succeeded, with no new contract
- Host-project paths, furniture names, or business asset names
- A rule that is already recorded (do not copy it a second time)

## Landing (pick one)

After the gate, pick exactly one landing. Do not write the same fact
into the script, a reference, and the README.

Match the first row that fits:

| Signal | Landing | Example |
|---|---|---|
| Missing a stable verb, structured `--json`, exit code, or reusable layer stats | Official CLI flag | `stack` instead of a throwaway Pillow script |
| Format trap, writable bound, color mode, name encoding | `references/` rule | Pascal name plus Unicode name on replace |
| Trigger, checklist, or example command | This skill `SKILL.md` usage | `inspect` then `layers --tree` |
| Transient failure with no new contract | None | A one-time file-not-found |

A linear sequence of existing commands that will be reused as a whole
may become `references/recipes/<id>.md`. Do not invent a batch runner.
If the sequence already lives in `SKILL.md`, do not copy it.

## Authorization

| Action | Authority |
|---|---|
| Update this skill's `SKILL.md`, `references/`, and `scripts/` | Do it after the gate |
| Same-family promotion: ad-hoc Python to an official flag | Do it after the gate |
| Host-project skill, a new standalone skill, or business asset names | User confirmation |

Same-family means the CLI already reads or writes PSD/PSB and only
lacks a verb, flag, JSON shape, or exit-code contract. It is not a
new product.

## How to add an official flag

1. Add a subparser in `scripts/psd_kit.py`
2. Implement it in `psd_inspect.py`, `psd_export.py`, or `psd_mutate.py`
3. Keep each `.py` near 250 lines. Split by duty. Do not parse in the
   CLI entry
4. Human summary by default; `--json` on UTF-8 stdout; non-zero exit
   with the reason on stderr
5. Writes go to `--out` unless `--in-place` is explicit
6. Add one example in `SKILL.md` only when the usage is new
7. Never write host-project paths or asset names into this repo

## How to write a rule

- Record the current contract, not a migration memoir or this-turn log
- Put format traps in `references/psd-format.md` or
  `references/write-limits.md`
- Put usage in `SKILL.md`
- UTF-8 without BOM, LF, trailing newline
- No drive-letter paths, PIDs, or session IDs

## Wrap-up report

Always print these four lines:

```text
PSD read/write self-iteration: <trigger>
Gate: pass / skip (<reason>)
Promotion landing: official flag / reference / SKILL.md / recipe / none
Files written:
```

If the gate did not fire, write "No PSD read/write promotion this turn."

## Checklist

- [ ] Decided whether evaluation triggered; if not, said so
- [ ] After two failures, reread `--help` instead of guessing a third time
- [ ] A passed attempt used exactly one landing
- [ ] Host-project paths and asset names stayed out of this repo
- [ ] Transient errors were not written into the skill
