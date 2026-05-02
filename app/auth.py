from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Child, DisabilityCategory, DisabilitySubcategory, Notification
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
    from app.forms import DISABILITY_CATEGORIES

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if request.method == 'POST':
        # Manually validate each child's subcategory against its category
        # This replaces the broken WTForms choice validation for dynamic dropdowns
        child_errors = []
        valid_children = 0

        for i, child_entry in enumerate(form.children.entries):
            cf = child_entry.form
            name = cf.name.data or ''
            age = cf.age.data
            category = cf.disability_category.data or ''
            subcategory = cf.disability_subcategory.data or ''

            has_data = bool(name.strip() or age or category or subcategory)

            if has_data:
                errors = {}
                if not name.strip():
                    errors['name'] = ["Child name is required."]
                if not age:
                    errors['age'] = ["Age is required."]
                if not category:
                    errors['disability_category'] = ["Select a disability category."]
                elif not subcategory:
                    errors['disability_subcategory'] = ["Select a disability subcategory."]
                elif category in DISABILITY_CATEGORIES:
                    valid_subs = DISABILITY_CATEGORIES[category]['subcategories']
                    if subcategory not in valid_subs:
                        errors['disability_subcategory'] = ["Not a valid subcategory for the selected category."]

                if errors:
                    child_errors.append((i, errors))
                else:
                    valid_children += 1

        # Only proceed if parent form is valid AND at least 1 valid child AND no child errors
        if form.validate_on_submit() and valid_children >= 1 and not child_errors:
            # Check if email already exists
            if User.query.filter_by(email=form.email.data).first():
                flash('❌ Email already registered. Please login instead.', 'danger')
                return redirect(url_for('auth.login'))

            # Create parent user
            user = User(
                email=form.email.data,
                name=form.name.data,
                county=form.county.data,
                is_admin=form.email.data.lower() in ADMIN_EMAILS
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()

            # Create children
            for child_entry in form.children.entries:
                cf = child_entry.form
                if (cf.name.data and cf.age.data and
                        cf.disability_category.data and cf.disability_subcategory.data):

                    category_name = cf.disability_category.data
                    category_code = DISABILITY_CATEGORIES[category_name]['code']
                    category = DisabilityCategory.query.filter_by(name=category_name).first()
                    if not category:
                        category = DisabilityCategory(name=category_name, code=category_code)
                        db.session.add(category)
                        db.session.flush()

                    subcategory_name = cf.disability_subcategory.data
                    subcategory = DisabilitySubcategory.query.filter_by(
                        name=subcategory_name, category_id=category.id
                    ).first()
                    if not subcategory:
                        subcategory = DisabilitySubcategory(name=subcategory_name, category=category)
                        db.session.add(subcategory)
                        db.session.flush()

                    child = Child(
                        name=cf.name.data,
                        age=cf.age.data,
                        parent=user
                    )
                    child.disabilities.append(subcategory)
                    db.session.add(child)

            db.session.commit()

            # Welcome notification for admins
            if user.is_admin:
                notification = Notification(
                    user_id=user.id,
                    title="Welcome Admin! 👑",
                    message="You have been set as an administrator. You can now manage users, approve posts, and add resources.",
                    notification_type="success"
                )
                db.session.add(notification)
                db.session.commit()

            flash('✅ Registration successful! Welcome to NCP-CDK Kenya. You can now login.', 'success')
            return redirect(url_for('auth.login'))

        else:
            # Show specific errors
            print("=" * 50)
            print("REGISTRATION ERRORS:", form.errors)
            print("Valid children:", valid_children)
            print("Child errors:", child_errors)
            print("=" * 50)

            if valid_children < 1:
                flash('⚠️ Please add at least one child with complete information.', 'danger')
            elif child_errors:
                flash('⚠️ Please correct the errors in the children section.', 'danger')
            else:
                flash('⚠️ Please correct the errors in the form.', 'danger')

    # Prepare disability data for JavaScript dropdown
    disability_data = {cat: data['subcategories'] for cat, data in DISABILITY_CATEGORIES.items()}

    return render_template('register.html', form=form, disability_data=disability_data)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember.data)
                flash(f'Welcome back, {user.name.split()[0]}! 👋', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.home'))
            else:
                flash('❌ Invalid email or password. Please try again.', 'danger')
        else:
            flash('⚠️ Please fill in all required fields.', 'danger')
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
                flash('✉️ A password reset email has been sent. Check your inbox and spam folder.', 'info')
                return redirect(url_for('auth.login'))
            else:
                flash('⚠️ Error sending password reset email. Please try again later.', 'danger')
        else:
            flash('✉️ If an account exists with this email, a password reset link will be sent.', 'info')
            return redirect(url_for('auth.login'))

    return render_template('forgot_password.html', form=form)


@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.query.filter_by(password_reset_token=token).first()

    if not user or not user.verify_password_reset_token(token):
        flash('❌ The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.login'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        user.clear_password_reset_token()
        db.session.commit()

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