"""CLI demo for PawPal+.

A standalone "testing ground" that exercises the logic in pawpal_system.py:
building a daily plan, sorting by time, filtering, conflict detection, and
recurring-task regeneration. Run with:

    python main.py
"""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task

# A fixed anchor day keeps the recurring-task output deterministic in this demo.
BASE_DAY = date(2025, 1, 6)  # a Monday


def pet_name_for(owner: Owner, task: Task) -> str:
    """Return the name of the pet that owns ``task`` (identity match)."""
    for pet in owner.pets:
        if any(task is t for t in pet.tasks):
            return pet.name
    return "?"


def build_owner() -> Owner:
    """Create a sample owner with two pets and several tasks (added out of order)."""
    owner = Owner(name="Jordan", available_minutes=90)

    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever")
    mochi = Pet(name="Mochi", species="cat", breed="Tabby")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Tasks are intentionally added out of time order to show off sorting.
    biscuit.add_task(Task("Fetch / enrichment", 20, priority="low",
                          category="enrichment", preferred_time="17:00"))
    biscuit.add_task(Task("Morning walk", 30, priority="high", category="walk",
                          preferred_time="08:00", frequency="daily", due_date=BASE_DAY))
    biscuit.add_task(Task("Feeding", 10, priority="high", category="feeding",
                          preferred_time="08:30", frequency="daily", due_date=BASE_DAY))
    mochi.add_task(Task("Medication", 5, priority="high", category="meds",
                        preferred_time="21:00", frequency="weekly", due_date=BASE_DAY))
    mochi.add_task(Task("Feeding", 10, priority="high", category="feeding",
                        preferred_time="09:00", frequency="daily", due_date=BASE_DAY))
    # Note the same 08:30 slot as Biscuit's feeding -> a conflict to detect.
    mochi.add_task(Task("Litter box", 5, priority="medium", category="grooming",
                        preferred_time="08:30"))
    return owner


def print_schedule(owner: Owner, scheduler: Scheduler) -> None:
    """Print today's priority-ordered plan and the reasoning behind it."""
    plan = scheduler.build_plan(owner.all_tasks())
    print(f"Today's Schedule for {owner.name} "
          f"({owner.available_minutes} min available)")
    print("=" * 52)
    for item in plan:
        task = item.task
        print(f"  {item.start_time}  {task.title:<20} "
              f"{task.duration_minutes:>3} min  "
              f"[{task.priority:<6}] {pet_name_for(owner, task)}")
    print("\nWhy this plan:")
    print(scheduler.explain(plan))


def print_sorted_by_time(owner: Owner, scheduler: Scheduler) -> None:
    """Print all tasks sorted by their preferred time of day."""
    print("\nAll tasks sorted by time (Scheduler.sort_by_time):")
    print("-" * 52)
    for task in scheduler.sort_by_time(owner.all_tasks()):
        when = task.preferred_time or "any"
        print(f"  {when:>5}  {task.title} ({pet_name_for(owner, task)})")


def print_filters(owner: Owner, scheduler: Scheduler) -> None:
    """Print filtering by pet name and by completion status."""
    print("\nFilter -> only Mochi's tasks (Owner.tasks_for_pet):")
    print("-" * 52)
    for task in owner.tasks_for_pet("Mochi"):
        print(f"  {task.title}")

    pending = scheduler.filter_by_status(owner.all_tasks(), completed=False)
    print(f"\nFilter -> pending tasks (Scheduler.filter_by_status): "
          f"{len(pending)} of {len(owner.all_tasks())}")


def print_conflicts(owner: Owner, scheduler: Scheduler) -> None:
    """Print any same-time conflicts the scheduler detects."""
    print("\nConflict check (Scheduler.find_conflicts):")
    print("-" * 52)
    warnings = scheduler.find_conflicts(owner.all_tasks())
    if warnings:
        for warning in warnings:
            print(f"  [!] {warning}")
    else:
        print("  No conflicts found.")


def demo_recurring(owner: Owner, scheduler: Scheduler) -> None:
    """Complete a recurring task and show the auto-generated next occurrence."""
    print("\nRecurring tasks (Scheduler.complete_task -> Task.next_occurrence):")
    print("-" * 52)
    biscuit = owner.pets[0]
    walk = next(t for t in biscuit.tasks if t.title == "Morning walk")
    print(f"  Completing '{walk.title}' (frequency={walk.frequency}, "
          f"due {walk.due_date})...")
    upcoming = scheduler.complete_task(biscuit, walk)
    print(f"  -> next occurrence auto-created, due {upcoming.due_date} "
          f"(completed={upcoming.completed})")


def main() -> None:
    """Run the full CLI demo."""
    owner = build_owner()
    scheduler = Scheduler(available_minutes=owner.available_minutes, day_start="08:00")

    print_schedule(owner, scheduler)
    print_sorted_by_time(owner, scheduler)
    print_filters(owner, scheduler)
    print_conflicts(owner, scheduler)
    demo_recurring(owner, scheduler)


if __name__ == "__main__":
    main()
