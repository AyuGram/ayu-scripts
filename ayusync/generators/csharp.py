import os

from ayusync.generators import SchemaGenerator

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

TYPE_MAP = {}


class CSharpGenerator(SchemaGenerator):
    lang = 'csharp'

    def prepare(self):
        with open(os.path.join(self.base_path, 'SyncEvent.cs'), 'w', encoding='utf-8') as f:
            f.write(BASE_CLASS)

    def generate(self):
        for base_class in self.classes:
            args_str = ''

            for arg in base_class.fields:
                mapped_type = TYPE_MAP.get(arg.type, arg.type)

                if mapped_type.endswith('[]'):
                    stripped = arg.type[:-2]
                    mapped_type = f'List<{TYPE_MAP.get(stripped, stripped)}>'

                args_str += '        public ' + mapped_type + ' ' + arg.name + ';\n'

            args_str = args_str.rstrip('\n')

            res = CLASS_TEMPLATE % (
                base_class.name,
                base_class.name,
                base_class.type,
                base_class.name,
                args_str
            )

            with open(os.path.join(self.base_path, base_class.name + '.cs'), 'w', encoding='utf-8') as f:
                f.write(res)
