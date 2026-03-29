from pawpal_system import Pet, Task


def test_mark_complete_updates_task_status() -> None:
    task = Task(title="Morning walk", category="walk", duration=20, priority=3)

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count() -> None:
    pet = Pet(name="Mochi", species="dog", age=3)
    starting_count = len(pet.tasks)

    pet.add_task(Task(title="Breakfast", category="feeding", duration=10, priority=2))

    assert len(pet.tasks) == starting_count + 1
