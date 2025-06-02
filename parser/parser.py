# coding=utf-8
"""
# @File       : create.py
# @Time       : 2024/7/30 18:32
# @Author     : forevermessi@foxmail.com
# @Description: convert query request to orm query code
"""
from typing import List, Dict
import re

MODEL_PATTERN = re.compile(r"\s*(\w+)\s*"  # model alias    
                           r":\s*"
                           r"(\w+)"  # model name 
                           r"(?:\((.*?)=(.*?)\))?(?:,\s*|$)")  # model condition


class Model(object):
    def __init__(self, name, alias, filter_col_name, filter_col_value):
        self.name = name
        self.alias = alias
        self.filter_col_name = filter_col_name
        self.filter_col_value = filter_col_value


class Relation(object):
    def __init__(self, from_model: str, from_col_name: str, to_model: str):
        self.from_model = from_model
        self.from_col_name = from_col_name
        self.to_model = to_model


class Request(object):
    def __init__(self, models: List[Model], relations: List[Relation], fields: List[str], limit: str = None):
        self.models: List[Model] = models
        self.relations: List[Relation] = relations
        self.fields: List[str] = fields
        # paging: (offset,page size)
        self.limit = limit

    @classmethod
    def from_request_body(cls, request_body: Dict[str, str]):
        # models
        try:
            models: List[Model] = []
            matches = MODEL_PATTERN.findall(request_body["Models"])
            for match in matches:
                alias, name, filter_col_name, filter_col_value = match
                models.append(Model(name=name, alias=alias,
                                    filter_col_name=filter_col_name, filter_col_value=filter_col_value))
        except Exception as e:
            raise Exception(f"Request body parse error of \"Models\": {e}")
        # relations
        try:
            relations: List[Relation] = []
            relation_desc = request_body["Relations"].split(",")
            for relation in relation_desc:
                if relation:
                    from_info, to_alias = relation.strip().split("->")
                    from_alias, from_col_name = from_info.split(".")
                    from_model = list(filter(lambda m: m.alias == from_alias, models))[0]
                    # print([m.alias for m in models], to_alias)
                    to_model = list(filter(lambda m: m.alias == to_alias, models))[0]
                    relations.append(Relation(from_model=from_model.name, from_col_name=from_col_name,
                                              to_model=to_model.name))
        except Exception as e:
            raise Exception(f"Request body parse error of \"Relations\": {e}")
        # fields
        try:
            fields: List[str] = request_body["Fields"].strip(",").split(",")
            fields = list(map(lambda f: f.strip(), fields))
        except Exception as e:
            raise Exception(f"Request body parse error of \"Fields\": {e}")
        # page_size, page_no
        limit = request_body.get("Limit", None)
        return cls(models=models, relations=relations, fields=fields, limit=limit)

    def to_orm_query(self):
        """
        ORM code example:
        import model
        ...
        results = db.query(model.A.name, model.A.status, model.B.name)
                  .join(model.B, model.A.id == model.B.uid)
                  .filter(model.A.status == "online")
                  .all()
        """
        orm_code = "db.query("
        model_alias_map = {model.alias: model.name for model in self.models}
        # to make sure all the models are queried even if no it's fields are specified, we add model id for each model
        # and these ids will be removed before send to client, see query.py
        for model in self.models:
            orm_code += f"model.{model.name}.id,"
        for field in self.fields:
            model_alias, field_name = field.split(".")
            orm_code += f"model.{model_alias_map[model_alias]}.{field_name},"
        orm_code = orm_code[:-1]
        for relation in self.relations:
            orm_code += ").join("
            orm_code += (f"model.{relation.to_model}, model.{relation.from_model}.{relation.from_col_name} "
                         f"== model.{relation.to_model}.id, isouter=True")
        orm_code += ").filter("
        have_filter = False
        for model in self.models:
            if model.filter_col_name:
                have_filter = True
                orm_code += f"model.{model.name}.{model.filter_col_name} == {model.filter_col_value},"
        orm_code = orm_code[:-1] if have_filter else orm_code
        if self.limit:
            offset, page_size = self.limit.split(",")
            orm_code += f").offset({offset}).limit({page_size}).all()"
        else:
            orm_code += ").all()"
        return orm_code


if __name__ == '__main__':
    # Example usage
    request_body = {
        "Models": "i: Item(name=\"testItem\"), u: Developer(id=1)",
        "Relations": "i.owner->u",
        "Fields": "i.name, u.name, u.status"
    }
    request = Request.from_request_body(request_body)
    print(request.to_orm_query())
    request_body = {
        "Models": "u: Developer(id=1)",
        "Relations": "",
        "Fields": "u.name"
    }
    request = Request.from_request_body(request_body)
    print(request.to_orm_query())
