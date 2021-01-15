from abc import ABC, abstractmethod
from typing import Any


class ICommand(ABC):
    @abstractmethod
    def execute(self, check: bool = True) -> Any:
        pass


class IDatabase(ABC):
    pass


class IGroup(ABC):
    @abstractmethod
    def get_path(self) -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def remove(self):
        pass


class IEntry(ABC):
    pass
