# code-counter proof - closes the last detection/counter gap

Before this, code had detection (code_detector) but no counter. This adds it.

## What it does

SAFE mechanical counters (auto-applied):
- remove_redundant_comments: drops // comments that just restate the code
- remove_debug_console: strips console.log/info/debug (keeps error/warn)

Flagged for HUMAN review (not auto-fixed, because they change semantics):
- TODO/FIXME/HACK trails
- generic identifier renames (data, result, item, temp, ...)
- placeholder strings

## Result on nova page.tsx (4311 lines)

- removed 2 redundant comments + 2 debug console -> 4307 lines
- code_detector total stayed 0.05 (file was already clean - honest)
- generic_naming (0.16) remains, correctly flagged for human rename

## Why the delta is small here

nova's code was already clean (total 0.05). The counter removed what it safely
could; the leftover signal is generic naming, which a human must decide on.
That is the correct, honest behavior - not forcing a fake improvement.