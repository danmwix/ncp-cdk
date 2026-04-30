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

# All 47 Kenyan counties
KENYA_COUNTIES = [
    ('Baringo', 'Baringo'),
    ('Bomet', 'Bomet'),
    ('Bungoma', 'Bungoma'),
    ('Busia', 'Busia'),
    ('Elgeyo-Marakwet', 'Elgeyo-Marakwet'),
    ('Embu', 'Embu'),
    ('Garissa', 'Garissa'),
    ('Homa Bay', 'Homa Bay'),
    ('Isiolo', 'Isiolo'),
    ('Kajiado', 'Kajiado'),
    ('Kakamega', 'Kakamega'),
    ('Kericho', 'Kericho'),
    ('Kiambu', 'Kiambu'),
    ('Kilifi', 'Kilifi'),
    ('Kirinyaga', 'Kirinyaga'),
    ('Kisii', 'Kisii'),
    ('Kisumu', 'Kisumu'),
    ('Kitui', 'Kitui'),
    ('Kwale', 'Kwale'),
    ('Laikipia', 'Laikipia'),
    ('Lamu', 'Lamu'),
    ('Machakos', 'Machakos'),
    ('Makueni', 'Makueni'),
    ('Mandera', 'Mandera'),
    ('Marsabit', 'Marsabit'),
    ('Meru', 'Meru'),
    ('Migori', 'Migori'),
    ('Mombasa', 'Mombasa'),
    ('Murang\'a', 'Murang\'a'),
    ('Nairobi', 'Nairobi'),
    ('Nakuru', 'Nakuru'),
    ('Nandi', 'Nandi'),
    ('Narok', 'Narok'),
    ('Nyamira', 'Nyamira'),
    ('Nyandarua', 'Nyandarua'),
    ('Nyeri', 'Nyeri'),
    ('Samburu', 'Samburu'),
    ('Siaya', 'Siaya'),
    ('Taita Taveta', 'Taita Taveta'),
    ('Tana River', 'Tana River'),
    ('Tharaka-Nithi', 'Tharaka-Nithi'),
    ('Trans Nzoia', 'Trans Nzoia'),
    ('Turkana', 'Turkana'),
    ('Uasin Gishu', 'Uasin Gishu'),
    ('Vihiga', 'Vihiga'),
    ('Wajir', 'Wajir'),
    ('West Pokot', 'West Pokot'),
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