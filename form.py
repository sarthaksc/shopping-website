from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, IntegerField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL, Optional


class AddForm(FlaskForm):
    id = IntegerField("Product ID", validators=[DataRequired()])
    name = StringField("Product Name", validators=[DataRequired()])
    price = IntegerField("Price", validators=[DataRequired()])
    img = StringField("Image URL", validators=[DataRequired()])
    category = SelectField("Select Category",
                           choices=[('dairy_bread_eggs', 'Dairy,Bread and Eggs'),
                                    ('fruits_vegetables', 'Fruits and Vegetables'),
                                    ('cold_drinks_juices', 'Cold Drinks and Juices'), ('snacks', 'Snacks'),
                                    ('breakfast', 'Breakfast & Instant Food'), ('tea_coffee', 'Tea & Coffee'),
                                    ('masala_oil', 'Masalas and Spices'),
                                    ('chicken_meat_fish', 'Chicken, Meat and Fish')], validators=[DataRequired()])
    submit = SubmitField("Add Item")


class DeleteForm(FlaskForm):
    id = IntegerField("Product ID", validators=[DataRequired()])
    submit = SubmitField("Delete Item")


class LoginForm(FlaskForm):
    email = EmailField("E-mail ID", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("E-mail", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    repeat_password = PasswordField("Password", validators=[DataRequired()])
    conditions = BooleanField("Conditions", validators=[Optional()])
    submit = SubmitField("Register")
