import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task


PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}


def find_pet_by_name(owner: Owner, pet_name: str) -> Pet | None:
    """Return the matching pet object for a given name."""
    for pet in owner.pets:
        if pet.name == pet_name:
            return pet
    return None


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
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
        new_pet = Pet(
            name=pet_name,
            species=species,
            age=int(pet_age),
            care_notes=care_notes,
        )
        st.session_state.owner.add_pet(new_pet)
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
    selected_pet_name = st.selectbox(
        "Choose a pet",
        [pet.name for pet in st.session_state.owner.pets],
    )
    task_title = st.text_input("Task title", value="Morning walk")
    task_category = st.text_input("Category", value="walk")
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    due_time = st.text_input("Due time", value="8:00 AM")

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
                )
            )
            st.success(f"Added {task_title} for {pet.name}.")

if st.session_state.owner.pets:
    all_pet_tasks = []
    for pet in st.session_state.owner.pets:
        for task in pet.tasks:
            all_pet_tasks.append(
                {
                    "pet": pet.name,
                    "title": task.title,
                    "category": task.category,
                    "duration": task.duration,
                    "priority": task.priority,
                    "due_time": task.due_time or "anytime",
                    "completed": task.completed,
                }
            )

    if all_pet_tasks:
        st.markdown("### Current tasks")
        st.table(all_pet_tasks)
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button now uses your backend scheduler.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner=st.session_state.owner)
    schedule = scheduler.generate_schedule()

    if not schedule:
        st.warning("No tasks were scheduled. Add pets or tasks first.")
    else:
        st.markdown("### Today's schedule")
        st.table(
            [
                {
                    "title": task.title,
                    "category": task.category,
                    "duration": task.duration,
                    "priority": task.priority,
                    "due_time": task.due_time or "anytime",
                }
                for task in schedule
            ]
        )
        st.markdown("### Why this plan was chosen")
        st.text(scheduler.explain_plan())
