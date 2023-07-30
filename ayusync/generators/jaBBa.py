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
    public %s.%sArgs args;

    public static class %sArgs {
%s
    }
}
'''

TYPE_MAP = {}


class JavaGenerator(ModelGenerator):
    lang = 'java'

    def prepare(self):
        with open(os.path.join(self.base_path, 'SyncEvent.java'), 'w', encoding='utf-8') as f:
            f.write(BASE_CLASS)

    def generate_schema(self):
        for base_class in self.classes:
            imports_str = ''
            args_str = ''

            for arg in base_class.fields:
                default_val = ''
                mapped_type = TYPE_MAP.get(arg.type, arg.type)

                if mapped_type.endswith('[]'):
                    stripped = arg.type[:-2]
                    mapped_type = f'ArrayList<{TYPE_MAP.get(stripped, stripped)}>'
                    default_val = 'new ArrayList<>()'
                    imports_str += '\nimport java.util.ArrayList;\n'

                args_str += ('        public ' + mapped_type + ' ' + arg.name +
                             (';\n' if not default_val else f' = {default_val};\n'))

            args_str = args_str.rstrip('\n')

            res = CLASS_TEMPLATE % (
                imports_str,
                base_class.name,
                base_class.type,
                base_class.name,
                base_class.name,
                base_class.name,
                args_str
            )

            with open(os.path.join(self.base_path, base_class.name + '.java'), 'w', encoding='utf-8') as f:
                f.write(res)

    def generate_entities(self):
        print('Java entity generator not implemented.')
