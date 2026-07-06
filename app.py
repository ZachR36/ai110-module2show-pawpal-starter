import streamlit as st
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler, TimeWindow

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")
st.markdown("Your intelligent pet care scheduling assistant.")

# Initialize session state
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", available_time=120, start_hour=8, sort_preference="priority")
if "pet_counter" not in st.session_state:
    st.session_state.pet_counter = 1
if "task_counter" not in st.session_state:
    st.session_state.task_counter = 1

owner = st.session_state.owner

# ============================================================================
# OWNER SETUP
# ============================================================================

st.subheader("👤 Owner Setup")
with st.expander("Configure Owner & Preferences", expanded=False):
    col1, col2, col3 = st.columns(3)
    with col1:
        owner.name = st.text_input("Owner name", value=owner.name, key="owner_name")
    with col2:
        owner.available_time = st.number_input("Available time per day (minutes)",
                                               min_value=15, max_value=1440,
                                               value=owner.available_time, key="available_time")
    with col3:
        owner.start_hour = st.number_input("Start hour (0-23)",
                                           min_value=0, max_value=23,
                                           value=owner.start_hour, key="start_hour")

    st.markdown("**Sort Preference** (how to order tasks):")
    owner.sort_preference = st.radio(
        "Choose how tasks are prioritized in the schedule:",
        ["priority", "duration", "pet"],
        format_func=lambda x: {
            "priority": "Priority (high → low)",
            "duration": "Duration (shortest first)",
            "pet": "Pet (complete one pet before next)"
        }[x],
        horizontal=True,
        key="sort_pref"
    )

    st.markdown("**Availability Windows** (when you're available):")
    use_custom_windows = st.checkbox("Use custom availability windows?", key="custom_windows")
    if use_custom_windows:
        st.caption("Example: 8:00-12:00, 2:00-6:00 (lunch break)")
        num_windows = st.number_input("Number of time windows", min_value=1, max_value=5, value=1, key="num_windows")
        windows = []
        for i in range(num_windows):
            col1, col2 = st.columns(2)
            with col1:
                start = st.time_input(f"Window {i+1} start", value=datetime.strptime("08:00", "%H:%M").time(), key=f"window_start_{i}")
            with col2:
                end = st.time_input(f"Window {i+1} end", value=datetime.strptime("12:00", "%H:%M").time(), key=f"window_end_{i}")
            windows.append(TimeWindow(start_time=start.strftime("%H:%M"), end_time=end.strftime("%H:%M")))
        owner.set_availability_windows(windows)
    else:
        owner.availability_windows = owner._create_default_window()

# Display owner summary
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Owner", owner.name)
with col2:
    st.metric("Available Time", f"{owner.available_time} min")
with col3:
    st.metric("Sort By", owner.sort_preference.title())

if st.button("🔄 Reset All"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.divider()

# ============================================================================
# PET & TASK MANAGEMENT
# ============================================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("🐾 Pets")
    with st.expander("Add Pet", expanded=False):
        pet_name = st.text_input("Pet name", value="Biscuit", key="pet_name_input")
        species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "hamster", "other"], key="species_input")
        if st.button("Add pet"):
            new_pet = Pet(id=st.session_state.pet_counter, name=pet_name, species=species)
            owner.add_pet(new_pet)
            st.session_state.pet_counter += 1
            st.success(f"✅ Added {pet_name} ({species})")

    if owner.pets:
        st.markdown("**Current Pets:**")
        for pet in owner.pets:
            col_pet1, col_pet2 = st.columns([3, 1])
            with col_pet1:
                st.write(f"🐾 **{pet.name}** ({pet.species})")
                st.caption(f"{len(pet.get_tasks())} active task(s) | {len(pet.completed_tasks)} completed")
            with col_pet2:
                if st.button("Remove", key=f"remove_pet_{pet.id}"):
                    owner.remove_pet(pet.id)
                    st.rerun()
    else:
        st.info("No pets yet. Add one above!")

with col2:
    st.subheader("✏️ Add Task")
    if not owner.pets:
        st.warning("Add a pet first before adding tasks.")
    else:
        with st.expander("Add New Task", expanded=False):
            pet_options = [pet.name for pet in owner.pets]
            selected_pet_name = st.selectbox("Assign to pet", pet_options, key="task_pet_select")

            col_t1, col_t2 = st.columns(2)
            with col_t1:
                task_title = st.text_input("Task description", value="Morning walk", key="task_title_input")
                duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=30, key="task_duration_input")
            with col_t2:
                priority = st.selectbox("Priority", ["high", "medium", "low"], index=0, key="task_priority_input")
                recurrence = st.selectbox("Recurrence", ["once", "daily", "weekly"], key="task_recurrence_input")

            scheduled_time = st.text_input("Scheduled time (HH:MM, optional)", value="", key="task_scheduled_time")

            if st.button("Add task"):
                selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)
                new_task = Task(
                    id=st.session_state.task_counter,
                    description=task_title,
                    duration_minutes=int(duration),
                    priority=priority,
                    frequency=recurrence,
                    recurrence_type=recurrence,
                    scheduled_time=scheduled_time if scheduled_time else None,
                    due_date=datetime.now()
                )
                selected_pet.add_task(new_task)
                st.session_state.task_counter += 1
                st.success(f"✅ Added '{task_title}' to {selected_pet_name}")

# Display tasks organized by pet
st.markdown("**All Tasks:**")
if owner.pets:
    for pet in owner.pets:
        with st.expander(f"🐾 {pet.name} ({len(pet.get_tasks())} active, {len(pet.completed_tasks)} completed)"):
            # Active tasks table
            if pet.get_tasks():
                st.markdown("*Active Tasks:*")
                task_data = []
                for task in pet.get_tasks():
                    fixed_label = "📌 " + task.scheduled_time if task.scheduled_time else "—"
                    task_data.append({
                        "Description": task.description,
                        "Duration (min)": task.duration_minutes,
                        "Priority": task.priority,
                        "Recurrence": task.recurrence_type,
                        "Scheduled Time": fixed_label
                    })
                st.table(task_data)

                # Action buttons below table
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    task_to_complete = st.selectbox(
                        "Mark task as done:",
                        [t.description for t in pet.get_tasks()],
                        key=f"complete_select_{pet.id}"
                    )
                    if st.button("✓ Mark Complete", key=f"complete_btn_{pet.id}"):
                        task_id = next(t.id for t in pet.get_tasks() if t.description == task_to_complete)
                        pet.complete_task(task_id)
                        st.rerun()

                with col_b2:
                    task_to_remove = st.selectbox(
                        "Remove task:",
                        [t.description for t in pet.get_tasks()],
                        key=f"remove_select_{pet.id}"
                    )
                    if st.button("✕ Remove Task", key=f"remove_btn_{pet.id}"):
                        task_id = next(t.id for t in pet.get_tasks() if t.description == task_to_remove)
                        pet.remove_task(task_id)
                        st.rerun()
            else:
                st.caption("No active tasks.")

            # Completed tasks table
            if pet.completed_tasks:
                st.markdown("*Completed Tasks:*")
                completed_data = []
                for task in pet.completed_tasks:
                    completed_data.append({
                        "Description": task.description,
                        "Duration (min)": task.duration_minutes,
                        "Completed On": task.completed_on.strftime('%m/%d/%y')
                    })
                st.table(completed_data)
else:
    st.info("No pets to display tasks.")

st.divider()

# ============================================================================
# SCHEDULE GENERATION
# ============================================================================

st.subheader("📋 Generate Schedule")

col1, col2 = st.columns(2)
with col1:
    filter_by = st.radio("Display schedule grouped by:", ["pet", "completion"], horizontal=True, key="filter_by")
with col2:
    schedule_type = st.radio("Schedule format:", ["simple", "with_times"],
                            format_func=lambda x: "Simple (task list)" if x == "simple" else "With Times (slots)",
                            horizontal=True, key="schedule_type")

if st.button("🚀 Generate Schedule", use_container_width=True):
    if not owner.pets or not owner.get_all_tasks():
        st.warning("⚠️ Add at least one pet with tasks before generating a schedule.")
    else:
        scheduler = Scheduler(owner)

        if schedule_type == "with_times":
            schedule = scheduler.schedule_with_times(owner.available_time)
        else:
            schedule = scheduler.build_schedule(owner.available_time, filter_by=filter_by)

        plan_output = scheduler.explain_schedule(schedule)

        # Display results in tabs
        tab1, tab2 = st.tabs(["📅 Plan", "📊 Details"])

        with tab1:
            st.success("✅ Schedule generated!")
            st.text(plan_output)

        with tab2:
            col1, col2, col3 = st.columns(3)
            with col1:
                scheduled_count = len(schedule.get("scheduled_tasks", []))
                st.metric("Tasks Scheduled", scheduled_count)
            with col2:
                skipped_count = len(schedule.get("skipped_tasks", []))
                st.metric("Tasks Skipped", skipped_count)
            with col3:
                st.metric("Time Remaining", f"{schedule.get('time_remaining', 0)} min")

            if schedule.get("warnings"):
                st.warning("⚠️ Scheduling Warnings:")
                for warning in schedule["warnings"]:
                    st.caption(f"• {warning}")

            if schedule.get("skipped_tasks"):
                st.info("**Skipped Tasks** (due to insufficient time):")
                skipped_data = []
                for task in schedule["skipped_tasks"]:
                    skipped_data.append({
                        "Task": task.description,
                        "Duration (min)": task.duration_minutes,
                        "Priority": task.priority
                    })
                st.table(skipped_data)

st.divider()

st.markdown(
    """
    ---
    **PawPal+ Tips:**
    - Set your **sort preference** to control how tasks are ordered
    - Use **scheduled times** (📌) to pin important tasks to specific times
    - Mark tasks **Done** when completed (recurring tasks auto-create for tomorrow)
    - Check **warnings** if a schedule doesn't include all your tasks
    """
)
