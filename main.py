from pawpal_system import Owner, Pet, Scheduler, Task


def find_pet_name_for_task(owner: Owner, task_to_match: Task) -> str:
    """Return the name of the pet that owns a given task object."""
    for pet in owner.pets:
        for task in pet.tasks:
            if task is task_to_match:
                return pet.name
    return "Unknown pet"


def print_schedule(owner: Owner, schedule: list[Task], scheduler: Scheduler) -> None:
    print(f"Today's Schedule for {owner.name}")
    print("=" * 32)
    print(f"Available time: {scheduler.time_limit} minutes")
    print()

    if not schedule:
        print("No tasks scheduled for today.")
        return

    total_minutes = 0
    for index, task in enumerate(schedule, start=1):
        pet_name = find_pet_name_for_task(owner, task)
        due_time = task.due_time or "anytime"
        print(
            f"{index}. {task.title} for {pet_name} "
            f"({task.category}, {task.duration} min, priority {task.priority}, due {due_time})"
        )
        total_minutes += task.duration

    print()
    print(f"Total planned time: {total_minutes} minutes")
    print()
    print("Why these tasks were chosen:")
    print(scheduler.explain_plan())


def main() -> None:
    owner = Owner(name="Jordan", available_time=60, preferences=["morning", "short walks first"])

    mochi = Pet(name="Mochi", species="dog", age=3, care_notes="High energy in the morning")
    luna = Pet(name="Luna", species="cat", age=5, care_notes="Needs medication after breakfast")

    mochi.add_task(Task(title="Morning walk", category="walk", duration=20, priority=3, due_time="8:00 AM"))
    mochi.add_task(Task(title="Breakfast", category="feeding", duration=10, priority=2, due_time="8:30 AM"))
    luna.add_task(Task(title="Medication", category="medication", duration=5, priority=3, due_time="9:00 AM"))
    luna.add_task(Task(title="Litter cleanup", category="cleaning", duration=15, priority=1, due_time="10:00 AM"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    scheduler = Scheduler(owner=owner)
    today_schedule = scheduler.generate_schedule()

    print_schedule(owner, today_schedule, scheduler)


if __name__ == "__main__":
    main()
