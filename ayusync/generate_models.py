import json
import os.path
import shutil

from generators import *


def main():
    with open('schema.json', 'r') as f:
        schema = json.load(f)

    classes = []

    for item in schema:
        name = item['name']
        args_fields = []

        for arg_name, arg_type in item['args'].items():
            args_fields.append(Field(arg_name, arg_type))

        classes.append(SchemaClass(name, args_fields))

    with open('entities.json', 'r') as f:
        entities_data = json.load(f)

    entities = []

    for item in entities_data:
        name = item['name']
        fields = []

        for field_name, field_type in item.get('fields', {}).items():
            fields.append(Field(field_name, field_type))

        entities.append(Entity(name, fields, item.get('abstract', False), item.get('derives')))

    base_path = os.path.abspath('./out/')

    if os.path.exists(base_path):
        shutil.rmtree(base_path)

    generators = [
        CSharpGenerator(classes, entities, base_path),
        JavaGenerator(classes, entities, base_path),
        CppGenerator(classes, entities, base_path),
    ]

    for generator in generators:
        os.makedirs(generator.base_path, exist_ok=True)
        generator.prepare()

    for generator in generators:
        generator.generate_schema()
        generator.generate_entities()


if __name__ == '__main__':
    main()
