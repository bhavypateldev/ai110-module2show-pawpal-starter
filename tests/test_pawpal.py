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


# --- Edge cases --------------------------------------------------------------

def test_pet_with_no_tasks_produces_empty_plan():
    """An owner whose pet has no tasks yields an empty plan and no conflicts."""
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Biscuit", species="dog"))
    scheduler = Scheduler()
    assert owner.all_tasks() == []
    assert scheduler.build_plan(owner.all_tasks()) == []
    assert scheduler.find_conflicts(owner.all_tasks()) == []


def test_tasks_for_unknown_pet_is_empty():
    """Asking for a pet that doesn't exist returns an empty list, not an error."""
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Biscuit", species="dog"))
    assert owner.tasks_for_pet("Nobody") == []


def test_no_conflict_when_times_differ():
    """Tasks at different preferred times should produce no conflict warnings."""
    scheduler = Scheduler()
    tasks = [Task("A", 10, preferred_time="08:00"), Task("B", 10, preferred_time="09:00")]
    assert scheduler.find_conflicts(tasks) == []


def test_untimed_tasks_are_not_conflicts():
    """Tasks without a preferred time never count as same-time conflicts."""
    scheduler = Scheduler()
    tasks = [Task("A", 10, preferred_time=None), Task("B", 10, preferred_time=None)]
    assert scheduler.find_conflicts(tasks) == []


def test_weekly_task_regenerates_seven_days_later():
    """Completing a weekly task creates a fresh occurrence due one week later."""
    scheduler = Scheduler()
    pet = Pet(name="Mochi", species="cat")
    meds = Task("Medication", 5, frequency="weekly", due_date=date(2025, 1, 6))
    pet.add_task(meds)
    upcoming = scheduler.complete_task(pet, meds)
    assert upcoming.due_date == date(2025, 1, 13)
    assert upcoming.completed is False


def test_task_exactly_filling_budget_is_included():
    """A task whose duration equals the whole budget still fits (boundary)."""
    scheduler = Scheduler(available_minutes=30)
    plan = scheduler.build_plan([Task("Walk", 30, priority="high")])
    assert len(plan) == 1


def test_task_exceeding_budget_is_dropped():
    """A task longer than the entire budget is left out of the plan."""
    scheduler = Scheduler(available_minutes=30)
    plan = scheduler.build_plan([Task("Marathon walk", 31, priority="high")])
    assert plan == []


def test_plan_start_times_are_sequential():
    """Scheduled tasks start back-to-back from the scheduler's day_start."""
    scheduler = Scheduler(available_minutes=120, day_start="08:00")
    # Distinct priorities keep the order deterministic (high before medium).
    tasks = [Task("A", 30, priority="high"), Task("B", 15, priority="medium")]
    plan = scheduler.build_plan(tasks)
    assert [item.task.title for item in plan] == ["A", "B"]
    assert [item.start_time for item in plan] == ["08:00", "08:30"]


# --- Challenge 1: next available slot ----------------------------------------

def test_next_available_slot_empty_day_returns_day_start():
    """With no timed tasks, the first slot is the scheduler's day_start."""
    scheduler = Scheduler(day_start="08:00")
    assert scheduler.next_available_slot([], 30) == "08:00"


def test_next_available_slot_finds_gap_between_tasks():
    """A 30-min request fits in the 08:30-09:00 gap between two 30-min tasks."""
    scheduler = Scheduler(day_start="08:00")
    tasks = [Task("A", 30, preferred_time="08:00"), Task("B", 30, preferred_time="09:00")]
    assert scheduler.next_available_slot(tasks, 30) == "08:30"


def test_next_available_slot_skips_gap_that_is_too_small():
    """A 45-min request can't use the 30-min gap, so it lands after 09:30."""
    scheduler = Scheduler(day_start="08:00")
    tasks = [Task("A", 30, preferred_time="08:00"), Task("B", 30, preferred_time="09:00")]
    assert scheduler.next_available_slot(tasks, 45) == "09:30"


def test_next_available_slot_returns_none_when_no_room():
    """If the day ends before the task can fit, return None instead of crashing."""
    scheduler = Scheduler(day_start="23:00")
    tasks = [Task("Late", 30, preferred_time="23:00")]
    assert scheduler.next_available_slot(tasks, 60, day_end="23:45") is None


# --- Challenge 2: JSON persistence -------------------------------------------

def _sample_owner():
    owner = Owner(name="Jordan", available_minutes=90)
    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever")
    owner.add_pet(biscuit)
    biscuit.add_task(
        Task("Morning walk", 30, priority="high", preferred_time="08:00",
             frequency="daily", due_date=date(2025, 1, 6))
    )
    done = Task("Feeding", 10, priority="high")
    done.mark_complete()
    biscuit.add_task(done)
    return owner


def test_task_dict_round_trip_preserves_date_and_status():
    """A task survives a to_dict/from_dict round trip, including its date."""
    task = Task("Meds", 5, frequency="weekly", due_date=date(2025, 1, 6))
    task.mark_complete()
    restored = Task.from_dict(task.to_dict())
    assert restored == task  # dataclass equality covers every field


def test_owner_save_and_load_round_trip(tmp_path):
    """Saving an owner to JSON and reloading rebuilds the whole object graph."""
    path = tmp_path / "data.json"
    original = _sample_owner()
    original.save_to_json(path)

    loaded = Owner.load_from_json(path)
    assert loaded.name == "Jordan"
    assert loaded.available_minutes == 90
    assert len(loaded.pets) == 1
    assert loaded.pets[0].task_count() == 2
    walk = loaded.pets[0].tasks[0]
    assert walk.due_date == date(2025, 1, 6)
    assert loaded.pets[0].tasks[1].completed is True


def test_loaded_tasks_are_usable_by_scheduler(tmp_path):
    """Tasks reloaded from JSON still work with the scheduler's logic."""
    path = tmp_path / "data.json"
    _sample_owner().save_to_json(path)
    loaded = Owner.load_from_json(path)
    scheduler = Scheduler(available_minutes=loaded.available_minutes)
    plan = scheduler.build_plan(loaded.all_tasks())
    assert [item.task.title for item in plan] == ["Morning walk"]  # 'Feeding' is completed
