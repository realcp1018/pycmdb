# coding=utf-8
"""
# @File       : codegen.py
# @Time       : 2024/6/14 15:32
# @Author     : forevermessi@foxmail.com
# @Description: parse new.model, get create table sql and orm model code
"""
import os
import re
import pymysql
import argparse
from typing import List

# database config
PYCMDB_CONFIG = {
    'host': os.getenv('PYCMDB_HOST', default="127.0.0.1"),
    'port': os.getenv('PYCMDB_PORT', default=3306),
    'user': os.getenv('PYCMDB_USER', default="cmdb_user"),
    'password': os.getenv('PYCMDB_PASSWORD', default="cmdb_password"),
    'database': os.getenv('PYCMDB_DATABASE', default="cmdb")
}
ALL_MODEL_FILE = "README.md"
NEW_MODEL_FILE = "new.model"


def arg_parse():
    parser = argparse.ArgumentParser(description="parse new.model to get create table sql and orm model code")
    parser.add_argument("--run", action="store_true", required=False, dest="run",
                        help="if specified, execute the sql in database and write the orm model code to model dir")
    return parser.parse_args()


class TypeMapping:
    Model_DB_TYPE_MAPPING = {"String": "VARCHAR(255)",
                             "Integer": "INT",
                             "BigInteger": "BIGINT",
                             "Float": "FLOAT",
                             "Boolean": "TINYINT(1)",
                             "DateTime": "DATETIME"}
    Model_PY_TYPE_MAPPING = {"String": "str",
                             "Integer": "int",
                             "BigInteger": "int",
                             "Float": "float",
                             "Boolean": "bool",
                             "DateTime": "datetime"}


class RegexPattern:
    MODEL_PATTERN = re.compile(r'(^\s*model\s+)'    # model keyword
                               r'([A-Z]\w*)'  # model name
                               r'(@tablename\("([a-z]\w*)"\))?'  # table name, optional
                               r'(\s+inherit\s+CI\s*{\s*)'   # inherit keyword
                               r'([^}]+)'  # fields part, see FIELD_PATTERN
                               r'}\s*',
                               flags=re.MULTILINE)
    FIELD_PATTERN = re.compile(r'^\s*([a-z]\w*)'  # field name
                               r'\s+([A-Z]\w*|\[[A-Z]\w*])'  # field type, scalar or reference
                               r'(\(\d+\))?'  # String length, optional
                               r'(!?)'  # nullable, where ! means not null
                               r'\s*(@uniq|@index)?'  # uniq index or normal index, optional
                               r'\s*(@default\("?([\w/]+)"?\))?'  # default value, optional
                               r'\s*("([^"]+)")?\s*$',  # comment, optional
                               flags=re.MULTILINE)


class Field(object):
    def __init__(self, name: str = None, origin_type: str = None, python_type: str = None, mysql_type: str = None,
                 mysql_type_len: str = None, is_ref: bool = False, nullable: bool = True, uniq: bool = False,
                 index: bool = False, default: str = None, comment: str = None):
        self.name = name
        self.origin_type = origin_type  # type defined in new.model
        self.python_type = python_type  # the corresponding python type, used in orm model
        self.mysql_type = mysql_type    # the corresponding mysql type, used in create table sql
        self.mysql_type_len = mysql_type_len  # the length of mysql varchar type, only for String
        self.is_ref = is_ref  # whether this field is a reference type ref to another model
        self.nullable = nullable
        self.uniq = uniq
        self.index = index  # mutually exclusive with uniq, because uniq mean an index too(unique index)
        self.default = default
        self.comment = comment

    @staticmethod
    def get_default_literal_by_scalar_type(default: str, origin_type: str) -> str:
        """
        get the default literal value that will be used in create sql by its scalar type
        a reference type can not define a default value
        """
        if origin_type in ["Integer", "BigInteger", "Float"]:
            return default
        if origin_type in ["String", "Datetime"]:
            return f'"{default}"'
        if origin_type in ["Boolean", "Bool"]:
            if default.lower() == 'true':
                return "True"
            elif default.lower() == 'false':
                return "False"
            else:
                raise Exception(f'Unsupported default value for bool type: {default}')
        raise Exception(f'Unsupported scalar type: {origin_type}')

    @classmethod
    def from_block(cls, block: str, current_models: List[str]) -> List['Field']:
        """
        parse the fields block from new.model to a list of Field instances
        """
        fields: List[Field] = list()
        field_matches = RegexPattern.FIELD_PATTERN.findall(block)
        for field_match in field_matches:
            python_type, mysql_type, uniq, index, is_ref = "", "", False, False, False
            name, origin_type, mysql_type_len, nullable, uniq_or_index, _, default, _, comment = field_match
            if origin_type in TypeMapping.Model_DB_TYPE_MAPPING.keys():
                mysql_type = TypeMapping.Model_DB_TYPE_MAPPING[origin_type]
                python_type = TypeMapping.Model_PY_TYPE_MAPPING[origin_type]
            # if not scalar type, then it is a reference type, filter it from current_models
            elif origin_type in current_models:
                is_ref = True
                mysql_type = "BIGINT"
                python_type = "int"
            else:
                raise Exception(f'Unsupported model type: {origin_type}')
            # parse default values, indexes, and comments
            if default:
                default = Field.get_default_literal_by_scalar_type(default, origin_type)
            if uniq_or_index == "@uniq":
                uniq = True
            if uniq_or_index == "@index":
                index = True
            cls_args = {
                'name': name,
                'origin_type': origin_type,
                "python_type": python_type,
                'mysql_type': mysql_type,
                'mysql_type_len': mysql_type_len.strip("(").strip(")") if mysql_type_len else None,
                'is_ref': is_ref,
                'nullable': False if nullable == "!" else True,
                'uniq': uniq,
                'index': index,
                'default': default,
                'comment': comment,
            }
            # print(cls_args)
            fields.append(cls(**cls_args))
        # check if the field count matches the actual field count in the block
        field_count = 0
        for line in block.split("\n"):
            field_count += 1 if line.strip() else 0
        if len(fields) == field_count:
            return fields
        else:
            print(f"model SDL parse failed, these fields are ok: {[f.name for f in fields]}, please check SDL syntax "
                  f"error for the rest {field_count - len(fields)} fields!")
            exit(1)

    def __str__(self):
        return str(self.__dict__)


class Model(object):
    def __init__(self, name=None, table_name=None, fields: List["Field"] = None):
        self.name = name
        self.table_name = table_name
        self.fields = fields

    @classmethod
    def from_all_model_file(cls) -> List['Model']:
        """
        get current models from ALL_MODEL_FILE, we only need a model name list so it will skip fields parsing
        """
        with open(ALL_MODEL_FILE, encoding="utf8") as f:
            schemas = f.read()
        models_matches = RegexPattern.MODEL_PATTERN.findall(schemas)
        models: List[Model] = list()
        for model_match in models_matches:
            _, name, _, table_name, _, fields_block = model_match
            cls_args = {
                'name': name,
                'table_name': table_name,
                'fields': "",
            }
            models.append(cls(**cls_args))
        return models

    @classmethod
    def from_new_model_file(cls, current_models: List[str]) -> List['Model']:
        """
        get model instances from NEW_MODEL_FILE
        """
        with open(NEW_MODEL_FILE, encoding="utf8") as f:
            schemas = f.read()
        models_matches = RegexPattern.MODEL_PATTERN.findall(schemas)
        models: List[Model] = list()
        for model_match in models_matches:
            _, name, _, table_name, _, fields_block = model_match
            cls_args = {
                'name': name,
                'table_name': table_name,
                'fields': Field.from_block(fields_block, current_models),
            }
            models.append(cls(**cls_args))
        return models

    def to_sql(self, run: bool):
        """
        generate mysql create table sql and meta_model/meta_relation insert sql
        if run, execute sqls in database
        """
        create_sql = (f"CREATE TABLE `{self.table_name}` (\n"
                      f"  `id` BIGINT AUTO_INCREMENT PRIMARY KEY,\n"
                      f"  `name` VARCHAR(255) NOT NULL,\n"
                      f"  `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,\n"
                      f"  `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,\n"
                      f"  `status` VARCHAR(10) NOT NULL DEFAULT 'online' "
                      f"COMMENT 'online, offline, inventory, unknown; default: online',\n"
                      f"  `notes` VARCHAR(255),\n")
        # meta_model/meta_relation are tables to store model metadata and relations metadata
        meta_model_sql = (f"INSERT INTO `meta_model`(model_name, table_name) "
                          f"VALUES ('{self.name}', '{self.table_name}');\n")
        meta_relation_sql = f"INSERT INTO `meta_relation`(model_name, table_name, column_name, ref_model) VALUES\n"
        for field in self.fields:
            if field.mysql_type_len:
                create_sql += "  `{0}` {1}".format(field.name,
                                                   field.mysql_type.replace("255", field.mysql_type_len))
            else:
                create_sql += "  `{0}` {1}".format(field.name, field.mysql_type)
            if not field.nullable:
                create_sql += " NOT NULL"
            if field.default:
                create_sql += f" DEFAULT {field.default}"
            if field.comment:
                create_sql += f" COMMENT '{field.comment}',\n"
        create_sql += (f"  UNIQUE KEY `uniq_name` (`name`),\n"
                       f"  KEY `idx_create_time` (`create_time`),\n"
                       f"  KEY `idx_update_time` (`update_time`),\n")
        for field in self.fields:
            if field.uniq:
                create_sql += f"  UNIQUE KEY `uniq_{field.name}` (`{field.name}`),\n"
            if field.index:
                create_sql += f"  INDEX `idx_{field.name}` (`{field.name}`),\n"
        create_sql = create_sql.strip(",\n") + "\n) ENGINE=InnoDB;"
        for field in self.fields:
            if field.is_ref:
                meta_relation_sql += f"('{self.name}','{self.table_name}','{field.name}','{field.origin_type}'),\n"
        meta_relation_sql = meta_relation_sql.strip(",\n") + ";\n"
        if run:
            conn = pymysql.connect(**PYCMDB_CONFIG)
            try:
                with conn.cursor() as cursor:
                    cursor.execute(create_sql)
                    cursor.execute(meta_model_sql)
                    cursor.execute(meta_relation_sql)
                    conn.commit()
                    print(f"Table {self.table_name} created successfully!")
            except pymysql.err.OperationalError as e:
                if e.args[0] == 1050:
                    print(e.args[1])
                    return
                else:
                    raise e
            except Exception as e:
                raise e
            finally:
                conn.close()
        else:
            print("################### Table create SQL:")
            print(create_sql)
            print("################### Model meta SQL:")
            print(meta_model_sql)
            print("################### Relation meta SQL:")
            print(meta_relation_sql)

    def to_orm_model(self, run: bool):
        """
        generate orm model code for this model, if run, write to model dir
        """
        code = "# coding=utf-8\n"
        code += ("from sqlalchemy import Column, String, Integer, BigInteger, Float, Boolean, DateTime\n"
                 "from .base import CI\n")
        code += f"class {self.name}(CI):\n"
        code += f"    __tablename__ = '{self.table_name}'\n\n"
        for field in self.fields:
            code += f"    {field.name} = Column("
            if field.is_ref:
                code += "BigInteger"
            else:
                code += f"{field.origin_type}"
            code += f"({field.mysql_type_len})" if field.origin_type == "String" and field.mysql_type_len else ""
            if not field.nullable:
                code += f", nullable=False"
            if field.uniq:
                code += f", unique=True"
            if field.index:
                code += f", index=True"
            if field.default:
                code += f", default={field.default}"
            if field.comment:
                code += f", comment=\"{field.comment}\""
            code += ")\n"
        if run:
            with open(f"../model/{self.name.lower()}.py", "w+", encoding="utf8") as f:
                f.write(code)
            with open(f"../model/__init__.py", "a+") as f:
                import_code = f"from .{self.name.lower()} import {self.name}"
                imported = [line.strip() for line in f.readlines()]
                if import_code not in imported:
                    f.write(import_code)
                    f.write("\n")
            print(f"Model {self.name} generated successfully!")
        else:
            print(code)


if __name__ == '__main__':
    args = arg_parse()
    run: bool = args.run
    current_models = [m.name for m in Model.from_all_model_file()]
    new_models = Model.from_new_model_file(current_models)
    for new_model in new_models:
        new_model.to_sql(run)
        new_model.to_orm_model(run)