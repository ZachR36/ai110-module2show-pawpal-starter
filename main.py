from pawpal_system import Owner, Pet, Task, Scheduler, TimeWindow

# Create an Owner with different sort preferences we can test
owner = Owner(name="Jordan", available_time=120, start_hour=8, sort_preference="priority")

# Create Pets
dog = Pet(id=1, name="Biscuit", species="dog")
cat = Pet(id=2, name="Whiskers", species="cat")

# Add Tasks OUT OF ORDER to test sorting
# Dog tasks
dog.add_task(Task(id=1, description="Playtime", duration_minutes=20, priority="medium", frequency="daily"))
dog.add_task(Task(id=2, description="Morning walk", duration_minutes=30, priority="high", frequency="daily"))
dog.add_task(Task(id=3, description="Treat", duration_minutes=5, priority="low", frequency="daily"))

# Cat tasks
cat.add_task(Task(id=4, description="Litter box cleaning", duration_minutes=10, priority="medium", frequency="daily"))
cat.add_task(Task(id=5, description="Feeding", duration_minutes=5, priority="high", frequency="daily"))
cat.add_task(Task(id=6, description="Grooming", duration_minutes=15, priority="low", frequency="daily"))

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# Test 1: Sort by priority (default), filter by pet
print("=" * 60)
print("TEST 1: Sort by PRIORITY, Filter by PET")
print("=" * 60)
scheduler = Scheduler(owner)
schedule = scheduler.build_schedule(owner.available_time, filter_by="pet")
print(scheduler.explain_schedule(schedule))
print("\nTime remaining:", schedule["time_remaining"], "minutes")

# Test 2: Sort by duration, filter by pet
print("\n" + "=" * 60)
print("TEST 2: Sort by DURATION, Filter by PET")
print("=" * 60)
owner.sort_preference = "duration"
scheduler = Scheduler(owner)
schedule = scheduler.build_schedule(owner.available_time, filter_by="pet")
print(scheduler.explain_schedule(schedule))
print("\nTime remaining:", schedule["time_remaining"], "minutes")

# Test 3: Sort by pet, filter by pet
print("\n" + "=" * 60)
print("TEST 3: Sort by PET, Filter by PET")
print("=" * 60)
owner.sort_preference = "pet"
scheduler = Scheduler(owner)
schedule = scheduler.build_schedule(owner.available_time, filter_by="pet")
print(scheduler.explain_schedule(schedule))
print("\nTime remaining:", schedule["time_remaining"], "minutes")

# Test 4: Sort by priority, filter by completion status
print("\n" + "=" * 60)
print("TEST 4: Sort by PRIORITY, Filter by COMPLETION")
print("=" * 60)
owner.sort_preference = "priority"
# Mark a few tasks as completed
dog.tasks[1].mark_complete()  # Morning walk
cat.tasks[1].mark_complete()  # Cat feeding
scheduler = Scheduler(owner)
schedule = scheduler.build_schedule(owner.available_time, filter_by="completion")
print(scheduler.explain_schedule(schedule))
print("\nTime remaining:", schedule["time_remaining"], "minutes")

# Test 5: Test schedule_with_times
print("\n" + "=" * 60)
print("TEST 5: Schedule with TIMES (8:00 AM start)")
print("=" * 60)
owner.sort_preference = "priority"
scheduler = Scheduler(owner)
timed_schedule = scheduler.schedule_with_times(owner.available_time)
print(f"Daily plan for {owner.name}:")
for timed_task in timed_schedule["timed_tasks"]:
    task = timed_task["task"]
    start = timed_task["start_time"]
    end = timed_task["end_time"]
    print(f"  {start} - {end}: {task.description} ({task.duration_minutes} min) [priority: {task.priority}]")
print(f"\nTime remaining: {timed_schedule['time_remaining']} minutes")

# Test 6: Fixed-time tasks
print("\n" + "=" * 60)
print("TEST 6: FIXED-TIME TASKS")
print("=" * 60)
owner2 = Owner(name="Sarah", available_time=120, start_hour=8, sort_preference="priority")
dog2 = Pet(id=1, name="Max", species="dog")
cat2 = Pet(id=2, name="Luna", species="cat")

dog2.add_task(Task(id=1, description="Morning walk", duration_minutes=30, priority="high", frequency="daily", scheduled_time="09:00"))
dog2.add_task(Task(id=2, description="Feeding", duration_minutes=10, priority="high", frequency="daily"))
cat2.add_task(Task(id=3, description="Litter box", duration_minutes=10, priority="medium", frequency="daily", scheduled_time="11:00"))
cat2.add_task(Task(id=4, description="Playtime", duration_minutes=20, priority="medium", frequency="daily"))

owner2.add_pet(dog2)
owner2.add_pet(cat2)

scheduler2 = Scheduler(owner2)
timed_schedule2 = scheduler2.schedule_with_times(owner2.available_time)
print(scheduler2.explain_schedule(timed_schedule2))
print(f"\nTime remaining: {timed_schedule2['time_remaining']} minutes")

# Test 7: Multiple availability windows
print("\n" + "=" * 60)
print("TEST 7: MULTIPLE AVAILABILITY WINDOWS (8-12, 2-6pm)")
print("=" * 60)
owner3 = Owner(name="Alex", available_time=120, start_hour=8, sort_preference="priority")
dog3 = Pet(id=1, name="Buddy", species="dog")

dog3.add_task(Task(id=1, description="Morning walk", duration_minutes=30, priority="high", frequency="daily"))
dog3.add_task(Task(id=2, description="Lunch break play", duration_minutes=20, priority="medium", frequency="daily", scheduled_time="14:00"))
dog3.add_task(Task(id=3, description="Feeding", duration_minutes=10, priority="high", frequency="daily"))
dog3.add_task(Task(id=4, description="Evening walk", duration_minutes=30, priority="high", frequency="daily"))

owner3.add_pet(dog3)
owner3.set_availability_windows([
    TimeWindow(start_time="08:00", end_time="12:00"),
    TimeWindow(start_time="14:00", end_time="18:00")
])

scheduler3 = Scheduler(owner3)
timed_schedule3 = scheduler3.schedule_with_times(owner3.available_time)
print(scheduler3.explain_schedule(timed_schedule3))
print(f"\nTime remaining: {timed_schedule3['time_remaining']} minutes")

# Test 8: Task completion and removal
print("\n" + "=" * 60)
print("TEST 8: TASK COMPLETION & REMOVAL")
print("=" * 60)
owner4 = Owner(name="Jamie", available_time=90, start_hour=8, sort_preference="priority")
dog4 = Pet(id=1, name="Rocky", species="dog")

task1 = Task(id=1, description="Walk", duration_minutes=30, priority="high", frequency="daily")
task2 = Task(id=2, description="Feed", duration_minutes=10, priority="high", frequency="daily")
task3 = Task(id=3, description="Play", duration_minutes=20, priority="medium", frequency="daily")

dog4.add_task(task1)
dog4.add_task(task2)
dog4.add_task(task3)
owner4.add_pet(dog4)

print(f"Before completion: {len(dog4.get_tasks())} active tasks")
print(f"  - {', '.join([t.description for t in dog4.get_tasks()])}")

dog4.complete_task(task2.id)

print(f"After marking 'Feed' complete: {len(dog4.get_tasks())} active tasks")
print(f"  - {', '.join([t.description for t in dog4.get_tasks()])}")
print(f"Completed tasks: {len(dog4.completed_tasks)}")
print(f"  - {', '.join([t.description for t in dog4.completed_tasks])}")

# Test 9: Recurring tasks with due dates
print("\n" + "=" * 60)
print("TEST 9: RECURRING TASKS WITH DUE DATES")
print("=" * 60)
from datetime import datetime as dt, timedelta

owner6 = Owner(name="Morgan", available_time=90, start_hour=8, sort_preference="priority")
dog6 = Pet(id=1, name="Daisy", species="dog")

today = dt.now().date()
tomorrow = today + timedelta(days=1)

# Create recurring daily tasks with due dates
task_walk = Task(
    id=1,
    description="Morning walk",
    duration_minutes=30,
    priority="high",
    frequency="daily",
    recurrence_type="daily",
    due_date=dt.combine(today, dt.min.time())
)
task_feed = Task(
    id=2,
    description="Feed",
    duration_minutes=10,
    priority="high",
    frequency="daily",
    recurrence_type="daily",
    due_date=dt.combine(today, dt.min.time())
)

dog6.add_task(task_walk)
dog6.add_task(task_feed)
owner6.add_pet(dog6)

print(f"Before completion:")
print(f"  Active tasks: {len(dog6.get_tasks())}")
for t in dog6.get_tasks():
    due_str = t.due_date.strftime("%Y-%m-%d") if t.due_date else "No due date"
    print(f"    - {t.description} (due: {due_str}, recurrence: {t.recurrence_type})")

print(f"\nCompleting 'Morning walk'...")
dog6.complete_task(task_walk.id)

print(f"\nAfter completion:")
print(f"  Active tasks: {len(dog6.get_tasks())}")
for t in dog6.get_tasks():
    due_str = t.due_date.strftime("%Y-%m-%d") if t.due_date else "No due date"
    print(f"    - {t.description} (due: {due_str}, recurrence: {t.recurrence_type}, id: {t.id})")

print(f"\n  Completed tasks: {len(dog6.completed_tasks)}")
for t in dog6.completed_tasks:
    due_str = t.due_date.strftime("%Y-%m-%d") if t.due_date else "No due date"
    print(f"    - {t.description} (was due: {due_str})")

next_walk = next((t for t in dog6.get_tasks() if "walk" in t.description.lower()), None)
if next_walk:
    next_due = next_walk.due_date.strftime("%Y-%m-%d") if next_walk.due_date else "No due date"
    print(f"\nNext walk is due: {next_due} (tomorrow should be {tomorrow})")

# Test 10: Fixed-time collision (two tasks at same time)
print("\n" + "=" * 60)
print("TEST 10: FIXED-TIME COLLISION HANDLING")
print("=" * 60)
owner5 = Owner(name="Casey", available_time=120, start_hour=8, sort_preference="priority")
dog5 = Pet(id=1, name="Scout", species="dog")

dog5.add_task(Task(id=1, description="High priority walk", duration_minutes=30, priority="high", frequency="daily", scheduled_time="09:00"))
dog5.add_task(Task(id=2, description="Low priority feed", duration_minutes=10, priority="low", frequency="daily", scheduled_time="09:00"))
dog5.add_task(Task(id=3, description="Medium priority play", duration_minutes=20, priority="medium", frequency="daily"))

owner5.add_pet(dog5)

scheduler5 = Scheduler(owner5)
timed_schedule5 = scheduler5.schedule_with_times(owner5.available_time)
print(scheduler5.explain_schedule(timed_schedule5))
print(f"\nNote: Only the high-priority task should get the 9:00 AM slot.")

# Test 11: Conflict detection (same pet, overlapping times)
print("\n" + "=" * 60)
print("TEST 11: CONFLICT DETECTION - SAME PET OVERLAP")
print("=" * 60)
owner7 = Owner(name="Taylor", available_time=120, start_hour=8, sort_preference="priority")
dog7 = Pet(id=1, name="Charlie", species="dog")

# Add two tasks that will overlap due to greedy floating task placement
dog7.add_task(Task(id=1, description="Morning walk", duration_minutes=30, priority="high", frequency="daily", scheduled_time="08:00"))
dog7.add_task(Task(id=2, description="Breakfast", duration_minutes=15, priority="high", frequency="daily", scheduled_time="08:20"))
dog7.add_task(Task(id=3, description="Play session", duration_minutes=20, priority="medium", frequency="daily"))

owner7.add_pet(dog7)

scheduler7 = Scheduler(owner7)
timed_schedule7 = scheduler7.schedule_with_times(owner7.available_time)
print(scheduler7.explain_schedule(timed_schedule7))

# Test 12: Conflict detection (manually created overlapping tasks to show detection)
print("\n" + "=" * 60)
print("TEST 12: CONFLICT DETECTION - MANUAL OVERLAP SIMULATION")
print("=" * 60)
print("Note: Our scheduler prevents overlaps by design, so we manually create")
print("overlapping tasks to demonstrate the conflict detection system.\n")

owner8 = Owner(name="Riley", available_time=120, start_hour=8, sort_preference="priority")
dog8 = Pet(id=1, name="Buddy", species="dog")
cat8 = Pet(id=2, name="Whiskers", species="cat")

task_dog_walk = Task(id=1, description="Dog walk", duration_minutes=30, priority="high", frequency="daily")
task_cat_feed = Task(id=2, description="Cat feeding", duration_minutes=5, priority="high", frequency="daily")
task_dog_feed = Task(id=3, description="Dog feeding", duration_minutes=10, priority="high", frequency="daily")
task_cat_play = Task(id=4, description="Cat playtime", duration_minutes=15, priority="medium", frequency="daily")

dog8.add_task(task_dog_walk)
dog8.add_task(task_dog_feed)
cat8.add_task(task_cat_feed)
cat8.add_task(task_cat_play)

owner8.add_pet(dog8)
owner8.add_pet(cat8)

scheduler8 = Scheduler(owner8)

# Manually create a schedule with overlapping tasks to test detection
# Dog walk: 09:00-09:30, Cat feeding: 09:15-09:20 (overlaps!)
synthetic_timed_tasks = [
    {"task": task_dog_walk, "start_time": "09:00", "end_time": "09:30", "type": "fixed"},
    {"task": task_cat_feed, "start_time": "09:15", "end_time": "09:20", "type": "fixed"},
    {"task": task_dog_feed, "start_time": "08:00", "end_time": "08:10", "type": "floating"},
    {"task": task_cat_play, "start_time": "08:10", "end_time": "08:25", "type": "floating"}
]

# Test the conflict detection
conflicts = scheduler8.detect_conflicts(synthetic_timed_tasks)

print("Synthetic schedule (with intentional overlap):")
for timed in synthetic_timed_tasks:
    print(f"  {timed['start_time']}-{timed['end_time']}: {timed['task'].description} ({timed['task'].priority})")

print("\nConflicts detected:")
if conflicts:
    for conflict in conflicts:
        print(f"  ⚠️  {conflict}")
else:
    print("  None")
