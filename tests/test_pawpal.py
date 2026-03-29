from pawpal_system import Pet, Task


from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_updates_task_status() -> None:
    task = Task(title="Morning walk", category="walk", duration=20, priority=3)

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="dog", age=3)
    starting_count = len(pet.tasks)

    pet.add_task(Task(title="Breakfast", category="feeding", duration=10, priority=2))

    assert len(pet.tasks) == starting_count + 1


def test_mark_task_complete_creates_next_daily_occurrence() -> None:
    owner = Owner(name="Jordan", available_time=60)
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(
        Task(
            title="Breakfast",
            category="feeding",
            duration=10,
            priority=2,
            due_time="8:00 AM",
            due_date=date.today(),
            frequency="daily",
        )
    )
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    next_task = scheduler.mark_task_complete("Mochi", "Breakfast")

    assert pet.tasks[0].completed is True
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.frequency == "daily"
    assert len(pet.tasks) == 2


def test_detect_conflicts_returns_warning_for_same_due_time() -> None:
    owner = Owner(name="Jordan", available_time=60)
    mochi = Pet(name="Mochi", species="dog", age=3)
    luna = Pet(name="Luna", species="cat", age=5)
    mochi.add_task(Task(title="Morning walk", category="walk", duration=20, priority=3, due_time="8:00 AM"))
    luna.add_task(Task(title="Medication", category="medication", duration=5, priority=3, due_time="8:00 AM"))
    owner.add_pet(mochi)
    owner.add_pet(luna)
    scheduler = Scheduler(owner=owner)
    scheduler.load_tasks_from_owner()

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "8:00 AM" in warnings[0]
    assert "Morning walk" in warnings[0]
    assert "Medication" in warnings[0]
