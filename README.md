# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## ✨ Features

PawPal+ implements the following, split between the logic layer (`pawpal_system.py`)
and the Streamlit UI (`app.py`):

- **Owner / Pet / Task modeling** — an owner keeps multiple pets, each with its own
  care tasks (title, duration, priority, category, preferred time, recurrence).
- **Priority-first daily plan** — `Scheduler.build_plan()` orders tasks by priority,
  packs them back-to-back from the day's start, and drops anything that won't fit the
  owner's time budget. `Scheduler.explain()` describes *why* the plan looks that way.
- **Sorting by time** — `Scheduler.sort_by_time()` lists tasks in chronological
  `HH:MM` order, with untimed tasks last.
- **Filtering** — by completion status (`Scheduler.filter_by_status()`) or by pet
  (`Owner.tasks_for_pet()`); surfaced in the UI as a pet + status filter.
- **Conflict warnings** — `Scheduler.find_conflicts()` flags tasks scheduled at the
  same time and the UI shows them as `st.warning` banners (it never crashes).
- **Daily / weekly recurrence** — completing a recurring task via
  `Scheduler.complete_task()` auto-creates its next occurrence
  (`Task.next_occurrence()` using `timedelta`).
- **Persistent UI state** — the `Owner` is stored in `st.session_state`, so pets and
  tasks survive Streamlit's reruns.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Output from running the CLI demo (`python main.py`):

```
Today's Schedule for Jordan (90 min available)
====================================================
  08:00  Morning walk          30 min  [high  ] Biscuit
  08:30  Feeding               10 min  [high  ] Biscuit
  08:40  Feeding               10 min  [high  ] Mochi
  08:50  Medication             5 min  [high  ] Mochi
  08:55  Litter box             5 min  [medium] Mochi
  09:00  Fetch / enrichment    20 min  [low   ] Biscuit

Why this plan:
Scheduled 6 task(s) using 80 of 90 available minutes.
Tasks are ordered by priority (high -> low) and laid out back-to-back starting at 08:00:
  - 08:00 Morning walk: chosen because its priority is 'high' and it fit the remaining time.
  - 08:30 Feeding: chosen because its priority is 'high' and it fit the remaining time.
  - 08:40 Feeding: chosen because its priority is 'high' and it fit the remaining time.
  - 08:50 Medication: chosen because its priority is 'high' and it fit the remaining time.
  - 08:55 Litter box: chosen because its priority is 'medium' and it fit the remaining time.
  - 09:00 Fetch / enrichment: chosen because its priority is 'low' and it fit the remaining time.

All tasks sorted by time (Scheduler.sort_by_time):
----------------------------------------------------
  08:00  Morning walk (Biscuit)
  08:30  Feeding (Biscuit)
  08:30  Litter box (Mochi)
  09:00  Feeding (Mochi)
  17:00  Fetch / enrichment (Biscuit)
  21:00  Medication (Mochi)

Filter -> only Mochi's tasks (Owner.tasks_for_pet):
----------------------------------------------------
  Medication
  Feeding
  Litter box

Filter -> pending tasks (Scheduler.filter_by_status): 6 of 6

Conflict check (Scheduler.find_conflicts):
----------------------------------------------------
  [!] Conflict at 08:30: 'Feeding', 'Litter box' are all scheduled at the same time.

Recurring tasks (Scheduler.complete_task -> Task.next_occurrence):
----------------------------------------------------
  Completing 'Morning walk' (frequency=daily, due 2025-01-06)...
  -> next occurrence auto-created, due 2025-01-07 (completed=False)
```

## 🧪 Testing PawPal+

Run the full suite from the project root:

```bash
python -m pytest
```

**What the tests cover** (`tests/test_pawpal.py`, 20 tests):

- **Core objects** — `mark_complete()` flips status, `add_task()` grows a pet's task
  count, and `Owner.all_tasks()` collects tasks across pets.
- **Scheduling** — plans are ordered by priority, respect the time budget (boundary +
  over-budget cases), skip completed tasks, and lay start times back-to-back.
- **Sorting** — `sort_by_time()` returns tasks in chronological order, with untimed
  tasks last.
- **Filtering** — by completion status (`filter_by_status()`) and by pet
  (`tasks_for_pet()`, including an unknown-pet case).
- **Conflict detection** — flags two tasks at the exact same time, and correctly
  reports *no* conflict when times differ or tasks are untimed.
- **Recurrence** — completing a daily task creates a new one due the next day, a weekly
  task one week later, and a one-off task regenerates nothing.
- **Edge cases** — a pet with no tasks and an empty owner produce an empty plan without
  errors.

Successful run:

```
collected 20 items

tests\test_pawpal.py ....................                                [100%]

============================= 20 passed in 0.06s ==============================
```

**Confidence level: ★★★★☆ (4/5).** All 20 tests pass, covering the happy paths and the
main edge cases for scheduling, sorting, filtering, conflicts, and recurrence. Docking
one star because conflict detection only catches exact same-time collisions (not
overlapping durations) and the recurring flow isn't yet exercised through the Streamlit
UI — both noted as future work in `reflection.md`.

## 📐 Smarter Scheduling

The algorithmic layer lives in `pawpal_system.py`. Each "smart" behavior and the
method that implements it:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Plan ordering | `Scheduler.build_plan()` | Sorts by priority (high→low), then preferred time, then duration; lays tasks back-to-back and drops any that exceed the time budget. |
| Task sorting | `Scheduler.sort_by_time()` | Sorts tasks by `preferred_time` (`"HH:MM"`) via a `sorted()` key; untimed tasks fall to the end. |
| Filtering | `Scheduler.filter_by_status()`, `Owner.tasks_for_pet()` | Filter by completion status, or return just one pet's tasks. |
| Conflict handling | `Scheduler.find_conflicts()` | Groups tasks by `preferred_time` and returns a warning string per exact same-time collision (never raises). |
| Recurring tasks | `Scheduler.complete_task()`, `Task.next_occurrence()`, `Task.is_recurring()` | Completing a `daily`/`weekly` task auto-creates the next occurrence using `timedelta` (today/day+1 or +1 week). |

## 📸 Demo Walkthrough

Launch the app with `streamlit run app.py`. The page is organized top-to-bottom:

**Main UI features**

- **Owner** — set the owner's name and the daily time budget (minutes) the scheduler
  must fit tasks into.
- **Pets** — add pets (name, species, breed) via a form; each is stored on the `Owner`.
- **Tasks** — pick a pet and add a task with a title, duration, priority, category,
  preferred time, and a *Repeats* option (`none` / `daily` / `weekly`). Check a task off
  to mark it complete.
- **Conflict warnings** — if two tasks share a preferred time, a yellow warning banner
  appears automatically.
- **Tasks at a glance** — a table you can filter by pet and by status
  (All / Pending / Completed); rows are sorted chronologically.
- **Build schedule** — generates the priority-ordered daily plan, shows a green success
  summary, a table of start times, and an expandable "Why this plan?" explanation.

**Example workflow**

1. Set the owner to *Jordan* with **90** available minutes.
2. Add two pets: *Biscuit* (dog) and *Mochi* (cat).
3. Add tasks — e.g. Biscuit's "Morning walk" (30 min, high, 08:00, daily) and "Feeding"
   (10 min, high, 08:30), and Mochi's "Litter box" (5 min, medium, 08:30).
4. Notice the **conflict warning** for the two 08:30 tasks.
5. Use **Tasks at a glance** to filter to just Mochi, or to pending tasks only.
6. Click **Generate schedule** to see the ordered plan and the reasoning.

**Key Scheduler behaviors shown:** priority-first ordering, packing to a time budget,
chronological sorting, pet/status filtering, same-time conflict warnings, and (via the
CLI) daily/weekly recurrence.

**Sample CLI output** from running `python main.py`:

```
Today's Schedule for Jordan (90 min available)
====================================================
  08:00  Morning walk          30 min  [high  ] Biscuit
  08:30  Feeding               10 min  [high  ] Biscuit
  08:40  Feeding               10 min  [high  ] Mochi
  08:50  Medication             5 min  [high  ] Mochi
  08:55  Litter box             5 min  [medium] Mochi
  09:00  Fetch / enrichment    20 min  [low   ] Biscuit

Conflict check (Scheduler.find_conflicts):
----------------------------------------------------
  [!] Conflict at 08:30: 'Feeding', 'Litter box' are all scheduled at the same time.

Recurring tasks (Scheduler.complete_task -> Task.next_occurrence):
----------------------------------------------------
  Completing 'Morning walk' (frequency=daily, due 2025-01-06)...
  -> next occurrence auto-created, due 2025-01-07 (completed=False)
```

*(The full CLI output — including the sorted and filtered views — is in the
[Sample Output](#-sample-output) section above.)*

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
