from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField,
    IntegerField, SelectMultipleField, BooleanField,
    FieldList, FormField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from wtforms.widgets import ListWidget, CheckboxInput

# Custom Checkbox Field
class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

# Kenyan counties
KENYA_COUNTIES = [
    ('Nairobi', 'Nairobi'), ('Kiambu', 'Kiambu'), ('Mombasa', 'Mombasa'), ('Kisumu', 'Kisumu'),
    ('Nakuru', 'Nakuru'), ('Uasin Gishu', 'Uasin Gishu'), ('Kakamega', 'Kakamega'), ('Kisii', 'Kisii'),
    ('Nyeri', 'Nyeri'), ('Meru', 'Meru'), ('Machakos', 'Machakos'), ('Kitui', 'Kitui'),
    ('Kilifi', 'Kilifi'), ('Kwale', 'Kwale'), ('Taita Taveta', 'Taita Taveta'), ('Garissa', 'Garissa'),
]

class ChildForm(FlaskForm):
    class Meta:
        csrf = False
    
    name = StringField("Child's Name", validators=[Length(max=100)])
    age = IntegerField("Child's Age", validators=[NumberRange(min=0, max=25, message="Enter a valid age")])
    disabilities = MultiCheckboxField("Disabilities", choices=[])

class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(message="Full name is required"), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(message="Email is required"), Email(message="Enter a valid email address")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required"), Length(min=6, message="Password must be at least 6 characters")])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(message="Please confirm your password"), EqualTo('password', message="Passwords must match")])
    county = SelectField('Your County', choices=KENYA_COUNTIES, validators=[DataRequired(message="County selection is required")])

    # Flexible number of children (min 1, max 10)
    children = FieldList(FormField(ChildForm), min_entries=1, max_entries=10)

    submit = SubmitField('Create Account & Join Community')

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(message="Email is required"), Email(message="Enter a valid email address")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class AdminLoginForm(FlaskForm):
    email = StringField('Admin Email Address', validators=[DataRequired(message="Email is required"), Email(message="Enter a valid email address")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required")])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Admin Login')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(message="Email is required"), Email(message="Enter a valid email address")])
    submit = SubmitField('Send Password Reset Email')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(message="Password is required"), Length(min=6, message="Password must be at least 6 characters")])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(message="Please confirm your password"), EqualTo('password', message="Passwords must match")])
    submit = SubmitField('Reset Password')

class EditProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(message="Full name is required"), Length(max=100)])
    county = SelectField('Your County', choices=KENYA_COUNTIES, validators=[DataRequired(message="County selection is required")])
    submit = SubmitField('Save Changes')

class EditChildForm(FlaskForm):
    name = StringField('Child Name', validators=[DataRequired(message="Child name is required"), Length(max=100)])
    age = IntegerField('Child Age', validators=[DataRequired(message="Age is required"), NumberRange(min=0, max=25, message="Enter a valid age")])
    disabilities = MultiCheckboxField('Disabilities', choices=[], validators=[DataRequired(message="Select at least one disability")])
    submit = SubmitField('Save Child Details')
