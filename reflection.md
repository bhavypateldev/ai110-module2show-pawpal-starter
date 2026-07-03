# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

The three core actions a user should be able to perform:

1. **Add a pet** — enter an owner and a pet with basic info (name, species, breed).
2. **Add / edit care tasks** — create tasks for a pet, each with at least a duration and a
   priority (and optionally a category, a preferred time, and whether it recurs).
3. **Generate and view a daily plan** — build a schedule that orders and selects tasks to fit the
   owner's available time, and see an explanation of why each task was chosen and placed.

**a. Initial design**

My initial UML has four classes:

- **Owner** — represents the person using the app. Holds the owner's name, a daily
  `available_minutes` budget (a key scheduling constraint), free-form preferences, and a list of
  `Pet` objects. Responsible for owning pets and collecting every task across all of its pets.
- **Pet** — represents an animal being cared for. Holds `name`, `species`, `breed`, and its own
  list of `Task` objects. Responsible for managing its task list (add/remove).
- **Task** — represents one unit of care work. A dataclass holding `title`, `duration_minutes`,
  `priority`, `category`, an optional `preferred_time`, and a `recurring` flag. Responsible for
  describing a single activity and reporting a numeric priority weight for sorting.
- **Scheduler** — the "brain" of the system. Given a set of tasks plus constraints (the available
  time budget), it produces an ordered daily plan and can explain its choices. Responsible for
  sorting tasks by priority, fitting them inside the time budget, and generating the reasoning.

Relationships: an Owner *has* many Pets, a Pet *has* many Tasks, and the Scheduler *uses* Tasks to
produce a plan.

**b. Design changes**

_(Filled in after reviewing the skeleton — see the review notes below.)_

During review I noticed the Scheduler's output was under-specified: `build_plan` returned a bare list
of tasks with no place to store *when* each task starts, which made "explain the plan / show the
time next to each task" awkward. **Change:** I added a small `PlanItem` dataclass (a `start_time`
plus the scheduled `Task`) so the plan carries its timing, and `Scheduler.build_plan` now returns
`list[PlanItem]`. I also made `priority` values explicit (`low` / `medium` / `high`) and gave `Task`
a `priority_weight()` helper so sorting logic lives with the data instead of being duplicated in the
Scheduler. These changes keep the scheduling and display code cleaner without adding real complexity.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

1. **Priority** — tasks are ordered high → medium → low via `Task.priority_weight()`, so the most
   important care happens first.
2. **Time budget** — the owner's `available_minutes` caps the day; `build_plan()` lays tasks
   back-to-back from `day_start` and drops any task that would exceed the budget.
3. **Preferred time** — used as a tiebreaker within a priority level and for the `sort_by_time()`
   and conflict-detection views.

Priority mattered most because a busy owner cares more about *the right tasks getting done* than
about exact clock times, so priority drives selection and time acts as the hard ceiling.

**b. Tradeoffs**

One deliberate tradeoff is in **conflict detection**: `find_conflicts()` only flags tasks that
share the *exact same* `preferred_time` (e.g. two tasks both at `08:30`). It does **not** account
for overlapping durations — a 30-minute task at `08:00` and a task at `08:15` won't be reported even
though they truly overlap. I chose exact-match detection because it is simple, fast, easy to explain,
and never raises; a real owner mostly needs a lightweight nudge that two things collide, and full
interval-overlap math would add complexity that isn't justified for this scenario. A similar
tradeoff exists in `build_plan()`, which schedules tasks sequentially from `day_start` rather than
honoring each task's `preferred_time` exactly — trading precise clock placement for a guaranteed,
priority-first plan that fits the time budget.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI across every phase: brainstorming the class breakdown and Mermaid UML in Phase 1,
scaffolding class skeletons and then fleshing out logic in Phases 2–4, generating and debugging the
pytest suite in Phase 5, and drafting documentation in Phase 6.

The most effective AI features were:

- **Agent / multi-file editing** — the biggest win was having the assistant edit `pawpal_system.py`,
  `main.py`, `tests/test_pawpal.py`, `app.py`, and the docs together and then *run* the code
  (`python main.py`, `python -m pytest`) to confirm each change actually worked, rather than just
  suggesting snippets.
- **Chat for targeted questions** — asking narrow, concrete questions ("how do I sort `HH:MM`
  strings with a `sorted()` key?", "how should the Scheduler get all tasks from the Owner's pets?",
  "how do I advance a date by one day with `timedelta`?") produced the most useful answers. Vague
  prompts produced vague code; specific prompts tied to my existing method names produced code that
  dropped straight in.
- **Using separate chat sessions per phase** kept context clean: the design conversation didn't bleed
  into the testing conversation, so the assistant stayed focused on the current goal and I could
  reason about one concern at a time.

**b. Judgment and verification**

I verified AI output primarily by *running it* — the CLI demo and the test suite were the source of
truth, not the assistant's confidence.

One concrete example: while building the test suite I wrote (with AI help) a "sequential start times"
test that created two tasks with the **same** priority and no preferred time, then asserted a specific
order. Reading the actual sort key in `build_plan()` (`-priority_weight`, then time, then duration),
I realized the tie would be broken by *duration*, so the shorter task would come first — the opposite
of what the test assumed. I didn't accept it as-is; I changed the tasks to have distinct priorities so
the ordering was deterministic, which made the test both correct and meaningful.

I also kept my conflict detection deliberately simple (exact same-time matches) instead of adopting a
more "complete" interval-overlap algorithm, because the simpler version was easier to read, test, and
explain — and I documented that tradeoff rather than hiding it (see 2b).

---

## 4. Testing and Verification

**a. What you tested**

The suite (`tests/test_pawpal.py`, 20 tests) covers:

- **Core objects** — completion status flips, adding a task grows a pet's count, and
  `all_tasks()` collects tasks across pets.
- **Scheduling** — priority ordering, respecting the time budget (including the exact-fit boundary
  and the one-minute-over case), excluding completed tasks, and sequential start times.
- **Sorting** — chronological order with untimed tasks last.
- **Filtering** — by status and by pet (including an unknown-pet lookup).
- **Conflict detection** — flagging exact same-time tasks, and *not* false-flagging different or
  untimed tasks.
- **Recurrence** — daily → next day, weekly → +7 days, and one-off tasks regenerating nothing.

These mattered because scheduling is the heart of the app: a plan that silently drops a high-priority
task, mis-orders the day, or crashes on an empty pet would make the tool untrustworthy. Testing the
"negative" cases (no conflict, nothing to schedule) was as important as the happy paths.

**b. Confidence**

I'm fairly confident (4/5) the scheduler works for the modeled scenario — every behavior I built has
at least one test, and the CLI demo exercises the whole flow end-to-end. With more time I'd test:
interval-overlap conflicts (not just exact matches), tasks with malformed or missing times, very tight
time budgets that force many tasks to be dropped, recurrence across month/year boundaries, and driving
the recurring-completion flow through the Streamlit UI (it's currently verified via the CLI and tests).

---

## 5. Reflection

**a. What went well**

The CLI-first workflow paid off: because the logic layer was solid and fully tested before I touched
the UI, wiring `app.py` to the classes was quick and low-risk. I'm most satisfied with how cleanly the
algorithmic layer (sorting, filtering, conflicts, recurrence) slotted into the existing `Scheduler`
without needing to rewrite the earlier code — the Phase 1 design mostly held up.

**b. What you would improve**

I'd upgrade conflict detection to account for overlapping *durations*, not just identical start times,
and I'd let `build_plan()` honor each task's `preferred_time` when placing it instead of packing tasks
back-to-back from `day_start`. I'd also wire the recurring-completion flow into the Streamlit UI so
completing a daily task in the browser regenerates it, matching the CLI behavior.

**c. Key takeaway**

The most important thing I learned is what it means to be the **lead architect** when working with a
powerful AI assistant. The AI is excellent at producing code fast, but it will happily generate a test
that asserts the wrong thing, a "clever" one-liner that's harder to read, or an over-engineered
algorithm I didn't ask for. My job was to own the design decisions — which classes exist, which
tradeoffs are acceptable, what "correct" means — and to verify everything by actually running it. AI
accelerated the *how*; I stayed responsible for the *what* and *why*. Treating the test suite and the
CLI demo as the source of truth, and using focused per-phase conversations, is what kept the system
coherent instead of a pile of plausible-looking code.
