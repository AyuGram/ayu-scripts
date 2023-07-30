import json
import os.path
import shutil

from generators import *


def main():
    with open('schema.json', 'r') as f:
        data = json.load(f)

    classes = []

    for item in data:
        name = item['name']
        args_fields = []

        for arg_name, arg_type in item['args'].items():
            args_fields.append(SchemaField(arg_name, arg_type))

        classes.append(SchemaClass(name, args_fields))

    base_path = os.path.abspath('./out/')

    if os.path.exists(base_path):
        shutil.rmtree(base_path)

    generators = [
        CSharpGenerator(classes, base_path),
        JavaGenerator(classes, base_path),
    ]

    for generator in generators:
        os.makedirs(generator.base_path, exist_ok=True)
        generator.prepare()

    for generator in generators:
        generator.generate()


if __name__ == '__main__':
    main()
