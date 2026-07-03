"""Quick behavioral tests for the PawPal+ logic layer."""

from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """mark_complete() should flip a task from not-done to done."""
    task = Task("Morning walk", 30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a pet should increase its task count by one."""
    pet = Pet(name="Biscuit", species="dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Feeding", 10))
    assert pet.task_count() == 1


def test_all_tasks_collects_across_pets():
    """Owner.all_tasks() should flatten tasks from every pet."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Biscuit", species="dog")
    cat = Pet(name="Mochi", species="cat")
    dog.add_task(Task("Walk", 30))
    cat.add_task(Task("Feeding", 10))
    owner.add_pet(dog)
    owner.add_pet(cat)
    assert len(owner.all_tasks()) == 2


def test_build_plan_respects_time_budget():
    """Tasks that exceed the available minutes should be dropped from the plan."""
    scheduler = Scheduler(available_minutes=30)
    tasks = [Task("A", 20, priority="high"), Task("B", 20, priority="high")]
    plan = scheduler.build_plan(tasks)
    assert len(plan) == 1


def test_build_plan_orders_by_priority():
    """The highest-priority task should be scheduled first."""
    scheduler = Scheduler(available_minutes=120)
    tasks = [Task("Low", 10, priority="low"), Task("High", 10, priority="high")]
    plan = scheduler.build_plan(tasks)
    assert plan[0].task.title == "High"


def test_completed_tasks_are_not_scheduled():
    """Completed tasks should be excluded from the generated plan."""
    scheduler = Scheduler(available_minutes=120)
    done = Task("Done", 10, priority="high")
    done.mark_complete()
    plan = scheduler.build_plan([done, Task("Todo", 10, priority="low")])
    titles = [item.task.title for item in plan]
    assert "Done" not in titles and "Todo" in titles


def test_sort_by_time_orders_by_preferred_time():
    """sort_by_time() orders by 'HH:MM'; untimed tasks fall to the end."""
    scheduler = Scheduler()
    tasks = [
        Task("Evening", 10, preferred_time="17:00"),
        Task("Anytime", 10, preferred_time=None),
        Task("Morning", 10, preferred_time="08:00"),
    ]
    ordered = [t.title for t in scheduler.sort_by_time(tasks)]
    assert ordered == ["Morning", "Evening", "Anytime"]


def test_filter_by_status_returns_only_matching():
    """filter_by_status() keeps only tasks with the requested completion state."""
    scheduler = Scheduler()
    done = Task("Done", 10)
    done.mark_complete()
    tasks = [done, Task("Todo", 10)]
    assert [t.title for t in scheduler.filter_by_status(tasks, completed=False)] == ["Todo"]
    assert [t.title for t in scheduler.filter_by_status(tasks, completed=True)] == ["Done"]


def test_tasks_for_pet_filters_by_name():
    """Owner.tasks_for_pet() returns only the named pet's tasks."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Biscuit", species="dog")
    cat = Pet(name="Mochi", species="cat")
    dog.add_task(Task("Walk", 30))
    cat.add_task(Task("Feeding", 10))
    owner.add_pet(dog)
    owner.add_pet(cat)
    assert [t.title for t in owner.tasks_for_pet("Mochi")] == ["Feeding"]


def test_find_conflicts_flags_same_time_tasks():
    """Two tasks at the same preferred time produce exactly one warning."""
    scheduler = Scheduler()
    tasks = [
        Task("Walk", 30, preferred_time="08:30"),
        Task("Feeding", 10, preferred_time="08:30"),
        Task("Alone", 10, preferred_time="12:00"),
    ]
    warnings = scheduler.find_conflicts(tasks)
    assert len(warnings) == 1 and "08:30" in warnings[0]


def test_daily_task_regenerates_next_day_on_completion():
    """Completing a daily task creates a fresh occurrence due one day later."""
    scheduler = Scheduler()
    pet = Pet(name="Biscuit", species="dog")
    walk = Task("Walk", 30, frequency="daily", due_date=date(2025, 1, 6))
    pet.add_task(walk)
    upcoming = scheduler.complete_task(pet, walk)
    assert walk.completed is True
    assert upcoming is not None
    assert upcoming.completed is False
    assert upcoming.due_date == date(2025, 1, 7)
    assert pet.task_count() == 2


def test_non_recurring_task_does_not_regenerate():
    """Completing a one-off task returns None and adds nothing."""
    scheduler = Scheduler()
    pet = Pet(name="Mochi", species="cat")
    once = Task("Vet visit", 60, frequency="none")
    pet.add_task(once)
    assert scheduler.complete_task(pet, once) is None
    assert pet.task_count() == 1
