
from uforms.forms import Jinja2Form
from pydantic import BaseModel


class User(BaseModel):
    name: str
    age: int


def test_jinja2_form_render():
    forms = Jinja2Form()
    form = forms.register(User)
    assert form
