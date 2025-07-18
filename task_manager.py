class Task:
    def __init__(self, title, completed=False):
        self.title = title
        self.completed = completed

    def complete(self):
        self.completed = True

class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task: Task):
        if not isinstance(task, Task):
            raise ValueError("Only Task instances can be added")
        self.tasks.append(task)

    def get_completed_tasks(self):
        return [t for t in self.tasks if t.completed]

    def get_incomplete_tasks(self):
        return [t for t in self.tasks if not t.completed]

    def clear_tasks(self):
        self.tasks.clear()

    def remove_task(self, title: str):
        self.tasks = [t for t in self.tasks if t.title != title]

    def find_task(self, title: str) -> Task:
        for task in self.tasks:
            if task.title == title:
                return task
        raise ValueError("Task not found")
