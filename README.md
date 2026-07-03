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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
............                                                             [100%]
12 passed in 0.05s
```

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
