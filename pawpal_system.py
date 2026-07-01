"""PawPal+ logic layer.

The system's "brain," independent of the Streamlit UI. It models pet care work
(:class:`Task`), the animals (:class:`Pet`), the person (:class:`Owner`), and a
:class:`Scheduler` that turns tasks + constraints into an ordered daily plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Priority labels used by tasks, ordered from least to most urgent.
PRIORITY_WEIGHTS: dict[str, int] = {"low": 1, "medium": 2, "high": 3}


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
    recurring: bool = False  # True for daily/repeating tasks, False for one-offs
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


@dataclass
class PlanItem:
    """One scheduled entry in the daily plan: a task placed at a start time."""

    start_time: str  # e.g. "08:00"
    task: Task


class Scheduler:
    """Builds and explains a daily plan from tasks and time constraints."""

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
                _parse_time(t.preferred_time) if t.preferred_time else 24 * 60,
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
