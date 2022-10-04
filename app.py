import email
import os
from datetime import datetime

import flask
import requests
from dotenv import find_dotenv, load_dotenv
from flask import flash, redirect, request, url_for
from flask_login import (LoginManager, UserMixin, current_user, login_user,
                         logout_user)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import (BooleanField, DecimalField, PasswordField, StringField,
                     SubmitField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                ValidationError)
from wtforms.widgets import TextArea

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

# Teams database model
class Teams(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    bio = db.Column(db.Text)
    certification = db.Column(db.Text)

#flask Teams form
class TeamsForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    bio = StringField("Bio",widget=TextArea())
    certification = StringField("Certification", widget=TextArea())
    submit = SubmitField("Save")

@app.route("/teams", methods=["GET", "POST"])
def teams():
    teams = Teams.query.all()
    return flask.render_template("/teams.html",teams=teams)

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
# Add Teams
@app.route("/addTeams", methods=["GET", "POST"])
def addTeams():
    form = TeamsForm()
    if form.validate_on_submit():
        team = Teams(name=form.name.data, bio=form.bio.data, certification = form.certification.data)
        form.name.data = ''
        form.bio.data = ''
        form.certification.data = ''
        db.session.add(team)
        db.session.commit()
        flash("Team data added Successfully!")
    return flask.render_template("addTeams.html", form=form)

@app.route('/teams/delete/<int:id>')
def delete_team(id):
    team_to_delete = Teams.query.get_or_404(id)
    try:
        db.session.delete(team_to_delete)
        db.session.commit()
        # Return a message
        flash("Blog Post Was Deleted!")
        # Grab all the posts from the database
        teams = Teams.query.all()
        return flask.render_template("teams.html", teams=teams)

    except:
    	# Return an error message
        flash("Whoops! There was a problem deleting post, try again...")
        teams = Teams.query.all()
        return flask.render_template("teams.html", teams=teams)
# else:
#     # Return a message
#     flash("You Aren't Authorized To Delete That Post!")

#     # Grab all the posts from the database
    # teams = Teams.query.all()
    # return flask.render_template("teams.html", teams=teams)

@app.route('/teams/edit/<int:id>', methods=['GET', 'POST'])
def edit_team(id):
    team = Teams.query.get_or_404(id)
    form = TeamsForm()
    if form.validate_on_submit():
        team.name = form.name.data
        #post.author = form.author.data
        team.bio = form.bio.data
        team.certification = form.certification.data
        # Update Database
        db.session.add(team)
        db.session.commit()
        flash("Post Has Been Updated!")
        return redirect(url_for('team', id=team.id))
    form.name.data = team.name
    #form.author.data = post.author
    form.bio.data = team.bio
    form.certification.data = team.certification
    return flask.render_template('editTeams.html', form=form)
	# else:
	# 	flash("You Aren't Authorized To Edit This Post...")
	# 	posts = Posts.query.order_by(Posts.date_posted)
	# 	return render_template("posts.html", posts=posts)       
@app.route('/team/<int:id>')
def team(id):
	team = Teams.query.get_or_404(id)
	return flask.render_template('team.html', team=team)

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
