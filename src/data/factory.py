from dataclasses import asdict, is_dataclass
from typing import Any, Callable

from .data_types import DTypes


class DataFactory:
    # A class that acts as a factory for creating and serializing data objects.

    _registry: dict[DTypes, type] = {}

    @classmethod
    def __init_subclass__(cls, /, dtype: DTypes|None, **kwargs):
        # A metaclass method called when a subclass is defined.
        # It registers the subclass in the _registry dictionary based on the dtype provided.

        super().__init_subclass__(**kwargs)
        if dtype:
            cls._registry[dtype] = cls

    def __new__(cls, dtype: DTypes = DTypes.GENERIC, **kwargs: dict[str, Any]):
        # A method that returns an instance of the appropriate subclass based on the dtype provided.

        subclass: type = cls._registry.get(dtype, DataFactory)
        return super().__new__(subclass)

    def __is_field(self, attr):
        # A method to check if the attribute should be considered as a field for serialization.

        return not any((
            attr.startswith("_"),  # Exclude private attributes (starting with '_').
            isinstance(getattr(self, attr), Callable),  # Exclude callable attributes (methods).
        ))

    def serialize(self, base_info: bool = False):
        # A method to serialize the data object into a dictionary.

        if not is_dataclass(self):
            return {attr: getattr(self, attr) for attr in dir(self) if self.__is_field(attr)}
            # Serialize non-dataclass objects by including only non-private, non-method attributes.

        data = asdict(self)
        # Convert the dataclass object to a dictionary.

        if not base_info:
            for key in ("id", "created_at", "updated_at"):
                data.pop(key)
                # If base_info is False, remove "id", "created_at", and "updated_at" fields from the dictionary.

        return data

    @staticmethod
    def load_many(data_list: list, dtype: DTypes = DTypes.GENERIC):
        # A static method to create and load multiple data objects from a list of dictionaries.

        return [DataFactory(dtype=dtype, **data) for data in data_list]
        # Create and load data objects using the provided dtype and data from the list.
