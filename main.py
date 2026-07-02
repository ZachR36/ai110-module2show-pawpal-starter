from pawpal_system import Owner, Pet, Task, Scheduler

# Create an Owner
owner = Owner(name="Jordan", available_time=120, preferences={"prefer_morning": True})

# Create Pets
dog = Pet(id=1, name="Biscuit", species="dog")
cat = Pet(id=2, name="Whiskers", species="cat")

# Add Tasks to the dog
dog.add_task(Task(id=1, description="Morning walk", duration_minutes=30, priority="high", frequency="daily"))
dog.add_task(Task(id=2, description="Feeding", duration_minutes=10, priority="high", frequency="daily"))
dog.add_task(Task(id=3, description="Playtime", duration_minutes=20, priority="medium", frequency="daily"))

# Add Tasks to the cat
cat.add_task(Task(id=4, description="Feeding", duration_minutes=5, priority="high", frequency="daily"))
cat.add_task(Task(id=5, description="Litter box cleaning", duration_minutes=10, priority="medium", frequency="daily"))

# Add pets to owner
owner.add_pet(dog)
owner.add_pet(cat)

# Create scheduler and build schedule
scheduler = Scheduler(owner)
schedule = scheduler.build_schedule(owner.available_time)

# Print the schedule
print("=" * 50)
print("Today's Schedule")
print("=" * 50)
print(scheduler.explain_schedule(schedule))
print("\nTime remaining:", schedule["time_remaining"], "minutes")
