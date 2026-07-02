import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

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

st.divider()

# Initialize session state to persist Owner and counters across page refreshes
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time=120)

if "pet_counter" not in st.session_state:
    st.session_state.pet_counter = 1

if "task_counter" not in st.session_state:
    st.session_state.task_counter = 1

owner = st.session_state.owner

# Owner Setup Section
st.subheader("👤 Owner Setup")
with st.expander("Create or Update Owner", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        input_owner_name = st.text_input("Owner name", value=owner.name, key="input_owner_name")
    with col2:
        input_available_time = st.number_input("Available time per day (minutes)", min_value=15, max_value=1440, value=owner.available_time, key="input_available_time")

    if st.button("Create/Update Owner"):
        owner.name = input_owner_name
        owner.available_time = int(input_available_time)
        st.success(f"Owner updated: {owner.name} with {owner.available_time} min available")

col1, col2 = st.columns(2)
with col1:
    st.metric("Current Owner", owner.name)
with col2:
    st.metric("Available Time", f"{owner.available_time} min")

if st.button("Reset / Start Over"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.divider()

# Pet and Task Management Section
st.subheader("🐾 Add Pets & Tasks")

# Add Pet Section
st.markdown("### Add Pet")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Biscuit", key="pet_name_input")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"], key="species_input")

if st.button("Add pet"):
    new_pet = Pet(id=st.session_state.pet_counter, name=pet_name, species=species)
    owner.add_pet(new_pet)
    st.session_state.pet_counter += 1
    st.success(f"Added {pet_name} ({species}) to {owner.name}'s pets!")

# Display current pets
if owner.pets:
    st.markdown("**Current Pets:**")
    for pet in owner.pets:
        st.write(f"- {pet.name} ({pet.species}) — {len(pet.get_tasks())} task(s)")
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Add Task")
if not owner.pets:
    st.warning("Add a pet first before adding tasks.")
else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        pet_options = [pet.name for pet in owner.pets]
        selected_pet_name = st.selectbox("Assign to pet", pet_options, key="task_pet_select")
    with col2:
        task_title = st.text_input("Task title", value="Morning walk", key="task_title_input")
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20, key="task_duration_input")
    with col4:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2, key="task_priority_input")

    if st.button("Add task"):
        selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        new_task = Task(id=st.session_state.task_counter, description=task_title, duration_minutes=int(duration), priority=priority, frequency="daily")
        selected_pet.add_task(new_task)
        st.session_state.task_counter += 1
        st.success(f"Added '{task_title}' to {selected_pet_name}!")

    # Display tasks by pet
    st.markdown("**Current Tasks:**")
    for pet in owner.pets:
        with st.expander(f"{pet.name} ({len(pet.get_tasks())} tasks)"):
            if pet.get_tasks():
                for task in pet.get_tasks():
                    st.write(f"- {task.description} ({task.duration_minutes} min) [priority: {task.priority}]")
            else:
                st.write("No tasks yet.")

st.divider()

st.subheader("📋 Generate Schedule")
st.caption("Click below to generate a daily plan based on tasks and available time.")

if st.button("Generate schedule"):
    if not owner.pets or not owner.get_all_tasks():
        st.warning("Add at least one pet with tasks before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        schedule = scheduler.build_schedule(owner.available_time)
        plan_output = scheduler.explain_schedule(schedule)

        st.success("Schedule generated!")
        st.markdown("### Daily Plan")
        st.text(plan_output)
