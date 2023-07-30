import os

from ayusync.generators import ModelGenerator

BASE_CLASS = '''namespace AyuGram.Sync.Core.Models;

public abstract class SyncEvent
{
    public virtual string Type { get; protected set; } = "sync_unspecified";
    public long UserId { get; set; }
}
'''

CLASS_TEMPLATE = '''namespace AyuGram.Sync.Core.Models;

public sealed class %s : SyncEvent
{
    public readonly %sArgs Args = new();
    public override string Type { get; protected set; } = "%s";

    public sealed class %sArgs
    {
%s
    }
}
'''

ENTITY_TEMPLATE = '''namespace AyuGram.Sync.Core.Models;

public %s
{
%s
}
'''

TYPE_MAP = {}


def camel_case(s):
    return s[0].upper() + s[1:]


def generate_args_str(fields, map_to_list, ident):
    ident_str = ' ' * ident
    args_str = ''

    for arg in fields:
        mapped_type = TYPE_MAP.get(arg.type, arg.type)

        if mapped_type.endswith('[]') and map_to_list:
            stripped = arg.type[:-2]
            mapped_type = f'List<{TYPE_MAP.get(stripped, stripped)}>'

        args_str += ident_str + 'public ' + mapped_type + ' ' + camel_case(arg.name) + ';\n'

    args_str = args_str.rstrip('\n')
    return args_str


class CSharpGenerator(ModelGenerator):
    lang = 'csharp'

    def prepare(self):
        with open(os.path.join(self.base_path, 'SyncEvent.cs'), 'w', encoding='utf-8') as f:
            f.write(BASE_CLASS)

    def generate_schema(self):
        for base_class in self.classes:
            args_str = generate_args_str(base_class.fields, True, ident=8)

            res = CLASS_TEMPLATE % (
                base_class.name,
                base_class.name,
                base_class.type,
                base_class.name,
                args_str
            )

            with open(os.path.join(self.base_path, base_class.name + '.cs'), 'w', encoding='utf-8') as f:
                f.write(res)

    def generate_entities(self):
        for entity in self.entities:
            args_str = generate_args_str(entity.fields, False, ident=4)

            name_str = ''
            if entity.is_abstract:
                name_str = 'abstract class ' + entity.name
            elif entity.derives:
                name_str = 'sealed class ' + entity.name + ' : ' + entity.derives
            else:
                name_str = 'sealed class ' + entity.name

            res = ENTITY_TEMPLATE % (
                name_str,
                args_str
            )

            with open(os.path.join(self.base_path, entity.name + '.cs'), 'w', encoding='utf-8') as f:
                f.write(res)
