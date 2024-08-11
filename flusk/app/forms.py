from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange


class SignupForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=30)])
    password = StringField('password', validators=[DataRequired(), Length(min=8)])
    repeat_password = StringField('repeat_password', validators=[DataRequired(), Length(min=3, max=30)])
    age = IntegerField('age', validators=[DataRequired(), NumberRange(min=1, max=120)])


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=30)])
    password = StringField('password', validators=[DataRequired()])


class GameBuyForm(FlaskForm):
    game_id = IntegerField('game_id', validators=[DataRequired()])
