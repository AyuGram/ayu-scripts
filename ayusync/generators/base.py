import os.path
import re
from dataclasses import dataclass


def string_to_snake_case(s):
    # https://stackoverflow.com/a/1176023
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()


@dataclass()
class Field:
    def __init__(self, name, type):
        self.name = name
        self.type = type


@dataclass()
class SchemaClass:
    def __init__(self, name: str, fields: list[Field]):
        self.name = name
        self.type = string_to_snake_case(name)
        self.fields = fields


@dataclass()
class Entity:
    def __init__(self, name: str, fields: list[Field], is_abstract: bool, derives: str | None):
        self.name = name
        self.fields = fields
        self.is_abstract = is_abstract
        self.derives = derives


class ModelGenerator:
    lang: str

    def __init__(self, classes: list[SchemaClass], entities: list[Entity], base_path: str):
        self.classes = classes.copy()
        self.entities = entities.copy()
        self.base_path = os.path.join(base_path, self.lang)

    def prepare(self):
        raise NotImplementedError()

    def generate_schema(self):
        raise NotImplementedError()

    def generate_entities(self):
        raise NotImplementedError()
