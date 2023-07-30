import os.path
import re


def string_to_snake_case(s):
    # https://stackoverflow.com/a/1176023
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()


class SchemaField:
    def __init__(self, name, type):
        self.name = name
        self.type = type


class SchemaClass:
    def __init__(self, name: str, fields: list[SchemaField]):
        self.name = name
        self.type = string_to_snake_case(name)
        self.fields = fields


class SchemaGenerator:
    lang: str

    def __init__(self, classes: list[SchemaClass], base_path: str):
        self.classes = classes.copy()
        self.base_path = os.path.join(base_path, self.lang)

    def prepare(self):
        raise NotImplementedError()

    def generate(self):
        raise NotImplementedError()
