from abc import ABC, abstractmethod


class BaseTableFormat(object):
    def __init__(self) -> None:
        pass

    def load_table(self, *args, **kwargs):
        pass

    @abstractmethod
    def table_version(self, *args, **kwargs):
        pass

    @abstractmethod
    def metadata(self, *args, **kwargs):
        pass

    @abstractmethod
    def files(self, *args, **kwargs):
        pass
