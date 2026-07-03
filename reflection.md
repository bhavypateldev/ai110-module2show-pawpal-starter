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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
