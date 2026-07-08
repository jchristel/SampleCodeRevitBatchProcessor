# Handover — dRofus QA comparison

> Code has moved on since this was written. Treat file/line references as
> directional, not literal — re-locate the current comparison path before
> implementing. No code is reproduced here by design.

## Context

The QA comparison joins dRofus reference data onto Revit-pushed rooms and
flags per-field mismatches. A batch of mismatches turned out to be false
positives caused by character-encoding differences, not real data
disagreements.

## The problem (confirmed from a validation output file)

The Revit export is UTF-8. Any character in the Revit source that is **not
representable** during that export is replaced with a literal `?` (U+003F).
So a Revit room value can legitimately carry a `?` where the true character
was, e.g., an en dash `–` (U+2013).

dRofus keeps the original character (an en dash, a hyphen, an accented
letter, etc.). Result: the two strings differ **only** at that one glyph and
QA reports a mismatch, even though they refer to the same value.

Observed example (one of ~12 such rows):
- room side:   `... Loading Dock ? Option 2 ...`
- dRofus side: `... Loading Dock – Option 2 ...`

The information the Revit side lost is unrecoverable on the Revit side — once
it is `?`, the original character is gone. So the reconciliation has to
happen by degrading the dRofus side to match, not by trying to restore the
Revit side.

## Requested fix — two-pass string comparison

Apply this only to string-type field comparisons (not numeric, not date).

1. **Pass 1 — compare as-is.** If the room value and the dRofus value match
   under the existing string comparison, done: pass. No change to current
   behaviour for the common case.

2. **Pass 2 — only on a Pass-1 mismatch.** Check whether the dRofus string
   contains any character that the Revit UTF-8 export would have replaced
   (i.e. any character the export cannot represent). If it does, produce a
   normalized copy of the dRofus string with each such character replaced by
   `?`, then compare again against the room value. If this second comparison
   matches, treat the field as a **pass** (the mismatch was purely an
   export-substitution artefact).

If Pass 2 still mismatches, report the mismatch as today.

## Points to nail down before implementing

- **Which characters get replaced with `?`.** The rule must mirror exactly
  what the Revit exporter does when it cannot represent a character. Confirm
  the exporter's target character set / codepage so the server's "would this
  have become `?`" test matches the exporter's actual behaviour. If the two
  definitions drift, Pass 2 will either miss real artefacts or mask genuine
  mismatches. Get the exporter's encoding rule in writing rather than
  inferring it from samples.

- **Scope to strings only.** Numeric and date fields already have their own
  comparison paths (adaptive-precision numeric, typed date). The `?`
  normalization must not touch them.

- **Only run Pass 2 on mismatch.** Keep it off the hot path — the vast
  majority of comparisons pass on Pass 1, and Pass 2 does extra scanning per
  character. Do not normalize every value up front.

- **Report wording.** Decide whether a Pass-2 pass is silently a pass, or is
  surfaced as a pass-with-note (e.g. "matched after export-substitution
  normalization"). A note is useful because it flags Revit values that have
  actually lost characters, which someone may want to clean up at source even
  though QA no longer fails on them.

- **This is distinct from dash normalization.** Do NOT fold hyphen/en-dash
  equivalence into this fix. Here, both sides genuinely started with the same
  character and the Revit side lost it to `?`. A hyphen-vs-en-dash difference
  where neither side is `?` is a separate normalization question and is out
  of scope for this change.

## Explicitly out of scope

The following also appeared in the same validation output and are **genuine**
issues, NOT encoding artefacts. Do not address them under this change:

- `Building (Number)` mismatches where the room value is `None` (rooms
  missing the property).
- Duplicate link-value rows (`None` / blank link values).
- Real content mismatches (e.g. `RISER` vs `FIRE(W)`, `SM.EX` vs `MECH`).

## Suggested validation

- Take the ~12 `?`-bearing rows from the sample validation output and confirm
  each now passes under Pass 2.
- Confirm a genuine mismatch that merely happens to contain a `?` on the
  dRofus side (if any) still fails — i.e. Pass 2 only rescues rows where the
  `?`-normalized dRofus string equals the room string in full.
- Confirm numeric and date comparisons are untouched.
