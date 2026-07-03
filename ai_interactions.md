# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked the agent (Claude) to add a third algorithmic capability to my Scheduler for the optional
extensions: a `next_available_slot(tasks, duration_minutes)` method that finds the earliest open time
in the day where a new task of a given length would fit without overlapping any tasks that already
have a preferred time. This goes beyond my Phase 4 sorting/filtering/conflict logic because it
actually reasons about *gaps between* scheduled tasks.

**Files modified**

- `pawpal_system.py` — added the `Scheduler.next_available_slot()` method.
- `tests/test_pawpal.py` — added four tests for it.

**What did the agent do?**

It implemented the method as a small interval-packing algorithm: it builds a sorted list of
`(start, end)` intervals from the timed tasks, walks a cursor forward from `day_start`, returns the
first gap large enough for the requested duration, and returns `None` if the day runs out of room. It
then wrote tests for the empty-day case, a gap that fits, a gap that's too small (so the slot lands
later), and the no-room case, and ran `python -m pytest` to confirm all tests passed (24 total).

**What did you have to verify or fix manually?**

I checked the edge behavior myself rather than trusting it blindly. Two things I specifically verified:
(1) that a gap exactly equal to the requested duration counts as "fits" (I used `>=`, not `>`), and
(2) the end-of-day boundary — I made the method take a `day_end` argument and return `None` instead of
suggesting a slot that would run past the end of the day, so it warns rather than producing a bad time.
I confirmed both with the "too small gap" and "no room" tests before accepting the change.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
