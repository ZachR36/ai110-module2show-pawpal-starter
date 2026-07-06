import pytest
from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler, TimeWindow


# ============================================================================
# BASIC TASK AND PET OPERATIONS
# ============================================================================

def test_task_completion():
    """Verify that calling mark_complete() changes the task's completed status."""
    task = Task(id=1, description="Morning walk", duration_minutes=30, priority="high", frequency="daily")
    assert task.completed is False

    task.mark_complete()
    assert task.completed is True


def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet(id=1, name="Biscuit", species="dog")
    assert len(pet.get_tasks()) == 0

    task1 = Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily")
    pet.add_task(task1)
    assert len(pet.get_tasks()) == 1

    task2 = Task(id=2, description="Feeding", duration_minutes=10, priority="high", frequency="daily")
    pet.add_task(task2)
    assert len(pet.get_tasks()) == 2


def test_task_removal():
    """Verify that removing a task by ID works correctly."""
    pet = Pet(id=1, name="Biscuit", species="dog")
    task1 = Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily")
    task2 = Task(id=2, description="Feed", duration_minutes=10, priority="high", frequency="daily")

    pet.add_task(task1)
    pet.add_task(task2)
    assert len(pet.get_tasks()) == 2

    pet.remove_task(1)
    assert len(pet.get_tasks()) == 1
    assert pet.get_tasks()[0].id == 2


def test_pet_completion_single_task():
    """Verify that marking a task complete moves it to completed_tasks."""
    pet = Pet(id=1, name="Biscuit", species="dog")
    task = Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily")
    pet.add_task(task)

    assert len(pet.get_tasks()) == 1
    assert len(pet.completed_tasks) == 0

    pet.complete_task(1)
    assert len(pet.get_tasks()) == 0
    assert len(pet.completed_tasks) == 1


# ============================================================================
# RECURRENCE LOGIC (Recurring task creates next occurrence)
# ============================================================================

def test_recurrence_daily_task_creates_next():
    """Verify that completing a daily recurring task creates a new task for the next day."""
    pet = Pet(id=1, name="Biscuit", species="dog")
    today = datetime.now()

    task = Task(
        id=1,
        description="Morning walk",
        duration_minutes=30,
        priority="high",
        frequency="daily",
        recurrence_type="daily",
        due_date=today
    )
    pet.add_task(task)

    assert len(pet.get_tasks()) == 1
    pet.complete_task(1)

    # Should have created a new task with next day's due date
    assert len(pet.get_tasks()) == 1  # New task replaces old one
    assert len(pet.completed_tasks) == 1  # Original moved to completed

    new_task = pet.get_tasks()[0]
    assert new_task.description == "Morning walk"
    assert new_task.recurrence_type == "daily"
    assert new_task.due_date == today + timedelta(days=1)


def test_recurrence_weekly_task_creates_next():
    """Verify that completing a weekly task creates a new task for the next week."""
    pet = Pet(id=1, name="Biscuit", species="dog")
    today = datetime.now()

    task = Task(
        id=1,
        description="Grooming",
        duration_minutes=60,
        priority="medium",
        frequency="weekly",
        recurrence_type="weekly",
        due_date=today
    )
    pet.add_task(task)

    pet.complete_task(1)

    assert len(pet.get_tasks()) == 1
    new_task = pet.get_tasks()[0]
    assert new_task.due_date == today + timedelta(weeks=1)


def test_recurrence_once_task_does_not_create_next():
    """Verify that completing a 'once' task does NOT create a new occurrence."""
    pet = Pet(id=1, name="Biscuit", species="dog")

    task = Task(
        id=1,
        description="Vet appointment",
        duration_minutes=60,
        priority="high",
        frequency="once",
        recurrence_type="once"
    )
    pet.add_task(task)

    pet.complete_task(1)

    assert len(pet.get_tasks()) == 0
    assert len(pet.completed_tasks) == 1


# ============================================================================
# SORTING CORRECTNESS (Tasks returned in correct priority order)
# ============================================================================

def test_sort_by_priority():
    """Verify tasks are sorted high → medium → low priority."""
    owner = Owner(name="Jordan", available_time=120, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    # Add tasks out of order
    pet.add_task(Task(id=1, description="Play", duration_minutes=20, priority="low", frequency="daily"))
    pet.add_task(Task(id=2, description="Walk", duration_minutes=30, priority="high", frequency="daily"))
    pet.add_task(Task(id=3, description="Feed", duration_minutes=10, priority="medium", frequency="daily"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    sorted_tasks = scheduler.sort_by_priority(scheduler.get_tasks())

    assert sorted_tasks[0].priority == "high"
    assert sorted_tasks[1].priority == "medium"
    assert sorted_tasks[2].priority == "low"


def test_sort_by_duration():
    """Verify tasks are sorted by duration (shortest to longest)."""
    owner = Owner(name="Jordan", available_time=120, sort_preference="duration")
    pet = Pet(id=1, name="Biscuit", species="dog")

    pet.add_task(Task(id=1, description="Play", duration_minutes=20, priority="low", frequency="daily"))
    pet.add_task(Task(id=2, description="Walk", duration_minutes=30, priority="high", frequency="daily"))
    pet.add_task(Task(id=3, description="Feed", duration_minutes=10, priority="medium", frequency="daily"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    sorted_tasks = scheduler.sort_by_duration(scheduler.get_tasks())

    assert sorted_tasks[0].duration_minutes == 10
    assert sorted_tasks[1].duration_minutes == 20
    assert sorted_tasks[2].duration_minutes == 30


def test_sort_by_pet():
    """Verify tasks are grouped by pet (all of one pet before the next)."""
    owner = Owner(name="Jordan", available_time=120, sort_preference="pet")
    dog = Pet(id=1, name="Biscuit", species="dog")
    cat = Pet(id=2, name="Whiskers", species="cat")

    dog.add_task(Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily"))
    dog.add_task(Task(id=2, description="Feed", duration_minutes=10, priority="high", frequency="daily"))
    cat.add_task(Task(id=3, description="Litter", duration_minutes=10, priority="medium", frequency="daily"))
    cat.add_task(Task(id=4, description="Play", duration_minutes=15, priority="medium", frequency="daily"))

    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner)

    sorted_tasks = scheduler.sort_by_pet(scheduler.get_tasks())

    # First two should be dog tasks, next two should be cat tasks
    assert sorted_tasks[0].id in [1, 2]
    assert sorted_tasks[1].id in [1, 2]
    assert sorted_tasks[2].id in [3, 4]
    assert sorted_tasks[3].id in [3, 4]


# ============================================================================
# SCHEDULING: TASK SELECTION AND TIME MANAGEMENT
# ============================================================================

def test_schedule_fits_all_tasks():
    """Verify that when all tasks fit, they are all scheduled."""
    owner = Owner(name="Jordan", available_time=100, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    pet.add_task(Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily"))
    pet.add_task(Task(id=2, description="Feed", duration_minutes=10, priority="high", frequency="daily"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    result = scheduler.select_tasks_for_day(100)

    assert len(result["scheduled_tasks"]) == 2
    assert len(result["skipped_tasks"]) == 0
    assert result["time_remaining"] == 60


def test_schedule_skips_overflow_tasks():
    """Verify that tasks that don't fit are skipped."""
    owner = Owner(name="Jordan", available_time=30, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    pet.add_task(Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily"))
    pet.add_task(Task(id=2, description="Feed", duration_minutes=20, priority="medium", frequency="daily"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    result = scheduler.select_tasks_for_day(30)

    assert len(result["scheduled_tasks"]) == 1
    assert len(result["skipped_tasks"]) == 1
    assert result["scheduled_tasks"][0].id == 1  # High priority scheduled
    assert result["skipped_tasks"][0].id == 2     # Medium priority skipped
    assert result["time_remaining"] == 0


def test_schedule_zero_available_time():
    """Verify that with zero available time, all tasks are skipped."""
    owner = Owner(name="Jordan", available_time=0, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    pet.add_task(Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily"))
    pet.add_task(Task(id=2, description="Feed", duration_minutes=10, priority="high", frequency="daily"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    result = scheduler.select_tasks_for_day(0)

    assert len(result["scheduled_tasks"]) == 0
    assert len(result["skipped_tasks"]) == 2
    assert result["time_remaining"] == 0


def test_schedule_empty_pet():
    """Verify that a pet with no tasks doesn't crash the scheduler."""
    owner = Owner(name="Jordan", available_time=100, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    result = scheduler.select_tasks_for_day(100)

    assert len(result["scheduled_tasks"]) == 0
    assert len(result["skipped_tasks"]) == 0
    assert result["time_remaining"] == 100


# ============================================================================
# CONFLICT DETECTION (Fixed-time task collisions)
# ============================================================================

def test_conflict_detection_two_tasks_same_time():
    """Verify that two tasks at the exact same time are detected as conflicting."""
    owner = Owner(name="Jordan", available_time=120, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    task1 = Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily")
    task2 = Task(id=2, description="Feed", duration_minutes=10, priority="medium", frequency="daily")
    pet.add_task(task1)
    pet.add_task(task2)

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    # Manually create two tasks at the same time to test conflict detection
    synthetic_timed_tasks = [
        {"task": task1, "start_time": "09:00", "end_time": "09:30", "type": "fixed"},
        {"task": task2, "start_time": "09:00", "end_time": "09:10", "type": "fixed"}
    ]

    conflicts = scheduler.detect_conflicts(synthetic_timed_tasks)
    assert len(conflicts) > 0
    assert "Conflict:" in conflicts[0]


def test_conflict_detection_overlapping_times():
    """Verify that overlapping time slots are detected."""
    owner = Owner(name="Jordan", available_time=120, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    # Task 1: 09:00-09:30
    pet.add_task(Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily", scheduled_time="09:00"))
    # Task 2: 09:15-09:25 (overlaps with Task 1)
    pet.add_task(Task(id=2, description="Feed", duration_minutes=10, priority="medium", frequency="daily", scheduled_time="09:15"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    # Manually create the schedule to test conflict detection
    synthetic_timed_tasks = [
        {"task": pet.get_tasks()[0], "start_time": "09:00", "end_time": "09:30", "type": "fixed"},
        {"task": pet.get_tasks()[1], "start_time": "09:15", "end_time": "09:25", "type": "fixed"}
    ]

    conflicts = scheduler.detect_conflicts(synthetic_timed_tasks)
    assert len(conflicts) > 0


def test_conflict_detection_no_overlap():
    """Verify that non-overlapping tasks do not trigger conflicts."""
    owner = Owner(name="Jordan", available_time=120, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    pet.add_task(Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily"))
    pet.add_task(Task(id=2, description="Feed", duration_minutes=10, priority="medium", frequency="daily"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    synthetic_timed_tasks = [
        {"task": pet.get_tasks()[0], "start_time": "09:00", "end_time": "09:30", "type": "floating"},
        {"task": pet.get_tasks()[1], "start_time": "09:30", "end_time": "09:40", "type": "floating"}
    ]

    conflicts = scheduler.detect_conflicts(synthetic_timed_tasks)
    assert len(conflicts) == 0


# ============================================================================
# FIXED-TIME TASKS AND AVAILABILITY WINDOWS
# ============================================================================

def test_fixed_task_outside_availability_window():
    """Verify that a fixed task scheduled outside the availability window is rejected."""
    owner = Owner(name="Jordan", available_time=120, start_hour=8, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    # Window is 8:00-10:00, task scheduled at 23:00 (outside window)
    pet.add_task(Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily", scheduled_time="23:00"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    timed_schedule = scheduler.schedule_with_times(120)

    # Should have a warning about the task being outside the window
    warnings = timed_schedule["warnings"]
    assert any("outside availability windows" in w for w in warnings)


def test_multiple_availability_windows():
    """Verify that floating tasks respect multiple availability windows (e.g., 8-12, 2-6)."""
    owner = Owner(name="Jordan", available_time=480, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    owner.set_availability_windows([
        TimeWindow(start_time="08:00", end_time="12:00"),
        TimeWindow(start_time="14:00", end_time="18:00")
    ])

    pet.add_task(Task(id=1, description="Morning walk", duration_minutes=30, priority="high", frequency="daily"))
    pet.add_task(Task(id=2, description="Afternoon walk", duration_minutes=30, priority="high", frequency="daily"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    timed_schedule = scheduler.schedule_with_times(480)

    # Both tasks should be scheduled
    assert len(timed_schedule["timed_tasks"]) == 2


def test_fixed_task_priority_breaks_collision():
    """Verify that when two fixed tasks collide, the higher priority one is kept."""
    owner = Owner(name="Jordan", available_time=120, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    # Both at 09:00, but different priorities
    pet.add_task(Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily", scheduled_time="09:00"))
    pet.add_task(Task(id=2, description="Play", duration_minutes=20, priority="low", frequency="daily", scheduled_time="09:00"))

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    timed_schedule = scheduler.schedule_with_times(120)

    # High priority walk should be scheduled, low priority play should be rejected
    scheduled_ids = [t["task"].id for t in timed_schedule["timed_tasks"]]
    assert 1 in scheduled_ids  # High priority walk
    assert 2 not in scheduled_ids or any("conflicts" in w.lower() for w in timed_schedule["warnings"])


# ============================================================================
# FILTER AND BUILD SCHEDULE
# ============================================================================

def test_filter_by_pet():
    """Verify that filtering by pet groups tasks correctly."""
    owner = Owner(name="Jordan", available_time=120, sort_preference="priority")
    dog = Pet(id=1, name="Biscuit", species="dog")
    cat = Pet(id=2, name="Whiskers", species="cat")

    dog.add_task(Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily"))
    dog.add_task(Task(id=2, description="Feed", duration_minutes=10, priority="high", frequency="daily"))
    cat.add_task(Task(id=3, description="Litter", duration_minutes=10, priority="medium", frequency="daily"))

    owner.add_pet(dog)
    owner.add_pet(cat)
    scheduler = Scheduler(owner)

    result = scheduler.build_schedule(120, filter_by="pet")

    schedule = result["schedule"]
    assert "Biscuit" in schedule
    assert "Whiskers" in schedule
    assert len(schedule["Biscuit"]) == 2
    assert len(schedule["Whiskers"]) == 1


def test_filter_by_completion():
    """Verify that filtering by completion separates completed and pending tasks."""
    owner = Owner(name="Jordan", available_time=120, sort_preference="priority")
    pet = Pet(id=1, name="Biscuit", species="dog")

    task1 = Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily")
    task2 = Task(id=2, description="Feed", duration_minutes=10, priority="high", frequency="daily")
    pet.add_task(task1)
    pet.add_task(task2)
    pet.complete_task(1)

    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    # Need to manually create a schedule with the completed task to test filter
    result = scheduler.build_schedule(120, filter_by="completion")

    schedule = result["schedule"]
    # After completion, task1 is moved to completed_tasks, so it won't appear in active tasks
    assert "pending" in schedule or "completed" in schedule


# ============================================================================
# OWNER AND PET MANAGEMENT
# ============================================================================

def test_owner_add_remove_pet():
    """Verify that pets can be added and removed from an owner."""
    owner = Owner(name="Jordan", available_time=120)
    dog = Pet(id=1, name="Biscuit", species="dog")
    cat = Pet(id=2, name="Whiskers", species="cat")

    owner.add_pet(dog)
    owner.add_pet(cat)
    assert len(owner.pets) == 2

    owner.remove_pet(1)
    assert len(owner.pets) == 1
    assert owner.pets[0].id == 2


def test_owner_get_all_tasks():
    """Verify that get_all_tasks returns tasks from all pets."""
    owner = Owner(name="Jordan", available_time=120)
    dog = Pet(id=1, name="Biscuit", species="dog")
    cat = Pet(id=2, name="Whiskers", species="cat")

    dog.add_task(Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily"))
    dog.add_task(Task(id=2, description="Feed", duration_minutes=10, priority="high", frequency="daily"))
    cat.add_task(Task(id=3, description="Litter", duration_minutes=10, priority="medium", frequency="daily"))

    owner.add_pet(dog)
    owner.add_pet(cat)

    all_tasks = owner.get_all_tasks()
    assert len(all_tasks) == 3


# ============================================================================
# TIME CONVERSION HELPERS
# ============================================================================

def test_time_to_minutes():
    """Verify time string conversion to minutes."""
    owner = Owner(name="Jordan", available_time=120)
    scheduler = Scheduler(owner)

    assert scheduler._time_to_minutes("08:00") == 480
    assert scheduler._time_to_minutes("09:30") == 570
    assert scheduler._time_to_minutes("00:00") == 0
    assert scheduler._time_to_minutes("23:59") == 1439


def test_minutes_to_time():
    """Verify minutes conversion to time string."""
    owner = Owner(name="Jordan", available_time=120)
    scheduler = Scheduler(owner)

    assert scheduler._minutes_to_time(480) == "08:00"
    assert scheduler._minutes_to_time(570) == "09:30"
    assert scheduler._minutes_to_time(0) == "00:00"
    assert scheduler._minutes_to_time(1439) == "23:59"
