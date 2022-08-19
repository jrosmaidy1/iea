import email
import os
from datetime import datetime

import flask
import requests
from dotenv import find_dotenv, load_dotenv
from flask import flash, redirect, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import BooleanField, DecimalField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

load_dotenv(find_dotenv())

app = flask.Flask(__name__)
app.secret_key = "TROLOLOLLOLOL"

# database flask config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

# initialize database
db = SQLAlchemy(app)

# login manager
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# loads user
@login_manager.user_loader
def load_user(name):
    """Get the current user name"""
    return Users.query.get(name)


# Users database model
class Users(db.Model, UserMixin):
    # nullable cannot be empty, unique email cannot be repeated
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # create a string
    def __repr__(self):
        return "<Name %r>" % self.name


# flask RegistrationForm
class RegistrationForm(FlaskForm):

    name = StringField(
        "Name",
        validators=[DataRequired(), Length(min=2, max=20)],
    )
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Sign Up")

    # validates user's email, returns error if email is taken
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")


# flask LoginForm class
class LoginForm(FlaskForm):

    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Login")

@app.route("/")
def main():
    """
    Main page, requires user authentication to see content
    """
    return flask.render_template("/welcome.html")


@app.route("/registration", methods=["GET", "POST"])
def registration():
    """
    Registration page, requires name and email
    """
    form = RegistrationForm()
    name = None  # initialize name
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash("User added successfully, log in using your email")
            return redirect(url_for("login"))

        name = form.name.data

        # clear form
        form.name.data = ""
        form.email.data = ""
    return flask.render_template(
        "/registration.html", form=form, name=name, email=email
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Login page, requires email
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            login_user(user)
            return redirect(url_for("home"))
        else:
            flash("Login unsuccessful, please check email")
    return flask.render_template("/login.html", form=form, email=email)


@app.route("/logout")
def logout():
    """
    Log user out and redirect to login page
    """
    logout_user()
    return redirect(url_for("login"))


@app.route("/welcome", methods=["GET", "POST"])
def landingPage():
    """
    Landing page detailing what our website offers
    """
    return flask.render_template("/welcome.html")


@app.route("/home", methods=["GET", "POST"])
def home():
    """
    Home page to view adoptions
    """
    if current_user.is_authenticated:
        name = current_user.name
        email = current_user.email
        return flask.render_template("/welcome.html", name=name, email=email)

    return redirect(url_for("welcome"))



@app.route("/userLogin", methods=["GET", "POST"])
def userLogin():
    return flask.render_template("userLogin.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8081, debug=True)