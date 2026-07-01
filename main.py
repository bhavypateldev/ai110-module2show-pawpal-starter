"""CLI demo for PawPal+.

A standalone "testing ground" that builds a small scenario using the classes in
pawpal_system.py and prints today's schedule to the terminal. Run with:

    python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def pet_name_for(owner: Owner, task: Task) -> str:
    """Return the name of the pet that owns ``task`` (identity match)."""
    for pet in owner.pets:
        if any(task is t for t in pet.tasks):
            return pet.name
    return "?"


def main() -> None:
    """Build a sample owner/pets/tasks and print today's schedule."""
    # 1. Create an owner with a daily time budget.
    owner = Owner(name="Jordan", available_minutes=90)

    # 2. Create two pets.
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever")
    mochi = Pet(name="Mochi", species="cat", breed="Tabby")
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # 3. Add several tasks with different times and priorities.
    biscuit.add_task(Task("Morning walk", 30, priority="high", category="walk",
                          preferred_time="08:00", recurring=True))
    biscuit.add_task(Task("Feeding", 10, priority="high", category="feeding",
                          preferred_time="08:30", recurring=True))
    biscuit.add_task(Task("Fetch / enrichment", 20, priority="low",
                          category="enrichment", preferred_time="17:00"))
    mochi.add_task(Task("Feeding", 10, priority="high", category="feeding",
                        preferred_time="09:00", recurring=True))
    mochi.add_task(Task("Litter box", 5, priority="medium", category="grooming"))
    mochi.add_task(Task("Medication", 5, priority="high", category="meds",
                        preferred_time="21:00", recurring=True))

    # 4. Build and print today's schedule.
    scheduler = Scheduler(available_minutes=owner.available_minutes, day_start="08:00")
    plan = scheduler.build_plan(owner.all_tasks())

    print(f"Today's Schedule for {owner.name} "
          f"({owner.available_minutes} min available)")
    print("=" * 52)
    if not plan:
        print("  (nothing scheduled)")
    for item in plan:
        task = item.task
        print(f"  {item.start_time}  {task.title:<20} "
              f"{task.duration_minutes:>3} min  "
              f"[{task.priority:<6}] {pet_name_for(owner, task)}")

    print("\nWhy this plan:")
    print(scheduler.explain(plan))


if __name__ == "__main__":
    main()
