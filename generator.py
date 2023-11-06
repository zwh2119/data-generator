from abc import ABC, abstractclassmethod, abstractstaticmethod, abstractmethod


class Generator(ABC):
    @abstractclassmethod
    def generator_type(cls) -> str:
        pass

    @abstractclassmethod
    def generator_description(cls) -> str:
        pass

    @abstractmethod
    def __init__(self, data_source: str, generator_id: int,
                 priority: int, task_dag: list) -> None:
        self.data_source = data_source
        self.generator_id = generator_id
        self.priority = priority
        self.task_dag = task_dag

    '''Should be implemented as a while loop that yields tasks'''

    @abstractmethod
    def run(self):
        pass
