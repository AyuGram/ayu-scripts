import os.path

from ayusync.generators import ModelGenerator

BASE_CLASS = '''/*
 * This is the source code of AyuGram for Android.
 *
 * We do not and cannot prevent the use of our code,
 * but be respectful and credit the original author.
 *
 * Copyright @Radolyn, 2023
 */

package com.radolyn.ayugram.sync.models;

public interface SyncEvent {
    String type = "sync_unspecified";
    long userId = 0;
}
'''

CLASS_TEMPLATE = '''/*
 * This is the source code of AyuGram for Android.
 *
 * We do not and cannot prevent the use of our code,
 * but be respectful and credit the original author.
 *
 * Copyright @Radolyn, 2023
 */

package com.radolyn.ayugram.sync.models;
%s
public class %s implements SyncEvent {
    public String type = "%s";
    public long userId;
    public %s.%sArgs args = new %s.%sArgs();

    public static class %sArgs {
%s
    }
}
'''

ENTITY_TEMPLATE = '''/*
 * This is the source code of AyuGram for Android.
 *
 * We do not and cannot prevent the use of our code,
 * but be respectful and credit the original author.
 *
 * Copyright @Radolyn, 2023
 */

package com.radolyn.ayugram.database.entities;
%s
public %s {
%s
}
'''

TYPE_MAP = {
    'string': 'String',
    'bool': 'boolean',
    'long?': 'Long'
}


def generate_args_str(fields, map_to_list, ident):
    ident_str = ' ' * ident
    imports_str = ''
    args_str = ''

    for arg in fields:
        default_val = ''
        mapped_type = TYPE_MAP.get(arg.type, arg.type)

        if mapped_type.endswith('[]') and map_to_list:
            stripped = arg.type[:-2]
            mapped_type = f'ArrayList<{TYPE_MAP.get(stripped, stripped)}>'
            default_val = 'new ArrayList<>()'

            if 'import java.util.ArrayList' not in imports_str:
                imports_str += '\nimport java.util.ArrayList;\n'

        args_str += (ident_str + 'public ' + mapped_type + ' ' + arg.name +
                     (';\n' if not default_val else f' = {default_val};\n'))

    args_str = args_str.rstrip('\n')

    return imports_str, args_str


class JavaGenerator(ModelGenerator):
    lang = 'java'

    def prepare(self):
        with open(os.path.join(self.base_path, 'SyncEvent.java'), 'w', encoding='utf-8') as f:
            f.write(BASE_CLASS)

    def generate_schema(self):
        for base_class in self.classes:
            imports_str, args_str = generate_args_str(base_class.fields, True, ident=8)

            res = CLASS_TEMPLATE % (
                imports_str,
                base_class.name,
                base_class.type,
                base_class.name,
                base_class.name,
                base_class.name,
                base_class.name,
                base_class.name,
                args_str
            )

            with open(os.path.join(self.base_path, base_class.name + '.java'), 'w', encoding='utf-8') as f:
                f.write(res)

    def generate_entities(self):
        for entity in self.entities:
            pre_str = ''
            imports_str, args_str = generate_args_str(entity.fields, False, ident=4)

            if entity.is_abstract:
                name_str = 'abstract class ' + entity.name
            elif entity.derives:
                pre_str += '\n@Entity()'
                name_str = 'class ' + entity.name + ' extends ' + entity.derives
                args_str = '    @PrimaryKey(autoGenerate = true)\n    public long fakeId;\n' + args_str
                imports_str += '\nimport androidx.room.Entity;\nimport androidx.room.PrimaryKey;\n'
            else:
                pre_str += '\n@Entity()'
                name_str = 'class ' + entity.name
                args_str = '    @PrimaryKey(autoGenerate = true)\n    public long fakeId;\n' + args_str
                imports_str += '\nimport androidx.room.Entity;\nimport androidx.room.PrimaryKey;\n'

            pre_str = imports_str + pre_str
            args_str = args_str.rstrip(' \n\r\t')

            res = ENTITY_TEMPLATE % (
                pre_str,
                name_str,
                args_str
            )

            with open(os.path.join(self.base_path, entity.name + '.java'), 'w', encoding='utf-8') as f:
                f.write(res)
