import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


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
