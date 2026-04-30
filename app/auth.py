from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Child, DisabilityCategory, Notification
from app.forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from app.email_utils import send_password_reset_email, send_notification_email

# Admin email list - these users will automatically be admins
ADMIN_EMAILS = {
    'danielmwanzia292@gmail.com',
    'jmetet26@gmail.com',
    'ibrahim14adan@gmail.com',
    'kamandeangela2021@gmail.com'
}

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    # Populate disability choices dynamically for each child form
    disabilities = DisabilityCategory.query.all()
    choices = [(str(d.id), d.name) for d in disabilities]
    for child_form in form.children:
        child_form.form.disabilities.choices = choices

    if request.method == 'POST':
        # Custom validation: Check that at least one child has complete data
        valid_children = 0
        for child_form in form.children.entries:
            name = child_form.form.name.data
            age = child_form.form.age.data
            disabilities = child_form.form.disabilities.data
            
            # Check if any field has data
            has_data = bool(name or age or disabilities)
            
            if has_data:
                # If any field has data, all must be filled
                if not name:
                    child_form.form.name.errors = ("Child name is required if adding a child",)
                elif not age:
                    child_form.form.age.errors = ("Age is required if adding a child",)
                elif not disabilities:
                    child_form.form.disabilities.errors = ("Select at least one disability if adding a child",)
                else:
                    valid_children += 1
        
        # Validate parent form + at least 1 valid child
        if form.validate_on_submit() and valid_children >= 1:
            # Check if email already exists
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered. Please login instead.', 'danger')
                return redirect(url_for('auth.login'))

            # Create parent user
            user = User(
                email=form.email.data,
                name=form.name.data,
                county=form.county.data,
                is_admin=form.email.data.lower() in ADMIN_EMAILS  # Auto-set admin if email matches
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()

            # Create children linked to parent
            for child_form in form.children.entries:
                if child_form.form.name.data and child_form.form.age.data and child_form.form.disabilities.data:
                    child = Child(
                        name=child_form.form.name.data,
                        age=child_form.form.age.data,
                        parent=user
                    )
                    selected_ids = [int(did) for did in child_form.form.disabilities.data]
                    child.disabilities = DisabilityCategory.query.filter(
                        DisabilityCategory.id.in_(selected_ids)
                    ).all()
                    db.session.add(child)

            db.session.commit()

            # Send welcome notification to admins
            if user.is_admin:
                notification = Notification(
                    user_id=user.id,
                    title="Welcome Admin! ",
                    message="You have been set as an administrator. You can now manage users, approve posts, and add resources.",
                    notification_type="success"
                )
                db.session.add(notification)
                db.session.commit()

            flash('✅ Registration successful! Welcome to NCP-CDK Kenya. You can now login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            # Debug: Print validation errors
            print("=" * 50)
            print("REGISTRATION FORM VALIDATION ERRORS:")
            print("Form errors:", form.errors)
            print(f"Valid children count: {valid_children}")
            print("=" * 50)
            if valid_children < 1:
                flash('Please add at least one child with complete information.', 'danger')
            else:
                flash('Please correct the errors in the form.', 'danger')

    return render_template('register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash(f'Welcome back, {user.name.split()[0]}! 👋', 'success')
                return redirect(url_for('main.home'))
            else:
                flash('Invalid email or password. Please try again.', 'danger')
        else:
            flash('Please fill in all required fields.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.home'))

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if send_password_reset_email(user):
                db.session.commit()
                flash('✉️ A password reset email has been sent to your email address. Check your inbox and spam folder.', 'info')
                return redirect(url_for('auth.login'))
            else:
                flash('⚠️ Error sending password reset email. Please try again later.', 'danger')
        else:
            # Don't reveal if email exists for security
            flash('✉️ If an account exists with this email, a password reset link will be sent.', 'info')
            return redirect(url_for('auth.login'))
    
    return render_template('forgot_password.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # Find user with this token
    user = User.query.filter_by(password_reset_token=token).first()
    
    if not user or not user.verify_password_reset_token(token):
        flash('❌ The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_password_reset_token()
        db.session.commit()
        
        # Create notification
        notification = Notification(
            user_id=user.id,
            title="Password Reset Successfully",
            message="Your password has been reset successfully. You can now login with your new password.",
            notification_type="success"
        )
        db.session.add(notification)
        db.session.commit()
        
        flash('✅ Your password has been reset successfully. You can now login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('reset_password.html', form=form, token=token)
