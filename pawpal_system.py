"""PawPal+ logic layer.

The system's "brain," independent of the Streamlit UI. It models pet care work
(:class:`Task`), the animals (:class:`Pet`), the person (:class:`Owner`), and a
:class:`Scheduler` that turns tasks + constraints into an ordered daily plan and
provides the "smart" behaviors: sorting, filtering, recurring tasks, and
conflict detection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

# Priority labels used by tasks, ordered from least to most urgent.
PRIORITY_WEIGHTS: dict[str, int] = {"low": 1, "medium": 2, "high": 3}

# Frequencies a task can repeat on (anything else means it does not recur).
RECURRING_FREQUENCIES: set[str] = {"daily", "weekly"}

# Sentinel time used to sort tasks that have no preferred time to the end.
_UNTIMED = 24 * 60


def _parse_time(hhmm: str) -> int:
    """Convert an ``"HH:MM"`` string into minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def _format_time(minutes: int) -> str:
    """Convert minutes since midnight back into an ``"HH:MM"`` string."""
    minutes %= 24 * 60
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


@dataclass
class Task:
    """A single unit of pet care work (a walk, a feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # one of: "low", "medium", "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds", "enrichment"
    preferred_time: str | None = None  # e.g. "08:00", or None for "any time"
    frequency: str = "none"  # "none", "daily", or "weekly"
    due_date: date | None = None  # the day this occurrence is due
    completed: bool = False

    def priority_weight(self) -> int:
        """Return this task's priority as a number so it can be sorted."""
        return PRIORITY_WEIGHTS.get(self.priority.lower(), 0)

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task back to not-done."""
        self.completed = False

    def is_recurring(self) -> bool:
        """Return True if this task repeats on a daily/weekly schedule."""
        return self.frequency in RECURRING_FREQUENCIES

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, uncompleted copy due on the next date, or None."""
        if not self.is_recurring():
            return None
        step = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        base = self.due_date or date.today()
        return Task(
            title=self.title,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            category=self.category,
            preferred_time=self.preferred_time,
            frequency=self.frequency,
            due_date=base + step,
            completed=False,
        )


@dataclass
class Pet:
    """An animal being cared for, owning its own list of tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> None:
        """Remove the first task with the given title, if present."""
        for index, task in enumerate(self.tasks):
            if task.title == title:
                del self.tasks[index]
                return

    def task_count(self) -> int:
        """Return how many tasks are currently attached to this pet."""
        return len(self.tasks)


@dataclass
class Owner:
    """The person using PawPal+. Owns pets and sets scheduling constraints."""

    name: str
    available_minutes: int = 120  # daily time budget the scheduler must respect
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets, flattened."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks

    def tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Return the tasks belonging to the pet with the given name."""
        for pet in self.pets:
            if pet.name == pet_name:
                return list(pet.tasks)
        return []


@dataclass
class PlanItem:
    """One scheduled entry in the daily plan: a task placed at a start time."""

    start_time: str  # e.g. "08:00"
    task: Task


class Scheduler:
    """Builds and explains a daily plan, plus sorting/filtering/conflict helpers."""

    def __init__(self, available_minutes: int = 120, day_start: str = "08:00") -> None:
        """Create a scheduler with a daily time budget and a start-of-day time."""
        self.available_minutes = available_minutes
        self.day_start = day_start

    def _order(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority (high first), then preferred time, then length."""
        return sorted(
            tasks,
            key=lambda t: (
                -t.priority_weight(),
                _parse_time(t.preferred_time) if t.preferred_time else _UNTIMED,
                t.duration_minutes,
            ),
        )

    def build_plan(self, tasks: list[Task]) -> list[PlanItem]:
        """Pick and order incomplete tasks that fit the budget, timed back-to-back."""
        plan: list[PlanItem] = []
        minutes_used = 0
        cursor = _parse_time(self.day_start)
        for task in self._order([t for t in tasks if not t.completed]):
            if minutes_used + task.duration_minutes > self.available_minutes:
                continue  # skip tasks that would blow the time budget
            plan.append(PlanItem(start_time=_format_time(cursor), task=task))
            cursor += task.duration_minutes
            minutes_used += task.duration_minutes
        return plan

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks sorted by preferred time ('HH:MM'); untimed tasks go last."""
        return sorted(
            tasks,
            key=lambda t: _parse_time(t.preferred_time) if t.preferred_time else _UNTIMED,
        )

    def filter_by_status(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Return only the tasks whose completion status matches `completed`."""
        return [task for task in tasks if task.completed == completed]

    def find_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return a warning for each group of tasks sharing a preferred time.

        Lightweight: it only flags *exact* same-time collisions and never raises,
        so callers can display the warnings instead of crashing.
        """
        by_time: dict[str, list[Task]] = {}
        for task in tasks:
            if task.preferred_time:
                by_time.setdefault(task.preferred_time, []).append(task)
        warnings: list[str] = []
        for when in sorted(by_time):
            group = by_time[when]
            if len(group) > 1:
                titles = ", ".join(f"'{task.title}'" for task in group)
                warnings.append(
                    f"Conflict at {when}: {titles} are all scheduled at the same time."
                )
        return warnings

    def next_available_slot(
        self, tasks: list[Task], duration_minutes: int, day_end: str = "24:00"
    ) -> "str | None":
        """Return the earliest start time that fits `duration_minutes` without
        overlapping any already-timed task, or None if the day has no room.

        Considers only tasks with a `preferred_time` (their occupied interval is
        start .. start+duration) and searches gaps from `day_start` onward.
        """
        intervals = sorted(
            (
                _parse_time(task.preferred_time),
                _parse_time(task.preferred_time) + task.duration_minutes,
            )
            for task in tasks
            if task.preferred_time
        )
        limit = _parse_time(day_end)
        cursor = _parse_time(self.day_start)
        for start, end in intervals:
            if start - cursor >= duration_minutes:
                return _format_time(cursor)  # gap before this task is big enough
            cursor = max(cursor, end)
        if cursor + duration_minutes <= limit:
            return _format_time(cursor)
        return None

    def complete_task(self, pet: Pet, task: Task) -> "Task | None":
        """Mark a task done; if it recurs, add and return its next occurrence."""
        task.mark_complete()
        if task.is_recurring():
            upcoming = task.next_occurrence()
            pet.add_task(upcoming)
            return upcoming
        return None

    def explain(self, plan: list[PlanItem]) -> str:
        """Return a human-readable explanation of why the plan looks this way."""
        if not plan:
            return "No tasks fit within the available time budget."
        total = sum(item.task.duration_minutes for item in plan)
        lines = [
            f"Scheduled {len(plan)} task(s) using {total} of "
            f"{self.available_minutes} available minutes.",
            f"Tasks are ordered by priority (high -> low) and laid out "
            f"back-to-back starting at {self.day_start}:",
        ]
        for item in plan:
            task = item.task
            lines.append(
                f"  - {item.start_time} {task.title}: chosen because its priority "
                f"is '{task.priority}' and it fit the remaining time."
            )
        return "\n".join(lines)
