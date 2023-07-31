from abc import ABC, abstractmethod


class OptionsPresenter(ABC):
    """
    This class defines the interface for presenting
    and communicating changes made to options in a
    system to various output channels. Output presentation
    is buffered and flushed out only after all options
    have been processed, or an exception occurs.
    """

    @abstractmethod
    def flush(self) -> None:
        """
        Flushes out all buffered output to the implemented
        output channel.
        """
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def unset(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, key: str, db_value: str, value: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def channel_update(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def drift(self, key: str, db_value: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def error(self, key: str, not_writable_reason: str) -> None:
        raise NotImplementedError
