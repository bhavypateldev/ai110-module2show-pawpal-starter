"""PawPal+ logic layer.

Phase 1 skeleton: class names, attributes, and empty method stubs derived from
the UML in diagrams/uml.mmd. No scheduling logic is implemented yet — the method
bodies raise NotImplementedError and are filled in during later phases.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Priority labels used by tasks, ordered from least to most urgent.
PRIORITY_WEIGHTS: dict[str, int] = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Task:
    """A single unit of pet care work (a walk, a feeding, meds, etc.)."""

    title: str
    duration_minutes: int
    priority: str = "medium"  # one of: "low", "medium", "high"
    category: str = "general"  # e.g. "walk", "feeding", "meds", "enrichment"
    preferred_time: str | None = None  # e.g. "08:00", or None for "any time"
    recurring: bool = False

    def priority_weight(self) -> int:
        """Return a numeric weight for this task's priority, for sorting."""
        raise NotImplementedError


@dataclass
class Pet:
    """An animal being cared for, owning its own list of tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError

    def remove_task(self, title: str) -> None:
        """Remove the task with the given title from this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """The person using PawPal+. Owns pets and sets scheduling constraints."""

    name: str
    available_minutes: int = 120  # daily time budget the scheduler must respect
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        raise NotImplementedError


@dataclass
class PlanItem:
    """One scheduled entry in the daily plan: a task placed at a start time."""

    start_time: str  # e.g. "08:00"
    task: Task


class Scheduler:
    """Builds and explains a daily plan from tasks and time constraints."""

    def __init__(self, available_minutes: int = 120, day_start: str = "08:00") -> None:
        self.available_minutes = available_minutes
        self.day_start = day_start

    def build_plan(self, tasks: list[Task]) -> list[PlanItem]:
        """Order and select tasks to fit the time budget, returning a plan."""
        raise NotImplementedError

    def explain(self, plan: list[PlanItem]) -> str:
        """Return a human-readable explanation of why the plan looks this way."""
        raise NotImplementedError
