import os.path
from copy import copy
from io import TextIOWrapper

from ayusync.generators import ModelGenerator, SchemaClass, Entity, Field

GIGA_BASED = '''// This is the source code of AyuGram for Desktop.
//
// We do not and cannot prevent the use of our code,
// but be respectful and credit the original author.
//
// Copyright @Radolyn, 2023
#pragma once

#include <string>

#define ID long long
'''

ENTITY_TEMPLATE = '''
%sclass %s
{
%s
};
'''

STORAGE_TEMPLATE = '''// This is the source code of AyuGram for Desktop.
//
// We do not and cannot prevent the use of our code,
// but be respectful and credit the original author.
//
// Copyright @Radolyn, 2023
#pragma once

#include "ayu_database.h"

#include "entities.h"
#include "ayu/libs/sqlite/sqlite_orm.h"

using namespace sqlite_orm;
'''

MODELS_BASED = '''// This is the source code of AyuGram for Desktop.
//
// We do not and cannot prevent the use of our code,
// but be respectful and credit the original author.
//
// Copyright @Radolyn, 2023
#pragma once

#include <string>
#include <vector>

#include "ayu/libs/json.hpp"
#include "ayu/database/entities.h"

using json = nlohmann::json;

class SyncEvent
{
public:
	std::string type = "sync_unspecified";
	ID userId = 0;
};

'''

CLASS_TEMPLATE = '''class %s : public SyncEvent
{
public:
	explicit %s()
	{
		type = "%s";
	}

	class %sArgs
	{
%s
	};

	%sArgs args{};
};

'''

DUMMY_FIELDS = '''	public:
		short dummy; // required to be JSON serializable'''

JSON_BASED_START = '''NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(SyncEvent, type, userId)
'''
JSON_BASED_TEMPLATE = 'NLOHMANN_DEFINE_TYPE_NON_INTRUSIVE(%s, %s)'

TYPE_MAP = {
    'string': 'std::string',
    'long': 'ID',
    'byte[]': 'std::vector<char>',
    'SyncEvent[]': 'std::vector<json>',
    # temp solution
    'EditedMessage': 'json',
    'DeletedMessage': 'json'
}


def generate_fields(fields: list[Field], ident=0) -> str:
    ident_str = '	' * ident

    res = ''
    for field in fields:
        mapped_type = TYPE_MAP.get(field.type, field.type)
        res += ident_str + '	' + mapped_type + ' ' + field.name + ';\n'

    res = res.rstrip('\n')

    if res and ident == 0:
        res = ident_str + 'public:\n' + '	ID fakeId;\n' + res
    elif res and ident == 1:
        res = ident_str + 'public:\n' + res

    return res


class CppGenerator(ModelGenerator):
    lang = 'cpp'

    def __init__(self, classes: list[SchemaClass], entities: list[Entity], base_path: str):
        super().__init__(classes, entities, base_path)

        self.fe: TextIOWrapper = None  # noqa
        self.fade: TextIOWrapper = None  # noqa
        self.fm: TextIOWrapper = None  # noqa

    def prepare(self):
        self.fe = open(os.path.join(self.base_path, 'entities.h'), 'w', encoding='utf-8')
        self.fade = open(os.path.join(self.base_path, 'ayu_database_entities.h'), 'w', encoding='utf-8')
        self.fm = open(os.path.join(self.base_path, 'models.h'), 'w', encoding='utf-8')

        self.fe.write(GIGA_BASED)
        self.fm.write(MODELS_BASED)

    def generate_schema(self):
        json_conv = JSON_BASED_START

        for base_class in self.classes:
            fields_str = generate_fields(base_class.fields, 1)

            if not fields_str:
                fields_str = DUMMY_FIELDS

            res = CLASS_TEMPLATE % (
                base_class.name,
                base_class.name,
                base_class.type,
                base_class.name,
                fields_str,
                base_class.name
            )

            self.fm.write(res)

            s = ', '.join(field.name for field in base_class.fields)
            if not s:
                s = 'dummy'

            json_conv += JSON_BASED_TEMPLATE % (base_class.name + '::' + base_class.name + 'Args', s) + '\n'
            json_conv += JSON_BASED_TEMPLATE % (base_class.name, ', '.join(['type', 'userId', 'args'])) + '\n'

        self.fm.write(json_conv)

    def generate_entities(self):
        storage_str = 'auto storage = make_storage("ayugram.db",\n'

        for i, entity in enumerate(self.entities):
            if not entity.is_abstract:
                storage_str += '	make_table("' + entity.name + '",\n'

                fields = copy(entity.fields)
                if entity.derives:
                    fields = next(e for e in self.entities if e.name == entity.derives).fields + fields

                for field in fields:
                    storage_str += '		make_column("' + field.name + '", &' + entity.name + '::' + field.name + '),\n'
                storage_str = storage_str.rstrip(',\n') + '\n	),\n'

            pre_str = ''
            name_str = None
            if entity.is_abstract:
                # не осилил абстрактные классы в плюсах
                name_str = entity.name
                pre_str = 'template <typename TableName>\n'
            elif entity.derives:
                # не осилил наследование в плюсах
                if not entity.fields:
                    self.fe.write(f'using {entity.name} = {entity.derives}<struct {entity.name}Tag>;')
                else:
                    raise Exception("Nested classes are not supported in C++")
            else:
                name_str = entity.name

            fields_str = generate_fields(entity.fields)

            if name_str:
                self.fe.write(ENTITY_TEMPLATE % (pre_str, name_str, fields_str))

            if i != len(self.entities) - 1:
                self.fe.write('\n')

        storage_str = storage_str.rstrip(',\n') + '\n);'

        self.fade.write(STORAGE_TEMPLATE + storage_str + '\n')
