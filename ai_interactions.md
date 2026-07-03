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

I ran the **two-prompt** version of this comparison (which the rubric allows): the same
task given to Claude with a vague prompt vs. a detailed, spec-driven prompt. The point was
to see how much prompt specificity changes the quality of the generated code.

**Prompt A (vague):** *"Write a method to reschedule a weekly recurring task to next week."*

Claude produced something like:

```python
def reschedule_weekly(self):
    from datetime import datetime, timedelta
    self.due_date = datetime.now() + timedelta(days=7)
    self.completed = False
```

**Prompt B (detailed / spec-driven):** *"In my `Task` dataclass (fields: title,
duration_minutes, priority, frequency, due_date, completed), write a method that returns a
**new** Task for the next occurrence with the due date advanced by one week (or one day if
daily) and `completed` reset to False. Base the new date on the task's own `due_date`, guard
against non-recurring tasks, and avoid external libraries."*

Claude produced (essentially my shipped code):

```python
def next_occurrence(self):
    if not self.is_recurring():
        return None
    step = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
    base = self.due_date or date.today()
    return Task(title=self.title, duration_minutes=self.duration_minutes,
                priority=self.priority, category=self.category,
                preferred_time=self.preferred_time, frequency=self.frequency,
                due_date=base + step, completed=False)
```

| | Option A — vague prompt | Option B — detailed prompt |
|-|-------------------------|----------------------------|
| **Model / tool used** | Claude | Claude |
| **Response summary** | A one-method in-place update: sets `due_date` to `datetime.now() + 7 days` and clears `completed`. | A pure `next_occurrence()` that returns a *new* Task advanced from the task's own `due_date`, handles daily vs. weekly, and guards non-recurring tasks. |
| **What was useful** | Short and immediately readable; captures the basic "+7 days, un-complete" idea. | Keeps the completed occurrence intact (returns a new object), correct cadence from `due_date`, handles both frequencies, dependency-free. |
| **Problems noticed** | (1) Uses `datetime.now()` — a `datetime`, not a `date`, and ignores the task's real due date, so a late completion drifts the schedule. (2) Mutates in place, losing the record that the current occurrence was done. (3) No daily/weekly distinction; no guard for one-off tasks. | More code to write, and it needed a companion `Scheduler.complete_task()` to actually attach the new task to the pet. |
| **Decision** | Rejected. | **Kept** — became `Task.next_occurrence()` + `Scheduler.complete_task()`. |

**Which approach did you use in your final implementation and why?**

I used Option B. The vague prompt gave me code that *looked* fine but had two real bugs I
didn't want (`datetime.now()` instead of the task's `due_date`, and in-place mutation that
throws away the completed occurrence). Writing a more specific prompt — naming the fields,
asking for a **new** object, and stating the "advance from `due_date`" and "guard
non-recurring" constraints — got Claude to produce the correct design on the first try. I
verified the weekly cadence with `test_weekly_task_regenerates_seven_days_later`. The
takeaway: for algorithmic logic, the specificity of the prompt mattered more than anything
else — the detailed prompt effectively encoded the edge cases I cared about.

> *Note: this is a two-prompt comparison (both Claude), which SF11 permits. If your section
> specifically requires two different **models**, run Prompt B through another tool (e.g.
> Gemini or Copilot) and add its result as a third column.*
