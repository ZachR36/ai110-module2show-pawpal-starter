# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Our design uses four core classes that work together to manage pet care scheduling:

**Task** represents individual pet care activities. Each task has a description, duration, priority level, frequency, and completion status. Tasks can be marked complete and checked for overdue status.

**Pet** stores information about a specific pet (name and species) and maintains a list of tasks associated with that pet. It provides methods to add, remove, and retrieve tasks.

**Owner** represents the pet owner and serves as the central point of access. It holds multiple pets, tracks available time per day, stores user preferences, and provides a method to retrieve all tasks across all pets at once.

**Scheduler** is the "brain" of the system. It takes an Owner as input and implements the scheduling logic: retrieving tasks, prioritizing them based on constraints, building a daily schedule that fits within available time, and explaining the reasoning behind the schedule.

The architecture follows a clear hierarchy: Owner → Pets → Tasks, with Scheduler acting as an orchestrator that uses this hierarchy to generate intelligent daily plans.

**b. Design changes**

Yes, we made several adjustments to the skeleton before implementation:

1. **Added ID fields**: Task and Pet lacked unique identifiers, but the remove methods (`remove_task(task_id)` and `remove_pet(pet_id)`) required them. We added `id: int` fields to both classes so that removal logic could identify which object to remove.

2. **Initialized Owner attributes**: The Owner `__init__` was incomplete—it took parameters but didn't store them. We added `self.name`, `self.available_time`, `self.preferences`, and crucially `self.pets = []` to enable the add/remove/get_all_tasks methods to function.

3. **Clarified return type for build_schedule**: The method signature didn't specify what a "schedule" object is. We changed the return type to `DailySchedule` (with a TODO comment to decide if we need that as a separate class) so the output structure is clear.

These changes resolved logical inconsistencies in the skeleton without changing the overall design—they ensured the class structure could actually support the intended behavior.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
