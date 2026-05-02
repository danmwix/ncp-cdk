from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField,
    IntegerField, SelectMultipleField, BooleanField,
    FieldList, FormField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
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
    ("Murang'a", "Murang'a"),
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

# Disability Categories and Subcategories
DISABILITY_CATEGORIES = {
    'Physical Disabilities': {
        'code': 'MOH/276A',
        'subcategories': [
            'AMELIA', 'ACQUIRED BRAIN INJURIES', 'CEREBRAL PALSY', 'CONGENITAL HIP DISLOCATION',
            "ERB'S PALSY", 'HEMIPLEGIA', 'HYDROCEPHALUS', "KLUMPKE'S PALSY", 'MONOPLEGIA',
            'AMPUTATION', 'ARTHRITIS', 'ATHROGRYPOSIS', 'ANKYLOSING SPONDYLOSIS', 'CONGENITAL DEFORMITIES',
            'SHORT STATURE', 'FREEMAN SHELDON SYNDROME', 'KYPHOSCOLIOSIS', 'OSTEOGENESIS IMPERFECTA',
            'POLIO', 'PARAPLEGIA', 'ALBINISM', 'QUADRIPLEGIA', 'SPINA BIFIDA', 'CONTRACTURES',
            'PERMANENT COLOSTOMY', 'GIGANTISM', 'SCOLIOSIS, KYPHOSIS'
        ]
    },
    'Visual Impairment': {
        'code': 'MOH/276B',
        'subcategories': ['SEVERE VISUAL IMPAIRMENT', 'BLIND']
    },
    'Hearing Impairment': {
        'code': 'MOH/276C',
        'subcategories': [
            'GRADE O - NORMAL HEARING', 'GRADE 1 - SLIGHT (MILD)', 'GRADE 3 - SEVERE',
            'GRADE 4 - PROFOUND', 'DEAF/ABLE TO TALK NORMALLY', 'DEAF/USING SIGN LANGUAGE'
        ]
    },
    'Speech, Language, Communication and Swallowing Disabilities': {
        'code': 'MOH/276D',
        'subcategories': [
            'DYSFLUENCY - STAMMERING', 'CLUTTERING', 'ARTICULATION', 'LANGUAGE DISORDERS',
            'COMMUNICATION IMPAIRMENT', 'DYSPHAGIA', 'DYSARTHRIA', 'APRAXIA OR VERBAL DYSPRAXIA',
            'DEVELOPMENTAL LANGUAGE DISORDER', 'CONGENITAL LANGUAGE DISORDER', 'APHASIA',
            'STAMMERING', 'DYSPHAGIA STAGE 1 - PRE-ORAL', 'DYSPHAGIA STAGE 2 - ORAL',
            'DYSPHAGIA STAGE 3 - PHARYNGEAL', 'DYSPHAGIA STAGE 4 - OESOPHAGEAL'
        ]
    },
    'Mental/Intellectual/Autism Spectrum Disorders': {
        'code': 'MOH/276E',
        'subcategories': [
            'NEURO-DEVELOPMENTAL DISORDERS', 'SCHIZOPHRENIA SPECTRUM AND OTHER PSYCHOTIC DISORDERS',
            'BIPOLAR AND RELATED DISORDERS', 'DEPRESSIVE DISORDERS', 'ANXIETY DISORDER',
            'INTELLECTUAL DISABILITY', 'ATTENTION DEFICIT HYPERACTIVITY DISORDER',
            'SPECIFIC LEARNING DISORDER', 'DOWN SYNDROME', 'DYSLEXIA',
            'TRAUMA AND STRESS RELATED DISORDERS', 'SOMATIC SYMPTOMS AND RELATED DISORDERS',
            'AUTISM SPECTRUM DISORDER (ASD)'
        ]
    },
    'Maxillofacial Disabilities': {
        'code': 'MOH/276F',
        'subcategories': [
            'TOTAL ANODONTIA', 'LOSS OF JAWS', 'IMPAIRMENTS AFFECTING NERVES', 'LOSS/MISSING SOFT TISSUE',
            'FACIAL PAINS AND SYNDROME', 'XEROSTOMIA', 'TRISMUS', 'TOTAL JAW RESORPTION',
            'MICROGNATHIA (COMPLETE IMPAIRMENT)', 'MICROGNATHIA (UNILATERAL OR BILATERAL IMPAIRMENT)',
            'TEMPORAL-MANDIBULAR JOINT ANKYLOSIS', 'AGEUSIA', "BELL'S PALSY AND OTHER MOTOR NERVE DEFECTS",
            'SALIVARY GLANDS DISORDERS', 'CLEFT LIP AND PALATE'
        ]
    },
    'Progressive Chronic Disorders': {
        'code': 'MOH/276G',
        'subcategories': [
            'MULTIPLE SCLEROSIS', 'CHRONIC PROGRESSIVE DISORDERS', 'SEVERE OSTEOARTHRITIS',
            'VITILIGO', 'COPD', 'CHRONIC ISCHEMIC HEART DISEASE', 'CARDIOMYOPATHY', 'CYSTIC FIBROSIS',
            'RHEUMATIC HEART DISEASE', 'SYMPTOMATIC CONGENITAL HEART DISEASE', 'FIBROMYALGIA',
            'MUSCULAR DYSTROPHY', 'SEVERE SYSTEMIC LUPUS ERYTHEMATOSUS', 'RHEUMATOID ARTHRITIS',
            "REITER'S SYNDROME", 'POLYMYOSITIS', 'DEMENTIA', 'ALS (AMYOTROPHIC LATERAL SCLEROSIS)',
            "PARKINSON'S", 'HEREDITARY NEUROPATHY', 'EPILEPSY', 'INCLUSION TYPE MYOSITIS',
            "HUNTINGTON'S DISEASE MOTOR", "FRIEDREICH'S ATAXIA", 'SPINOCEREBELLAR DEGENERATION',
            'COMA AND PERSISTENT VEGETATIVE STATE', 'CHRONIC FATIGUE SYNDROME', 'STROKE',
            'BRAIN TUMORS', 'SPINAL CORD INJURY', 'ARACHNOIDITIS', 'HAEMATOLOGICAL E.G LEUKEMIA',
            'SOLID ORGANS', 'BONE/SOFT TISSUE TUMORS RESULTING IN AMPUTATION', 'HEAD AND NECK TUMORS',
            'INFLAMMATORY BOWEL DISEASES', 'LIVER CIRRHOSIS', 'CHRONIC PANCREATIC', 'PSORIASIS',
            'HYDRADENITIS SUPPURATIVA', 'SCLERODERMA', 'LYMPHEDEMA',
            'ASSOCIATION OF LYMPHEDEMA AND MASTECTOMY', 'MASTECTOMY', 'BOWEL INCONTINENCE'
        ]
    }
}

# Build a flat list of ALL possible subcategory values across all categories
# This is used to make WTForms accept any valid subcategory on form submission
ALL_SUBCATEGORIES = [('', 'Select Subcategory')]
for cat_data in DISABILITY_CATEGORIES.values():
    for sub in cat_data['subcategories']:
        ALL_SUBCATEGORIES.append((sub, sub))

# Build category choices
CATEGORY_CHOICES = [('', 'Select Category')] + [(cat, cat) for cat in DISABILITY_CATEGORIES.keys()]


class ChildForm(FlaskForm):
    class Meta:
        csrf = False

    name = StringField("Child's Name", validators=[Optional(), Length(max=100)])
    age = IntegerField("Child's Age", validators=[Optional(), NumberRange(min=0, max=25, message="Enter a valid age")])
    
    # KEY FIX: Set choices to ALL possible values so WTForms validation passes
    disability_category = SelectField(
        "Disability Category",
        choices=CATEGORY_CHOICES,
        validators=[Optional()]
    )
    disability_subcategory = SelectField(
        "Disability Subcategory",
        choices=ALL_SUBCATEGORIES,
        validators=[Optional()]
    )


class RegistrationForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(message="Full name is required"), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(message="Email is required"), Email(message="Enter a valid email address")])
    password = PasswordField('Password', validators=[DataRequired(message="Password is required"), Length(min=6, message="Password must be at least 6 characters")])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(message="Please confirm your password"), EqualTo('password', message="Passwords must match")])
    county = SelectField('Your County', choices=KENYA_COUNTIES, validators=[DataRequired(message="County selection is required")])

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
    disability_category = SelectField("Disability Category", choices=CATEGORY_CHOICES, validators=[DataRequired(message="Select a disability category")])
    disability_subcategory = SelectField("Disability Subcategory", choices=ALL_SUBCATEGORIES, validators=[DataRequired(message="Select a disability subcategory")])
    submit = SubmitField('Save Child Details')