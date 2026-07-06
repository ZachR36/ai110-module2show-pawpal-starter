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

Our scheduler considers three major constraints:

1. **Time constraints**: Available time per day (configurable), and optional availability windows (e.g., 8am-12pm, 2-6pm). Tasks must fit within these windows or be skipped.

2. **Priority constraints**: Tasks have priority levels (high, medium, low) that determine selection order. High-priority tasks are scheduled first; if a task doesn't fit in available time, it's skipped in favor of lower-duration or higher-priority alternatives.

3. **Recurring task constraints**: Daily and weekly recurring tasks are cloned with updated due dates using Python's `timedelta`. Once completed, they automatically spawn the next occurrence.

4. **Owner preferences**: The owner can choose sort order (by priority, duration, or pet), which determines how tasks compete for limited time slots.

We decided priority and time were most critical because a schedule that fits more tasks but ignores priority would be useless (feeding a pet might be skipped for grooming). Owner-controlled sort preferences came second because they give flexibility but don't override the fundamental time constraint.

**b. Tradeoffs**

**Tradeoff: Greedy task placement vs. optimal packing**

Our scheduler uses a greedy algorithm: it sorts tasks by owner preference (priority/duration/pet), then slots them into available time in order. Once a task is placed, we move to the next. This means a 40-minute task placed first might "waste" a slot that could have held two 15-minute tasks, if the order were reversed.

**Why this is reasonable**: 
- **Predictability**: Users expect high-priority tasks to run first, not to be demoted because a different order packs better. Greedy respects the sort order the user selected.
- **Simplicity**: Optimal packing (bin-packing algorithms) is O(n²) or worse and much harder to explain. For small task lists (5-10 tasks per pet), greedy is fast enough.
- **Transparency**: It's easy to understand why each task was included or skipped. With complex packing, a user might wonder why their high-priority task didn't fit when "so much" time remained.

**Alternative we rejected**: We could use a bin-packing heuristic (try to minimize gaps), but that would violate sort priority—the user picked "sort by priority" for a reason. Breaking that contract would make the scheduler unpredictable.

**Edge case this affects**: If a user has 90 minutes and selects tasks [30min, 40min, 20min] (all high priority), greedy schedules [30, 40] and skips the 20min task. A packing algorithm might skip [30, 40] and schedule [40, 20] instead, but that would ignore priority order. Our choice respects the user's intent.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code throughout the project:
- **Design phase**: Asked questions about system tradeoffs (greedy vs. optimal packing) and got clear reasoning back
- **Implementation**: Delegated repetitive code (class definitions, method implementations) once I'd set the design direction
- **Testing**: Had AI write comprehensive test cases based on edge cases I identified; debugged one test failure together
- **UI integration**: Described the features needed and got a complete Streamlit app that matched the backend logic
- **Documentation**: Generated README sections, demo walkthroughs, and UML diagrams from the final code

**Most effective features:**
1. **Edit & Read tools** — Being able to see exactly what code was written and fix it immediately kept quality high
2. **Agent delegation** — When I needed to search for something across the codebase, I could spawn an agent to explore without cluttering the main session
3. **Iterative refinement** — I could say "this test is failing because X" and the AI would fix it without me having to re-explain the whole system
4. **Artifact design** — Got guidance on whether to create a table/diagram vs. text, which improved UX

**b. Judgment and verification**

**One example of rejecting an AI suggestion:**

Early on, the AI suggested using **optimal bin-packing** to maximize tasks scheduled per day. I recognized this would violate a core design principle: users who select "sort by priority" expect high-priority tasks to go first, not to be demoted for better packing. I pushed back and explained the greedy algorithm was better despite fitting fewer tasks in some cases.

**How I verified it:**
- Tested both approaches mentally with example scenarios (e.g., "90 minutes, three 30-minute tasks")
- Verified the greedy choice was documented in reflection.md with clear reasoning
- Wrote tests that proved high-priority tasks are always scheduled before lower-priority ones

**c. Using separate chat sessions for organization**

I used roughly 3-4 focused chat sessions, each for a phase:
1. **Design & System Architecture** — Initial discussions about UML, tradeoffs, class structure
2. **Implementation & Testing** — Building the core logic, writing and debugging tests
3. **UI & Documentation** — Streamlit app, README, demo walkthrough
4. **Final Polish** — Fixing app features, adding tables, updating UML and reflection

**Why this helped:**
- **Clear scope per session** — Each session had one goal, so prompts stayed focused and context didn't bloat
- **Fresh perspective** — Starting a new session meant AI wasn't constrained by earlier decisions; it could question and improve
- **Easier to debug** — When something broke in session 2, I didn't have to scroll past 50 UI discussion messages to find the relevant code
- **Deliberate transitions** — Moving to a new session forced me to write a summary of what was done, which caught gaps (e.g., "we never added recurrence to the app")

This phase-based approach kept the work organized and made handoffs clean—I could say "here's what we built last session; now let's add X" instead of relying on the AI to remember everything.

---

## 4. Testing and Verification

**a. What you tested**

We implemented 26 comprehensive tests covering:

- **Recurrence logic**: Daily/weekly tasks auto-create next occurrences with correct due dates; "once" tasks don't.
- **Sorting correctness**: Priority, duration, and pet-based sorts all return tasks in the expected order.
- **Task selection**: Greedy algorithm fits high-priority tasks first; overflow tasks are skipped correctly.
- **Conflict detection**: Overlapping fixed-time tasks are flagged with human-readable warnings.
- **Edge cases**: Zero available time, empty pets, multiple availability windows, non-overlapping schedules.

These tests were critical because they verify the core business logic that users depend on: whether the scheduler actually respects their preferences and constraints.

**b. Confidence**

**★★★★★ (5/5 stars)** — The system is reliable for basic pet scheduling workflows.

All 26 tests pass consistently. The scheduler correctly handles priority ordering, recurring task creation, and conflict detection. Edge cases (zero time, empty pets) are handled gracefully without crashes.

If we had more time, we'd test:
- Large task lists (50+ tasks) to verify performance
- Complex recurring patterns (bi-weekly, monthly)
- Tasks spanning multiple days
- Availability windows with minute-level precision

---

## 5. Reflection

**a. What went well**

The UML → implementation → testing workflow was effective. Starting with a clear design phase meant the code implementation was straightforward, and our comprehensive test suite (26 tests) caught edge cases before they became bugs. The Streamlit UI integration also came together smoothly once the backend logic was solid—the separation of concerns (system logic vs. UI) made both easier to reason about.

**b. What you would improve**

I'd refactor the `Scheduler` class—it's grown large with many methods (20+). Breaking it into smaller, focused classes (e.g., `TaskSorter`, `ConflictValidator`, `ScheduleBuilder`) would improve readability and testability. I'd also add support for task dependencies (e.g., "can't feed the dog before walking the dog") and recurring patterns beyond daily/weekly.

**c. Key takeaway**

**Being the lead architect with AI:** 

The most important lesson was that AI tools are powerful *collaborators*, not autonomous developers. My role was to:

- **Set the vision** — Define the system requirements and constraints upfront (greedy selection, three sorting strategies, recurring tasks)
- **Make judgment calls** — When AI suggested optimal bin-packing, I recognized it violated user expectations about priority ordering and chose greedy selection instead
- **Verify and validate** — I tested all AI-generated code, didn't blindly accept suggestions, and caught issues (like the initial test failure with assert 0 > 0)
- **Iterate intentionally** — I directed the AI to add features incrementally (recurring tasks, conflict detection, availability windows) rather than asking for everything at once

The AI excelled at *implementing* decisions I made, writing tests, and refactoring code—but it couldn't have designed the system without my direction. The best collaboration happened when I understood the problem deeply enough to steer the AI toward the right solution, rather than accepting the first suggestion or over-explaining every detail.

This project taught me that "lead architect with AI" means staying in the decision-making loop: own the design, leverage the AI for execution, and always verify before committing.
