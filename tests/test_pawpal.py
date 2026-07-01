"""Quick behavioral tests for the PawPal+ logic layer."""

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
