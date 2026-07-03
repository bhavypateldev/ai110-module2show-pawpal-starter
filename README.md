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

Output from running the CLI demo (`python main.py`). Tasks are formatted with the
`tabulate` library and emoji indicators (🔴/🟡/🟢 = high/medium/low priority; icons mark
the task category):

```
Today's Schedule for Jordan (120 min available)

╭─────────┬──────────────────────┬─────────┬────────────┬────────────╮
│ Start   │ Task                 │ Pet     │ Duration   │ Priority   │
├─────────┼──────────────────────┼─────────┼────────────┼────────────┤
│ 08:00   │ 🐕 Morning walk       │ Biscuit │ 30 min     │ 🔴 high     │
│ 08:30   │ 🍽️ Feeding           │ Biscuit │ 10 min     │ 🔴 high     │
│ 08:40   │ 🍽️ Feeding           │ Mochi   │ 10 min     │ 🔴 high     │
│ 08:50   │ 💊 Medication         │ Mochi   │ 5 min      │ 🔴 high     │
│ 08:55   │ 🧼 Litter box         │ Mochi   │ 5 min      │ 🟡 medium   │
│ 09:00   │ 🎾 Sunrise stretch    │ Biscuit │ 15 min     │ 🟢 low      │
│ 09:15   │ 🎾 Fetch / enrichment │ Biscuit │ 20 min     │ 🟢 low      │
╰─────────┴──────────────────────┴─────────┴────────────┴────────────╯

Priority-first: 'Sunrise stretch' is low priority, so despite its 07:00
preferred time it is planned after the higher-priority tasks.

Why this plan:
Scheduled 7 task(s) using 95 of 120 available minutes.
Tasks are ordered by priority (high -> low) and laid out back-to-back starting at 08:00:
  - 08:00 Morning walk: chosen because its priority is 'high' and it fit the remaining time.
  ... (one line per task) ...

All tasks sorted by time (Scheduler.sort_by_time):

╭────────┬──────────────────────┬─────────┬────────────╮
│ Time   │ Task                 │ Pet     │ Priority   │
├────────┼──────────────────────┼─────────┼────────────┤
│ 07:00  │ 🎾 Sunrise stretch    │ Biscuit │ 🟢 low      │
│ 08:00  │ 🐕 Morning walk       │ Biscuit │ 🔴 high     │
│ 08:30  │ 🍽️ Feeding           │ Biscuit │ 🔴 high     │
│ 08:30  │ 🧼 Litter box         │ Mochi   │ 🟡 medium   │
│ 09:00  │ 🍽️ Feeding           │ Mochi   │ 🔴 high     │
│ 17:00  │ 🎾 Fetch / enrichment │ Biscuit │ 🟢 low      │
│ 21:00  │ 💊 Medication         │ Mochi   │ 🔴 high     │
╰────────┴──────────────────────┴─────────┴────────────╯

Filter -> only Mochi's tasks (Owner.tasks_for_pet):
  💊 Medication   🍽️ Feeding   🧼 Litter box
Filter -> pending tasks (Scheduler.filter_by_status): 7 of 7

Conflict check (Scheduler.find_conflicts):
  ⚠  Conflict at 08:30: 'Feeding', 'Litter box' are all scheduled at the same time.

Next free 20-min slot (Scheduler.next_available_slot):
  Earliest gap that fits a 20-minute task: 08:40

Recurring tasks (Scheduler.complete_task -> Task.next_occurrence):
  Completing 'Morning walk' (frequency=daily, due 2025-01-06)...
  -> next occurrence auto-created, due 2025-01-07 (completed=False)
```

> **Priority-based scheduling (CLI evidence):** in the plan above, *Sunrise stretch* has
> the earliest preferred time (07:00) but is **low** priority, so it is scheduled at 09:00 —
> after every high- and medium-priority task. This shows the scheduler sorts by priority
> first, then by time.

## 🧪 Testing PawPal+

Run the full suite from the project root:

```bash
python -m pytest
```

**What the tests cover** (`tests/test_pawpal.py`, 27 tests):

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
- **Next available slot** — finds a gap that fits, skips gaps that are too small, and
  returns `None` when the day is full.
- **Persistence** — a task and a full owner survive a JSON save/load round trip
  (dates and completion status included).
- **Edge cases** — a pet with no tasks and an empty owner produce an empty plan without
  errors.

Successful run:

```
collected 27 items

tests\test_pawpal.py ...........................                         [100%]

============================= 27 passed in 0.11s ==============================
```

**Confidence level: ★★★★☆ (4/5).** All 27 tests pass, covering the happy paths and the
main edge cases for scheduling, sorting, filtering, conflicts, recurrence, persistence,
and slot-finding. Docking one star because conflict detection only catches exact
same-time collisions (not overlapping durations) and the recurring flow isn't yet
exercised through the Streamlit UI — both noted as future work in `reflection.md`.

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
| Next available slot | `Scheduler.next_available_slot()` | Finds the earliest gap in the day that fits a task of a given duration without overlapping already-timed tasks (returns `None` if the day is full). |

## 💾 Data Persistence

PawPal+ can remember your pets and tasks between runs by saving them to a `data.json`
file (git-ignored, since it's per-user runtime data).

**How it works** — the `Owner`, `Pet`, and `Task` classes each have `to_dict()` /
`from_dict()` methods that convert to and from plain, JSON-safe dictionaries (dates are
stored as ISO strings). I used custom dictionary conversion rather than a library like
`marshmallow` because the object graph is small and the conversion is easy to read and
test. `Owner.save_to_json(path)` and `Owner.load_from_json(path)` wrap those with
Python's built-in `json` module.

**Workflow in the app** — on startup `app.py` loads `data.json` if it exists (otherwise
it starts with a default owner). The **Data** section has **💾 Save** and **🔄 Reload**
buttons, so anything you add is restored the next time you launch the app.

**Files modified for this feature:** `pawpal_system.py` (serialization + save/load),
`app.py` (load on startup + Save/Reload buttons), `.gitignore` (ignore `data.json`),
and `tests/test_pawpal.py` (round-trip tests).

## 🎨 CLI Formatting

The CLI demo (`main.py`) uses professional output formatting:

- **`tabulate` library** (`tablefmt="rounded_outline"`) renders the schedule and the
  sorted-by-time list as clean bordered tables.
- **Emoji indicators** — priority is color-coded 🔴 high / 🟡 medium / 🟢 low, and each
  task is prefixed with a category icon (🐕 walk, 🍽️ feeding, 💊 meds, 🎾 enrichment,
  🧼 grooming, 📌 general), defined in the `PRIORITY_ICONS` / `CATEGORY_ICONS` maps.
- **UTF-8 stdout** — `main.py` calls `sys.stdout.reconfigure(encoding="utf-8")` so the
  emoji and box-drawing characters print correctly even on a Windows (cp1252) console.

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
- **Data** — **💾 Save** / **🔄 Reload** buttons persist your pets and tasks to
  `data.json` between runs.

**Example workflow**

1. Set the owner to *Jordan* with **120** available minutes.
2. Add two pets: *Biscuit* (dog) and *Mochi* (cat).
3. Add tasks — e.g. Biscuit's "Morning walk" (30 min, high, 08:00, daily) and "Feeding"
   (10 min, high, 08:30), and Mochi's "Litter box" (5 min, medium, 08:30).
4. Notice the **conflict warning** for the two 08:30 tasks.
5. Use **Tasks at a glance** to filter to just Mochi, or to pending tasks only.
6. Click **Generate schedule** to see the ordered plan and the reasoning.
7. Click **💾 Save**, close the app, relaunch — your pets and tasks are still there.

**Key Scheduler behaviors shown:** priority-first ordering, packing to a time budget,
chronological sorting, pet/status filtering, same-time conflict warnings, next-available-slot
finding, and (via the CLI) daily/weekly recurrence.

**Sample CLI output** from running `python main.py` (formatted with `tabulate` + emoji):

```
Today's Schedule for Jordan (120 min available)

╭─────────┬──────────────────────┬─────────┬────────────┬────────────╮
│ Start   │ Task                 │ Pet     │ Duration   │ Priority   │
├─────────┼──────────────────────┼─────────┼────────────┼────────────┤
│ 08:00   │ 🐕 Morning walk       │ Biscuit │ 30 min     │ 🔴 high     │
│ 08:30   │ 🍽️ Feeding           │ Biscuit │ 10 min     │ 🔴 high     │
│ 08:55   │ 🧼 Litter box         │ Mochi   │ 5 min      │ 🟡 medium   │
│ 09:00   │ 🎾 Sunrise stretch    │ Biscuit │ 15 min     │ 🟢 low      │
╰─────────┴──────────────────────┴─────────┴────────────┴────────────╯

Conflict check (Scheduler.find_conflicts):
  ⚠  Conflict at 08:30: 'Feeding', 'Litter box' are all scheduled at the same time.

Next free 20-min slot (Scheduler.next_available_slot):
  Earliest gap that fits a 20-minute task: 08:40

Recurring tasks (Scheduler.complete_task -> Task.next_occurrence):
  Completing 'Morning walk' (frequency=daily, due 2025-01-06)...
  -> next occurrence auto-created, due 2025-01-07 (completed=False)
```

*(The full CLI output — including the complete plan and the sorted/filtered views — is in
the [Sample Output](#-sample-output) section above. The table above is trimmed for brevity.)*

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
