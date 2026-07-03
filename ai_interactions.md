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

**Task compared:** the logic for rescheduling a **weekly** recurring task — i.e. when a
weekly task is completed, produce the next occurrence with the correct due date.

**Prompt used for both:** *"In my `Task` dataclass (fields: title, duration_minutes,
priority, frequency, due_date, completed), write a method that, when a weekly task is
completed, returns a new Task for the next occurrence with the due date advanced by one
week and completed reset to False. Keep it simple and avoid external libraries."*

> ⚠️ **Honesty note:** Option A below is Claude, which I actually used to build this
> project. I have **not yet** run the same prompt through a second model — the Option B
> column is a placeholder for me to fill in after I run Gemini / ChatGPT / Copilot on the
> identical prompt. I'm leaving it clearly marked rather than inventing another model's
> output.

| | Option A (used) | Option B (to run) |
|-|-----------------|-------------------|
| **Model / tool used** | Claude (Claude Code) | _TODO: e.g. Gemini / ChatGPT / Copilot_ |
| **Prompt** | (see prompt above) | (same prompt) |
| **Response summary** | Added `Task.is_recurring()` + `Task.next_occurrence()`. `next_occurrence` picks `timedelta(days=1)` for daily or `timedelta(weeks=1)` for weekly, adds it to `due_date` (falling back to `date.today()`), and returns a fresh `Task` with `completed=False`. A `Scheduler.complete_task(pet, task)` marks the task done and appends the new occurrence to the pet. | _TODO: paste the other model's answer_ |
| **What was useful** | Used only the standard-library `datetime`, correctly reset `completed`, and separated the pure "make the next task" step from the "add it to the pet" step. | _TODO_ |
| **Problems noticed** | It first based the next date on `date.today()`; I changed it to advance from the task's own `due_date` so a late-completed task still lands on the right weekly cadence. | _TODO_ |
| **Decision** | **Kept Option A** (with my due_date fix). | _TODO_ |

**Which approach did you use in your final implementation and why?**

I used the Claude version (Option A) because it stayed dependency-free and testable, and
after my one correction (advancing from `due_date` instead of `today`) it produced the
correct weekly cadence — which I verified with the
`test_weekly_task_regenerates_seven_days_later` test. To fully complete this stretch
feature I still need to run the same prompt through a second model and fill in Option B.
