import pytest
import task_manager


# Можно было создать файл с данными и перенести туда класс NotATask и переменные
# Класс используется для проверки добавления невалидных объектов в add_task()
class NotATask:
    def __init__(self):
        self.title = "Not a task"
        self.completed = False

    def complete(self):
        pass


@pytest.fixture
def empty_task_manager():
    manager = task_manager.TaskManager()
    assert manager.tasks == []
    return manager


@pytest.fixture
def create_basic_test_task():
    def create(title="Test task", completed=False):
        return task_manager.Task(title, completed)

    return create


NAMES_TO_CHECK_NAME_TEST_TASK = [
    "Test task ",
    " Test task",
    "test task",
    "Test  task",
    "TEST TASK"
]

TASK_OBJECTS = [
    123,
    None,
    3.14,
    ["task"],
    "str",
    " ",
    "",
    {"title": "abc"},
    True,
    ("tuple",),
    {"set_item"},
    "A" * 10000
]


class TestTask:
    def test_creating_default_task(self):
        default_task = task_manager.Task("Default task")
        assert default_task.completed is False

    # Было бы хорошо если были ограничения на название задачи
    @pytest.mark.parametrize("title", TASK_OBJECTS)
    def test_creation_task_with_different_titles(self, title):
        task = task_manager.Task(title)
        assert task.title == title

    def test_change_task_state(self, create_basic_test_task):
        task = create_basic_test_task()
        assert task.completed is False
        task.complete()
        assert task.completed is True
        task.complete()
        assert task.completed is True

    def test_complete_only_affects_target_task(self, create_basic_test_task):
        task1 = create_basic_test_task()
        task2 = create_basic_test_task()
        assert task1.completed is False
        assert task2.completed is False
        task1.complete()
        assert task1.completed is True
        assert task2.completed is False


class TestTaskManager:
    def test_add_valid_tasks(self, empty_task_manager, create_basic_test_task):
        task1 = create_basic_test_task("Test task1")
        empty_task_manager.add_task(task1)
        assert task1 in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 1
        task2 = create_basic_test_task("Test task2")
        empty_task_manager.add_task(task2)
        assert task2 in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 2

    # Было бы хорошо если была проверка на повторную задачу (с таким же именем) и ее нельзя было добавить
    def test_adding_one_task_twice(self, empty_task_manager, create_basic_test_task):
        task = create_basic_test_task()
        empty_task_manager.add_task(task)
        empty_task_manager.add_task(task)
        assert empty_task_manager.tasks.count(task) == 2
        assert empty_task_manager.tasks[0] is task
        assert empty_task_manager.tasks[1] is task

    @pytest.mark.parametrize("invalid_input", TASK_OBJECTS + [NotATask()])
    def test_add_invalid_task_types(self, empty_task_manager, invalid_input):
        with pytest.raises(ValueError, match="Only Task instances can be added"):
            empty_task_manager.add_task(invalid_input)
        assert invalid_input not in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 0

    def test_get_completed_tasks_one_task(self, empty_task_manager, create_basic_test_task):
        completed_task = create_basic_test_task("Done", completed=True)
        empty_task_manager.add_task(completed_task)
        assert len(empty_task_manager.tasks) == 1
        completed_tasks = empty_task_manager.get_completed_tasks()
        assert completed_task in completed_tasks
        assert completed_tasks == [completed_task]

    def test_get_incomplete_tasks_one_task(self, empty_task_manager, create_basic_test_task):
        incomplete_task = create_basic_test_task("Not done", completed=False)
        empty_task_manager.add_task(incomplete_task)
        assert len(empty_task_manager.tasks) == 1
        incomplete_tasks = empty_task_manager.get_incomplete_tasks()
        assert incomplete_task in incomplete_tasks
        assert incomplete_tasks == [incomplete_task]

    def test_get_completed_tasks_three_tasks(self, empty_task_manager, create_basic_test_task):
        completed_task1 = create_basic_test_task(completed=True)
        completed_task2 = create_basic_test_task(completed=True)
        incomplete_task = create_basic_test_task(completed=False)
        empty_task_manager.add_task(completed_task1)
        empty_task_manager.add_task(completed_task2)
        empty_task_manager.add_task(incomplete_task)
        assert len(empty_task_manager.tasks) == 3
        completed_tasks = empty_task_manager.get_completed_tasks()
        assert completed_task1 in completed_tasks
        assert completed_task2 in completed_tasks
        assert incomplete_task not in completed_tasks
        assert completed_tasks == [completed_task1, completed_task2]

    def test_get_incomplete_tasks_three_tasks(self, empty_task_manager, create_basic_test_task):
        completed_task = create_basic_test_task(completed=True)
        incomplete_task1 = create_basic_test_task(completed=False)
        incomplete_task2 = create_basic_test_task(completed=False)
        empty_task_manager.add_task(completed_task)
        empty_task_manager.add_task(incomplete_task1)
        empty_task_manager.add_task(incomplete_task2)
        assert len(empty_task_manager.tasks) == 3
        incomplete_tasks = empty_task_manager.get_incomplete_tasks()
        assert incomplete_task1 in incomplete_tasks
        assert incomplete_task2 in incomplete_tasks
        assert completed_task not in incomplete_tasks
        assert incomplete_tasks == [incomplete_task1, incomplete_task2]

    def test_get_completed_tasks_empty(self, empty_task_manager):
        completed_tasks = empty_task_manager.get_completed_tasks()
        assert completed_tasks == []

    def test_get_incomplete_tasks_empty(self, empty_task_manager):
        incomplete_tasks = empty_task_manager.get_incomplete_tasks()
        assert incomplete_tasks == []

    # clear_tasks удаляет все задачи, повторный вызов не вызывает ошибок (идемпотентность)
    def test_clear_tasks_with_one_task(self, empty_task_manager, create_basic_test_task):
        task = create_basic_test_task()
        empty_task_manager.add_task(task)
        assert task in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 1
        empty_task_manager.clear_tasks()
        assert task not in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 0
        empty_task_manager.clear_tasks()
        assert len(empty_task_manager.tasks) == 0

    # clear_tasks очищает список при трех задачах, две с одинаковыми названиями
    def test_clear_tasks_with_three_task(self, empty_task_manager, create_basic_test_task):
        task1 = create_basic_test_task("Test task1")
        empty_task_manager.add_task(task1)
        empty_task_manager.add_task(task1)
        task2 = create_basic_test_task("Test task2")
        empty_task_manager.add_task(task2)
        assert task1 in empty_task_manager.tasks
        assert task2 in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 3
        empty_task_manager.clear_tasks()
        assert task1 not in empty_task_manager.tasks
        assert task2 not in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 0

    def test_clear_tasks_on_empty_manager(self, empty_task_manager):
        assert empty_task_manager.tasks == []
        empty_task_manager.clear_tasks()
        assert empty_task_manager.tasks == []

    def test_remove_existing_task_with_one_task(self, empty_task_manager, create_basic_test_task):
        task = create_basic_test_task()
        empty_task_manager.add_task(task)
        assert task in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 1
        empty_task_manager.remove_task(task.title)
        assert task not in empty_task_manager.tasks
        assert empty_task_manager.tasks == []
        # Повторное удаление не вызывает ошибку и не меняет список
        empty_task_manager.remove_task(task.title)
        assert task not in empty_task_manager.tasks
        assert empty_task_manager.tasks == []

    def test_remove_existing_task_with_two_different_tasks(self, empty_task_manager, create_basic_test_task):
        task1 = create_basic_test_task("Test task1")
        empty_task_manager.add_task(task1)
        task2 = create_basic_test_task("Test task2")
        empty_task_manager.add_task(task2)
        assert task1 in empty_task_manager.tasks
        assert task2 in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 2
        empty_task_manager.remove_task(task1.title)
        assert task1 not in empty_task_manager.tasks
        assert task2 in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 1

    # Было бы хорошо если была проверка на повторную задачу (с таким же именем) и ее нельзя было добавить
    def test_remove_existing_task_with_two_identical_tasks(self, empty_task_manager, create_basic_test_task):
        task = create_basic_test_task()
        empty_task_manager.add_task(task)
        empty_task_manager.add_task(task)
        assert len(empty_task_manager.tasks) == 2
        empty_task_manager.remove_task(task.title)
        assert len(empty_task_manager.tasks) == 0

    def test_remove_task_on_empty_manager(self, empty_task_manager, create_basic_test_task):
        task = create_basic_test_task()
        empty_task_manager.remove_task(task.title)
        assert empty_task_manager.tasks == []

    @pytest.mark.parametrize("invalid_input", NAMES_TO_CHECK_NAME_TEST_TASK + TASK_OBJECTS)
    def test_remove_non_existing_task(self, empty_task_manager, create_basic_test_task, invalid_input):
        task = create_basic_test_task()
        empty_task_manager.remove_task(task.title)
        empty_task_manager.add_task(task)
        assert task in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 1
        empty_task_manager.remove_task(invalid_input)
        assert task in empty_task_manager.tasks
        assert len(empty_task_manager.tasks) == 1

    def test_find_existing_task_with_one_task(self, empty_task_manager, create_basic_test_task):
        task = create_basic_test_task()
        empty_task_manager.add_task(task)
        assert empty_task_manager.find_task(task.title) is task

    def test_find_existing_task_with_two_different_task(self, empty_task_manager, create_basic_test_task):
        task1 = create_basic_test_task("Test task1")
        task2 = create_basic_test_task("Test task2")
        empty_task_manager.add_task(task1)
        empty_task_manager.add_task(task2)
        assert empty_task_manager.find_task(task1.title) is task1
        assert empty_task_manager.find_task(task2.title) is task2

    def test_find_existing_task_with_two_identical_task(self, empty_task_manager, create_basic_test_task):
        task = create_basic_test_task()
        empty_task_manager.add_task(task)
        empty_task_manager.add_task(task)
        assert len(empty_task_manager.tasks) == 2
        assert empty_task_manager.find_task(task.title) is task

    def test_find_existing_task_on_empty_manager(self, empty_task_manager, create_basic_test_task):
        task = create_basic_test_task()
        assert empty_task_manager.tasks == []
        with pytest.raises(ValueError, match="Task not found"):
            empty_task_manager.find_task(task.title)

    # Поиск можно сделать более универсальным
    @pytest.mark.parametrize("invalid_input", NAMES_TO_CHECK_NAME_TEST_TASK + TASK_OBJECTS)
    def test_find_non_existing_task(self, empty_task_manager, create_basic_test_task, invalid_input):
        task = create_basic_test_task()
        empty_task_manager.add_task(task)
        with pytest.raises(ValueError, match="Task not found"):
            empty_task_manager.find_task(invalid_input)
