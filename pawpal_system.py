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
        raise NotImplementedError

    def edit_task(
        self,
        title: str | None = None,
        duration: int | None = None,
        priority: int | None = None,
        category: str | None = None,
        due_time: str | None = None,
    ) -> None:
        """Update selected task fields."""
        raise NotImplementedError

    def is_due_today(self) -> bool:
        """Return whether this task should appear in today's plan."""
        raise NotImplementedError


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
        raise NotImplementedError

    def list_tasks(self) -> list[Task]:
        """Return all tasks associated with this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    name: str
    available_time: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def set_availability(self, minutes: int) -> None:
        """Set the owner's available time for the day."""
        raise NotImplementedError

    def update_preferences(self, preferences: list[str]) -> None:
        """Replace the owner's scheduling preferences."""
        raise NotImplementedError


class Scheduler:
    def __init__(
        self,
        tasks: list[Task] | None = None,
        time_limit: int = 0,
        rules: list[str] | None = None,
    ) -> None:
        self.tasks = tasks or []
        self.time_limit = time_limit
        self.rules = rules or []

    def sort_by_priority(self) -> list[Task]:
        """Return tasks ordered by scheduling priority."""
        raise NotImplementedError

    def filter_by_time(self) -> list[Task]:
        """Return tasks that fit within the current time limit."""
        raise NotImplementedError

    def generate_schedule(self, owner: Owner | None = None) -> list[Task]:
        """Build the final daily task plan."""
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Explain why the current schedule was selected."""
        raise NotImplementedError


__all__ = ["Owner", "Pet", "Scheduler", "Task"]
