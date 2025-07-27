Below is a complete Python script that demonstrates advanced Python features while adhering to the requirements. The example simulates a task management system where users can create, list, and complete tasks. It incorporates all the requested features.

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Generator, AsyncGenerator
import asyncio
import os


# Custom exception for task-related errors
class TaskError(Exception):
    """Custom exception for errors related to tasks."""
    pass


# Base class for a Task
@dataclass
class Task:
    """Represents a generic task."""
    name: str
    completed: bool = False

    def complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def __str__(self) -> str:
        return f"{'[x]' if self.completed else '[ ]'} {self.name}"


# Subclass for a TimedTask with polymorphism
@dataclass
class TimedTask(Task):
    """Represents a task with a time limit."""
    duration: int = 0  # Duration in minutes

    def __str__(self) -> str:
        return f"{super().__str__()} (Duration: {self.duration} min)"


# Decorator to log function calls
def log_execution(func):
    """Decorator to log the execution of a function."""
    async def wrapper(*args, **kwargs):
        print(f"Executing {func.__name__}...")
        result = await func(*args, **kwargs)
        print(f"Finished {func.__name__}.")
        return result
    return wrapper


# Context manager for file operations
class FileManager:
    """Context manager for safely handling file operations."""
    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode, encoding="utf-8")
        return self.file

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file:
            self.file.close()


# TaskManager class to manage a list of tasks
class TaskManager:
    """Manages a collection of tasks."""
    def __init__(self):
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a new task to the task list."""
        self.tasks.append(task)

    def list_tasks(self) -> str:
        """Return a string representation of all tasks."""
        if not self.tasks:
            return "No tasks available."
        return "\n".join(str(task) for task in self.tasks)

    def get_completed_tasks(self) -> Generator[Task, None, None]:
        """Yield completed tasks."""
        return (task for task in self.tasks if task.completed)

    def save_tasks_to_file(self, filename: str) -> None:
        """Save all tasks to a file."""
        with FileManager(filename, "w") as file:
            for task in self.tasks:
                file.write(str(task) + "\n")

    def load_tasks_from_file(self, filename: str) -> None:
        """Load tasks from a file."""
        if not os.path.exists(filename):
            raise TaskError(f"File '{filename}' does not exist.")
        with FileManager(filename, "r") as file:
            for line in file:
                name, completed = line.strip().split(" | ")
                self.tasks.append(Task(name=name, completed=completed == "True"))


# Asynchronous function to simulate task processing
@log_execution
async def process_tasks(task_manager: TaskManager) -> None:
    """Simulate processing tasks asynchronously."""
    for task in task_manager.tasks:
        print(f"Processing task: {task.name}")
        await asyncio.sleep(1)  # Simulate time delay
        task.complete()


# Example usage
async def main():
    """Main function to demonstrate the task management system."""
    task_manager = TaskManager()

    # Add tasks
    task_manager.add_task(Task("Write documentation"))
    task_manager.add_task(TimedTask("Prepare presentation", duration=30))
    task_manager.add_task(Task("Review pull requests"))

    # List tasks
    print("Tasks:")
    print(task_manager.list_tasks())

    # Process tasks asynchronously
    await process_tasks(task_manager)

    # List completed tasks using a generator
    print("\nCompleted tasks:")
    for completed_task in task_manager.get_completed_tasks():
        print(completed_task)

    # Save tasks to a file
    task_file = "tasks.txt"
    task_manager.save_tasks_to_file(task_file)
    print(f"\nTasks saved to {task_file}.")

    # Load tasks from a file
    print("\nReloading tasks from file:")
    new_task_manager = TaskManager()
    new_task_manager.load_tasks_from_file(task_file)
    print(new_task_manager.list_tasks())


# Run the example
if __name__ == "__main__":
    asyncio.run(main())
```

### Features Demonstrated:
1. **Class with inheritance and polymorphism**: `Task` is the base class, and `TimedTask` inherits from it with additional functionality.
2. **Decorators**: `log_execution` logs the execution of an asynchronous function.
3. **Context Managers**: `FileManager` safely handles file operations.
4. **Async/await patterns**: `process_tasks` simulates asynchronous task processing.
5. **Type hints and dataclasses**: Used throughout the code for better clarity and type safety.
6. **Error handling with custom exceptions**: `TaskError` is used for file-related errors.
7. **File I/O operations**: Tasks are saved to and loaded from a file.
8. **List comprehensions and generator expressions**: Used in `list_tasks` and `get_completed_tasks`.

### Example Usage:
Run the script to see how tasks are added, processed asynchronously, saved to a file, and reloaded. This code is practical for managing tasks in a small project or as a learning tool for advanced Python features.