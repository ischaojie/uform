from datetime import date, datetime, time
from enum import Enum
from secrets import token_hex
from typing import (
    Any,
    Sequence,
    Type,
)

from jinja2 import Environment, PackageLoader
from markupsafe import Markup
from pydantic import AnyUrl, BaseModel, SecretField, EmailStr
from pydantic.color import Color
from collections import OrderedDict

SUPPORT_THEMES = ("bootstrap",)

TYPE_INPUT_MAPPING = OrderedDict(
    {
        bool: "checkbox",
        int: "number",
        float: "number",
        datetime: "datetime-local",
        date: "date",
        time: "time",
        Color: "color",
        AnyUrl: "url",
        SecretField: "password",
        EmailStr: "email",
        Enum: "radio",
        bytes: "text",
        # make sure type str always in the end.
        str: "text",
    }
)


def select_input_type(field_type: Type[Any]) -> str:
    for type_, input in TYPE_INPUT_MAPPING.items():
        if issubclass(field_type, type_):
            return input
    return "text"


def concat_field_extra_attrs(extra_attrs: Sequence) -> str:
    r = []
    for e in extra_attrs:
        if isinstance(e, dict):
            r.extend([f'{k}="{v}"' for k, v in e.items()])
        elif isinstance(e, list):
            r.extend(e)
        else:
            r.append(e)
    return " ".join(r)


class Form:
    def __init__(
        self, *, env: "Environment", schema: BaseModel, theme: str = "bootstrap"
    ) -> None:
        assert theme in SUPPORT_THEMES, "Not supported this theme."
        self.env = env
        self.schema = schema
        self.theme = theme

    def render(self) -> str:
        # TODO: <textarea> <select> file
        render_fields = []
        template = self.env.get_template(f"{self.theme}/base.html")
        for field_name, field in self.schema.__fields__.items():
            # some extra property need for <input>
            extra_attrs = []
            extra = {}
            field_default = field.default
            input_type = select_input_type(field.type_)
            if issubclass(field.type_, Color):
                # FIXME: when colors by name, should return full hex not shorthand.
                field_default = Color(field.default).as_hex()
            if issubclass(field.type_, bool):
                if field.default:
                    extra_attrs.append("checked")
            if input_type == "radio" and issubclass(field.type_, Enum):
                extra["options"] = [
                    {
                        "id": token_hex(8),
                        "name": e.name,
                        "value": e.name,
                        "checked": field.default == e,
                    }
                    for e in field.type_
                ]
            field = {
                "name": field_name,
                "type": input_type,
                "id": token_hex(8),
                "value": field_default,
                "extra_attrs": concat_field_extra_attrs(extra_attrs),
                "extra": extra,
            }
            render_fields.append(field)
        return template.render(fields=render_fields)

    def __str__(self) -> str:
        return self.render()

    def __html__(self) -> Markup:
        return Markup(self.render())

    def register(self, schema: BaseModel):
        raise NotImplementedError


class Jinja2Form(Form):
    def __init__(self, *, theme: str = "bootstrap") -> None:
        self.theme = theme
        self.env = self.get_template_engine()

    def get_template_engine(self) -> Environment:
        loader = PackageLoader("uforms", "templates")
        return Environment(loader=loader, autoescape=True)

    def register(self, schema: BaseModel) -> Form:
        return Form(env=self.env, schema=schema, theme=self.theme)
