from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileField, FileAllowed

class UserLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UserSignupForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    address = StringField("Address", validators=[DataRequired(), Length(min=3, max=50)])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(min=10, max=10)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Sign Up")
    
class DryFruitForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    image = FileField("Image", validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    price = DecimalField('Price (₹)', validators=[DataRequired()])
    priority = IntegerField('Priority (lower = first)', default=0)
    submit = SubmitField('Save')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')