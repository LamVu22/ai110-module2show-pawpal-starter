from datetime import date, timedelta

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}
PRIORITY_LABELS = {value: key.title() for key, value in PRIORITY_MAP.items()}


def find_pet_by_name(owner: Owner, pet_name: str) -> Pet | None:
    """Return the matching pet object for a given name."""
    for pet in owner.pets:
        if pet.name == pet_name:
            return pet
    return None


def build_task_table(owner: Owner, tasks: list[Task]) -> list[dict[str, str | int | bool]]:
    """Format task objects for Streamlit tables."""
    task_rows: list[dict[str, str | int | bool]] = []
    for task in tasks:
        pet_name = owner.get_pet_name_for_task(task) or "Unknown"
        task_rows.append(
            {
                "pet": pet_name,
                "title": task.title,
                "category": task.category,
                "duration": task.duration,
                "priority": PRIORITY_LABELS.get(task.priority, task.priority),
                "due_time": task.due_time or "anytime",
                "due_date": task.due_date.isoformat() if task.due_date else "today",
                "frequency": task.frequency,
                "completed": task.completed,
            }
        )
    return task_rows


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
PawPal+ helps a pet owner turn a list of care tasks into a usable daily plan.
This version connects the Streamlit UI to the actual backend classes, sorting,
filtering, recurrence, and conflict warnings from the scheduler.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.
"""
    )

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time=60, preferences=[])

st.divider()

st.subheader("Owner Setup")
owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
available_time = st.number_input(
    "Available time today (minutes)",
    min_value=1,
    max_value=240,
    value=st.session_state.owner.available_time,
)

st.session_state.owner.name = owner_name
st.session_state.owner.set_availability(int(available_time))

st.caption(f"Session owner loaded: {st.session_state.owner.name}")

st.divider()

st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
pet_age = st.number_input("Pet age", min_value=0, max_value=30, value=3)
care_notes = st.text_input("Care notes", value="")

if st.button("Add pet"):
    existing_pet = find_pet_by_name(st.session_state.owner, pet_name)
    if existing_pet is not None:
        st.warning(f"{pet_name} is already in your pet list.")
    else:
        st.session_state.owner.add_pet(
            Pet(
                name=pet_name,
                species=species,
                age=int(pet_age),
                care_notes=care_notes,
            )
        )
        st.success(f"Added {pet_name} to {st.session_state.owner.name}'s pets.")

if st.session_state.owner.pets:
    st.markdown("### Current pets")
    st.table(
        [
            {
                "name": pet.name,
                "species": pet.species,
                "age": pet.age,
                "notes": pet.care_notes,
                "task_count": len(pet.tasks),
            }
            for pet in st.session_state.owner.pets
        ]
    )
else:
    st.info("No pets added yet. Add one above.")

st.divider()

st.subheader("Add a Task")
if not st.session_state.owner.pets:
    st.info("Add a pet first so you can assign tasks.")
else:
    selected_pet_name = st.selectbox("Choose a pet", [pet.name for pet in st.session_state.owner.pets])
    task_title = st.text_input("Task title", value="Morning walk")
    task_category = st.text_input("Category", value="walk")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    due_time = st.text_input("Due time", value="8:00 AM")
    due_date = st.date_input("Due date", value=date.today())
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        pet = find_pet_by_name(st.session_state.owner, selected_pet_name)
        if pet is None:
            st.error("Selected pet could not be found.")
        else:
            pet.add_task(
                Task(
                    title=task_title,
                    category=task_category,
                    duration=int(duration),
                    priority=PRIORITY_MAP[priority_label],
                    due_time=due_time,
                    due_date=due_date,
                    frequency=frequency,
                )
            )
            st.success(f"Added {task_title} for {pet.name}.")

st.divider()

st.subheader("Task Explorer")
scheduler = Scheduler(owner=st.session_state.owner)
scheduler.load_tasks_from_owner()

if not scheduler.tasks:
    st.info("No tasks yet. Add pets and tasks to explore your schedule.")
else:
    conflict_warnings = scheduler.detect_conflicts()
    if conflict_warnings:
        for warning in conflict_warnings:
            st.warning(f"Scheduling conflict: {warning}")
    else:
        st.success("No exact time conflicts detected.")

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        task_pet_filter = st.selectbox(
            "Filter by pet",
            ["All pets"] + [pet.name for pet in st.session_state.owner.pets],
        )
    with filter_col2:
        task_status_filter = st.selectbox("Filter by status", ["All", "Open", "Completed"])

    filtered_tasks = scheduler.tasks
    if task_status_filter == "Open":
        filtered_tasks = scheduler.filter_tasks(completed=False, tasks=filtered_tasks)
    elif task_status_filter == "Completed":
        filtered_tasks = scheduler.filter_tasks(completed=True, tasks=filtered_tasks)

    if task_pet_filter != "All pets":
        filtered_tasks = scheduler.filter_tasks(pet_name=task_pet_filter, tasks=filtered_tasks)

    st.markdown("### Current tasks")
    st.table(build_task_table(st.session_state.owner, scheduler.sort_by_time(filtered_tasks)))

    open_tasks = scheduler.filter_tasks(completed=False)
    if open_tasks:
        task_options = [
            f"{(st.session_state.owner.get_pet_name_for_task(task) or 'Unknown')} | {task.title}"
            for task in scheduler.sort_by_time(open_tasks)
        ]
        selected_task_option = st.selectbox("Complete a task", task_options)
        if st.button("Mark task complete"):
            selected_pet_name, selected_task_title = selected_task_option.split(" | ", maxsplit=1)
            next_task = scheduler.mark_task_complete(selected_pet_name, selected_task_title)
            if next_task is None:
                st.success(f"Marked {selected_task_title} as complete.")
            else:
                st.success(
                    f"Marked {selected_task_title} complete and scheduled the next {next_task.frequency} "
                    f"occurrence for {next_task.due_date.isoformat()}."
                )
            st.rerun()

st.divider()

st.subheader("Build Schedule")
st.caption("This plan uses the backend scheduler and displays conflict warnings before the final table.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=st.session_state.owner)
    schedule = scheduler.generate_schedule()
    schedule_warnings = scheduler.detect_conflicts(schedule)

    if not schedule:
        st.warning("No tasks were scheduled. Add pets or tasks first.")
    else:
        if schedule_warnings:
            for warning in schedule_warnings:
                st.warning(f"Plan warning: {warning}")

        st.markdown("### Today's schedule")
        st.table(build_task_table(st.session_state.owner, schedule))

        total_minutes = sum(task.duration for task in schedule)
        st.success(f"Scheduled {len(schedule)} task(s) in {total_minutes} minutes.")

        tomorrow = date.today() + timedelta(days=1)
        recurring_preview = [
            task for task in st.session_state.owner.get_all_tasks() if task.due_date == tomorrow
        ]
        if recurring_preview:
            st.markdown("### Upcoming recurring tasks")
            st.table(build_task_table(st.session_state.owner, scheduler.sort_by_time(recurring_preview)))

        st.markdown("### Why this plan was chosen")
        st.text(scheduler.explain_plan())
