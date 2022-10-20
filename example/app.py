import json
from datetime import date, datetime, time
from enum import Enum

from flask import Flask, jsonify, render_template, request
from pydantic import BaseModel, EmailStr, HttpUrl, SecretStr, ValidationError
from pydantic.color import Color

from uforms.forms import Jinja2Form

app = Flask(__name__)

forms = Jinja2Form(theme="bootstrap")

users = []


class Animal(str, Enum):
    dog = "dog"
    cat = "cat"


class UserSchema(BaseModel):
    name: str = "chaojie"
    age: int = 20
    birthday: date = datetime.now().date()
    home_page: HttpUrl = "https://google.com/"
    color: Color = Color("#2e68d3")
    password: SecretStr = "123456"
    is_student: bool = True
    email: EmailStr = "hi@chaojie.fun"
    animal: Animal = Animal.dog


@app.route("/users", methods=["GET", "POST"])
def users_view():
    if request.method == "GET":
        form = forms.register(UserSchema)
        context = {"form": form}
        return render_template("user.html", **context)
    elif request.method == "POST":
        try:
            new_user = UserSchema(**request.form)
        except ValidationError as e:
            pass
        users.append(json.loads(new_user.json()))
        return jsonify({"users": users})


if __name__ == "__main__":
    app.run(debug=True, port=5001)
