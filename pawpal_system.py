from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


@dataclass
class Task:
    title: str
    category: str
    duration: int
    priority: int
    due_time: str | None = None
    due_date: date | None = None
    frequency: str = "once"
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
        due_date: date | None = None,
        frequency: str | None = None,
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
        if due_date is not None:
            self.due_date = due_date
        if frequency is not None:
            self.frequency = frequency

    def is_due_today(self) -> bool:
        """Return whether this task should appear in today's plan."""
        return not self.completed and (self.due_date is None or self.due_date <= date.today())

    def next_occurrence(self) -> "Task | None":
        """Create the next recurring task instance when this task repeats."""
        if self.frequency not in {"daily", "weekly"}:
            return None

        current_due_date = self.due_date or date.today()
        days_to_add = 1 if self.frequency == "daily" else 7
        return Task(
            title=self.title,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            due_time=self.due_time,
            due_date=current_due_date + timedelta(days=days_to_add),
            frequency=self.frequency,
        )


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

    def complete_task(self, task_title: str) -> Task | None:
        """Mark a task complete and append its next recurring instance when needed."""
        for task in self.tasks:
            if task.title == task_title and not task.completed:
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task is not None:
                    self.tasks.append(next_task)
                return next_task
        return None


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

    def get_tasks_for_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks for the pet whose name matches the given value."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet.list_tasks()
        return []

    def get_pet_name_for_task(self, task_to_match: Task) -> str | None:
        """Return the pet name associated with a specific task object."""
        for pet in self.pets:
            for task in pet.tasks:
                if task is task_to_match:
                    return pet.name
        return None


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

    @staticmethod
    def _parse_due_time(due_time: str | None) -> tuple[int, int]:
        """Convert a task's due time into sortable hour and minute values."""
        if not due_time:
            return (23, 59)

        normalized_time = due_time.strip().upper()
        for time_format in ("%I:%M %p", "%H:%M"):
            try:
                parsed_time = datetime.strptime(normalized_time, time_format)
                return (parsed_time.hour, parsed_time.minute)
            except ValueError:
                continue

        return (23, 59)

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

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return tasks ordered by due time from earliest to latest."""
        task_list = tasks if tasks is not None else self.tasks
        return sorted(
            task_list,
            key=lambda task: (
                self._parse_due_time(task.due_time),
                -task.priority,
                task.title.lower(),
            ),
        )

    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
        tasks: list[Task] | None = None,
    ) -> list[Task]:
        """Filter tasks by completion status and optionally by pet name."""
        task_list = tasks.copy() if tasks is not None else self.tasks.copy()

        if completed is not None:
            task_list = [task for task in task_list if task.completed == completed]

        if pet_name is not None and self.owner is not None:
            pet_tasks = self.owner.get_tasks_for_pet(pet_name)
            pet_task_ids = {id(task) for task in pet_tasks}
            task_list = [task for task in task_list if id(task) in pet_task_ids]
        elif pet_name is not None:
            task_list = []

        return task_list

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

    def mark_task_complete(self, pet_name: str, task_title: str) -> Task | None:
        """Complete a pet task and generate the next recurring task when applicable."""
        if self.owner is None:
            return None

        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                next_task = pet.complete_task(task_title)
                self.load_tasks_from_owner()
                return next_task
        return None

    def detect_conflicts(self, tasks: list[Task] | None = None) -> list[str]:
        """Return warning messages for tasks that share the exact same due time."""
        task_list = self.sort_by_time(tasks if tasks is not None else self.tasks)
        tasks_by_time: dict[str, list[Task]] = {}

        for task in task_list:
            if not task.due_time:
                continue
            tasks_by_time.setdefault(task.due_time, []).append(task)

        warnings: list[str] = []
        for due_time, grouped_tasks in tasks_by_time.items():
            if len(grouped_tasks) < 2:
                continue

            task_labels = []
            for task in grouped_tasks:
                pet_name = self.owner.get_pet_name_for_task(task) if self.owner is not None else None
                if pet_name is None:
                    task_labels.append(task.title)
                else:
                    task_labels.append(f"{task.title} ({pet_name})")

            warnings.append(
                f"Conflict at {due_time}: " + ", ".join(task_labels)
            )

        return warnings

    def generate_schedule(self, owner: Owner | None = None) -> list[Task]:
        """Build the final daily task plan."""
        if owner is not None:
            self.owner = owner
            if self.time_limit == 0:
                self.time_limit = owner.available_time

        if self.owner is not None:
            self.load_tasks_from_owner()

        self.last_plan = self.sort_by_time(self.filter_by_time())
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
