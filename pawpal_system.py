from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    category: str
    duration: int
    priority: int
    due_time: str | None = None
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as finished."""
        self.completed = True

    def edit_task(
        self,
        title: str | None = None,
        duration: int | None = None,
        priority: int | None = None,
        category: str | None = None,
        due_time: str | None = None,
    ) -> None:
        """Update selected task fields."""
        if title is not None:
            self.title = title
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if category is not None:
            self.category = category
        if due_time is not None:
            self.due_time = due_time

    def is_due_today(self) -> bool:
        """Return whether this task should appear in today's plan."""
        return not self.completed


@dataclass
class Pet:
    name: str
    species: str
    age: int
    care_notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def update_details(
        self,
        name: str | None = None,
        age: int | None = None,
        notes: str | None = None,
    ) -> None:
        """Update pet profile information."""
        if name is not None:
            self.name = name
        if age is not None:
            self.age = age
        if notes is not None:
            self.care_notes = notes

    def list_tasks(self) -> list[Task]:
        """Return all tasks associated with this pet."""
        return self.tasks.copy()

    def add_task(self, task: Task) -> None:
        """Attach a new care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_title: str) -> bool:
        """Remove the first task that matches the provided title."""
        for index, task in enumerate(self.tasks):
            if task.title == task_title:
                del self.tasks[index]
                return True
        return False


@dataclass
class Owner:
    name: str
    available_time: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def set_availability(self, minutes: int) -> None:
        """Set the owner's available time for the day."""
        self.available_time = minutes

    def update_preferences(self, preferences: list[str]) -> None:
        """Replace the owner's scheduling preferences."""
        self.preferences = preferences.copy()

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's household."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all pets owned by this owner."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.list_tasks())
        return all_tasks


class Scheduler:
    def __init__(
        self,
        owner: Owner | None = None,
        tasks: list[Task] | None = None,
        time_limit: int = 0,
        rules: list[str] | None = None,
    ) -> None:
        self.owner = owner
        self.tasks = tasks.copy() if tasks else []
        self.time_limit = time_limit
        self.rules = rules.copy() if rules else []
        self.last_plan: list[Task] = []

    def load_tasks_from_owner(self) -> list[Task]:
        """Collect tasks from all pets that belong to the current owner."""
        if self.owner is None:
            return self.tasks.copy()

        owner_tasks = self.owner.get_all_tasks()
        self.tasks = owner_tasks
        if self.time_limit == 0:
            self.time_limit = self.owner.available_time
        return owner_tasks.copy()

    def sort_by_priority(self) -> list[Task]:
        """Return tasks ordered by scheduling priority."""
        return sorted(
            self.tasks,
            key=lambda task: (
                not task.is_due_today(),
                -task.priority,
                task.duration,
                task.title.lower(),
            ),
        )

    def filter_by_time(self) -> list[Task]:
        """Return tasks that fit within the current time limit."""
        selected_tasks: list[Task] = []
        used_minutes = 0

        for task in self.sort_by_priority():
            if not task.is_due_today():
                continue
            if used_minutes + task.duration <= self.time_limit:
                selected_tasks.append(task)
                used_minutes += task.duration

        return selected_tasks

    def generate_schedule(self, owner: Owner | None = None) -> list[Task]:
        """Build the final daily task plan."""
        if owner is not None:
            self.owner = owner
            if self.time_limit == 0:
                self.time_limit = owner.available_time

        if self.owner is not None:
            self.load_tasks_from_owner()

        self.last_plan = self.filter_by_time()
        return self.last_plan.copy()

    def explain_plan(self) -> str:
        """Explain why the current schedule was selected."""
        if not self.last_plan:
            return "No tasks were scheduled. Check available time, task status, or task list."

        plan_lines = [
            f"- {task.title}: priority {task.priority}, {task.duration} minutes"
            for task in self.last_plan
        ]
        return "Tasks were selected based on completion status, priority, and available time.\n" + "\n".join(
            plan_lines
        )


__all__ = ["Owner", "Pet", "Scheduler", "Task"]
