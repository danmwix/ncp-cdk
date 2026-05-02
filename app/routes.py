from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, jsonify
from flask_login import login_required, current_user
from app import db, mail
from app.models import DisabilityCategory, DisabilitySubcategory, Child, SupportGroup, GroupMessage, Event, Story, User, Notification
from app.forms import EditProfileForm, EditChildForm, ChildForm
from flask_mail import Message
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
from sqlalchemy import desc

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return render_template('home.html')

@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@main_bp.route('/forums')
@login_required
def forums():
    disabilities = DisabilityCategory.query.all()
    return render_template('forums.html', disabilities=disabilities)

# Group Chat for a specific disability
@main_bp.route('/group_chat/<int:disability_id>', methods=['GET', 'POST'])
@login_required
def group_chat(disability_id):
    disability = DisabilityCategory.query.get_or_404(disability_id)
    
    # Get or create support group for this disability
    group = SupportGroup.query.filter_by(disability_id=disability_id).first()
    if not group:
        group = SupportGroup(disability_id=disability_id)
        db.session.add(group)
        db.session.commit()
    
    # Join group if not already a member
    if current_user not in group.members:
        group.members.append(current_user)
        db.session.commit()
        flash(f'✅ You joined the {disability.name} support group!', 'success')
    
    # Handle new message posting with file upload
    if request.method == 'POST':
        content = request.form.get('message', '').strip()
        file = request.files.get('file')
        
        if content or file:
            message = GroupMessage(
                content=content,
                author=current_user,
                group=group
            )
            
            # Handle file upload
            if file and file.filename:
                ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'mp4', 'mov', 'avi'}
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                
                if ext in ALLOWED_EXTENSIONS:
                    upload_folder = os.path.join(os.path.dirname(__file__), 'static', 'uploads', str(group.id))
                    os.makedirs(upload_folder, exist_ok=True)
                    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    file.save(os.path.join(upload_folder, filename))
                    message.file_name = file.filename
                    message.file_path = f'uploads/{group.id}/{filename}'
                    message.file_type = file.content_type
                    flash(f'File "{file.filename}" uploaded successfully!', 'success')
                else:
                    flash(f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}', 'danger')
            
            db.session.add(message)
            db.session.commit()
            flash('Message posted successfully!', 'success')
            return redirect(url_for('main.group_chat', disability_id=disability_id))
    
    messages = GroupMessage.query.filter_by(group_id=group.id).order_by(GroupMessage.created_at.desc()).all()
    
    return render_template('group_chat.html', 
                         disability=disability, 
                         group=group, 
                         messages=messages)

# Edit parent profile
@main_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.county = form.county.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    else:
        if request.method == 'POST':
            print(form.errors)
            flash('Please correct the errors in the form.', 'danger')
    return render_template('edit_profile.html', form=form)

# Edit child details
@main_bp.route('/edit_child/<int:child_id>', methods=['GET', 'POST'])
@login_required
def edit_child(child_id):
    from app.forms import DISABILITY_CATEGORIES
    
    child = Child.query.get_or_404(child_id)
    if child.parent != current_user:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.profile'))

    form = EditChildForm(obj=child)
    
    category_choices = [('', 'Select Category')] + [(cat, cat) for cat in DISABILITY_CATEGORIES.keys()]
    form.disability_category.choices = category_choices
    form.disability_subcategory.choices = [('', 'Select Subcategory')]
    
    if child.disabilities:
        subcategory = child.disabilities[0]
        form.disability_category.data = subcategory.category.name
        form.disability_subcategory.data = subcategory.name
        if subcategory.category.name in DISABILITY_CATEGORIES:
            sub_choices = [('', 'Select Subcategory')] + [(sub, sub) for sub in DISABILITY_CATEGORIES[subcategory.category.name]['subcategories']]
            form.disability_subcategory.choices = sub_choices

    if form.validate_on_submit():
        category_name = form.disability_category.data
        category_code = DISABILITY_CATEGORIES[category_name]['code']
        category = DisabilityCategory.query.filter_by(name=category_name).first()
        if not category:
            category = DisabilityCategory(name=category_name, code=category_code)
            db.session.add(category)
            db.session.flush()
        
        subcategory_name = form.disability_subcategory.data
        subcategory = DisabilitySubcategory.query.filter_by(
            name=subcategory_name, category_id=category.id
        ).first()
        if not subcategory:
            subcategory = DisabilitySubcategory(name=subcategory_name, category=category)
            db.session.add(subcategory)
            db.session.flush()
        
        child.name = form.name.data
        child.age = form.age.data
        child.disabilities = [subcategory]
        db.session.commit()
        flash('Child details updated successfully!', 'success')
        return redirect(url_for('main.profile'))
    else:
        if request.method == 'POST':
            print(form.errors)
            flash('Please correct the errors in the form.', 'danger')
    
    disability_data = {cat: data['subcategories'] for cat, data in DISABILITY_CATEGORIES.items()}
    return render_template('edit_child.html', form=form, child=child, disability_data=disability_data)

# Add new child
@main_bp.route('/add_child', methods=['GET', 'POST'])
@login_required
def add_child():
    from app.forms import DISABILITY_CATEGORIES
    
    form = ChildForm()
    
    category_choices = [('', 'Select Category')] + [(cat, cat) for cat in DISABILITY_CATEGORIES.keys()]
    form.disability_category.choices = category_choices
    form.disability_subcategory.choices = [('', 'Select Subcategory')]

    if form.validate_on_submit():
        category_name = form.disability_category.data
        category_code = DISABILITY_CATEGORIES[category_name]['code']
        category = DisabilityCategory.query.filter_by(name=category_name).first()
        if not category:
            category = DisabilityCategory(name=category_name, code=category_code)
            db.session.add(category)
            db.session.flush()
        
        subcategory_name = form.disability_subcategory.data
        subcategory = DisabilitySubcategory.query.filter_by(
            name=subcategory_name, category_id=category.id
        ).first()
        if not subcategory:
            subcategory = DisabilitySubcategory(name=subcategory_name, category=category)
            db.session.add(subcategory)
            db.session.flush()
        
        child = Child(
            name=form.name.data,
            age=form.age.data,
            parent=current_user
        )
        child.disabilities.append(subcategory)
        db.session.add(child)
        db.session.commit()
        flash('New child added successfully!', 'success')
        return redirect(url_for('main.profile'))
    else:
        if request.method == 'POST':
            print(form.errors)
            flash('Please correct the errors in the form.', 'danger')
    
    disability_data = {cat: data['subcategories'] for cat, data in DISABILITY_CATEGORIES.items()}
    return render_template('add_child.html', form=form, disability_data=disability_data)

# Resource Library
@main_bp.route('/resources')
@login_required
def resources():
    return render_template('resources.html')

# Events Calendar
@main_bp.route('/events')
@login_required
def events():
    upcoming_events = Event.query.filter(Event.date >= datetime.utcnow()).order_by(Event.date).all()
    past_events = Event.query.filter(Event.date < datetime.utcnow()).order_by(desc(Event.date)).limit(5).all()
    return render_template('events.html', 
                         upcoming_events=upcoming_events, 
                         past_events=past_events,
                         now=datetime.utcnow())

@main_bp.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    if not current_user.is_admin:
        flash('Only admins can create events.', 'danger')
        return redirect(url_for('main.events'))
    
    if request.method == 'POST':
        title = request.form.get('title').strip()
        description = request.form.get('description').strip()
        location = request.form.get('location').strip()
        date_str = request.form.get('date')
        
        if title and description and location and date_str:
            try:
                event_date = datetime.fromisoformat(date_str)
                event = Event(
                    title=title,
                    description=description,
                    location=location,
                    date=event_date,
                    created_by=current_user
                )
                db.session.add(event)
                db.session.commit()
                flash('Event created successfully!', 'success')
                return redirect(url_for('main.events'))
            except ValueError:
                flash('Invalid date format.', 'danger')
        else:
            flash('All fields are required.', 'danger')
    
    return render_template('add_event.html')

# Stories/Testimonials
@main_bp.route('/stories')
@login_required
def stories():
    approved_stories = Story.query.filter_by(is_approved=True).order_by(desc(Story.created_at)).all()
    return render_template('stories.html', stories=approved_stories)

@main_bp.route('/submit_story', methods=['GET', 'POST'])
@login_required
def submit_story():
    if request.method == 'POST':
        title = request.form.get('title').strip()
        content = request.form.get('content').strip()
        is_anonymous = request.form.get('anonymous') == 'on'
        
        if title and content:
            story = Story(
                title=title,
                content=content,
                is_anonymous=is_anonymous,
                author=current_user,
                is_approved=False
            )
            db.session.add(story)
            db.session.commit()
            flash('Story submitted! It will appear after admin review.', 'success')
            return redirect(url_for('main.stories'))
        else:
            flash('Title and content are required.', 'danger')
    
    return render_template('submit_story.html')

# Admin Panel
@main_bp.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('main.home'))
    
    pending_stories = Story.query.filter_by(is_approved=False).all()
    all_users = User.query.all()
    all_events = Event.query.order_by(desc(Event.date)).all()
    now = datetime.utcnow()
    upcoming_event_count = len([e for e in all_events if e.date > now])
    
    return render_template('admin_dashboard.html', 
                         pending_stories=pending_stories,
                         all_users=all_users,
                         all_events=all_events,
                         upcoming_event_count=upcoming_event_count,
                         now=now)

@main_bp.route('/admin/approve_story/<int:story_id>', methods=['POST'])
@login_required
def approve_story(story_id):
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('main.home'))
    story = Story.query.get_or_404(story_id)
    story.is_approved = True
    db.session.commit()
    flash(f'Story "{story.title}" approved!', 'success')
    return redirect(url_for('main.admin'))

@main_bp.route('/admin/reject_story/<int:story_id>', methods=['POST'])
@login_required
def reject_story(story_id):
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('main.home'))
    story = Story.query.get_or_404(story_id)
    db.session.delete(story)
    db.session.commit()
    flash('Story rejected and deleted.', 'success')
    return redirect(url_for('main.admin'))

@main_bp.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def toggle_admin(user_id):
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('main.home'))
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    status = 'promoted to admin' if user.is_admin else 'removed from admin'
    flash(f'User {user.name} {status}.', 'success')
    return redirect(url_for('main.admin'))

@main_bp.route('/admin/delete_event/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    if not current_user.is_admin:
        flash('Admin access required.', 'danger')
        return redirect(url_for('main.home'))
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted.', 'success')
    return redirect(url_for('main.admin'))

# Notifications
@main_bp.route('/notifications')
@login_required
def notifications():
    page = request.args.get('page', 1, type=int)
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc())\
        .paginate(page=page, per_page=10)
    return render_template('notifications.html', notifications=notifications)

@main_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.home'))
    notification.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for('main.notifications'))

@main_bp.route('/notifications/<int:notification_id>/delete', methods=['POST'])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('main.home'))
    db.session.delete(notification)
    db.session.commit()
    flash('Notification deleted.', 'info')
    return redirect(request.referrer or url_for('main.notifications'))

@main_bp.route('/notifications/unread-count')
@login_required
def unread_notifications_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return str(count)

# ===== PARTNER WITH US =====
@main_bp.route('/partner-request', methods=['POST'])
def partner_request():
    try:
        data = request.get_json()
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()

        if not name or not email or not phone:
            return jsonify({'success': False, 'error': 'All fields are required.'}), 400

        msg = Message(
            subject=f'🤝 New Partnership Request from {name}',
            sender=('NCP-CDK Kenya', 'info.ncpcdk@gmail.com'),
            recipients=['info.ncpcdk@gmail.com'],
            body=f"""
New Partnership Request Received
=================================

Name:    {name}
Email:   {email}
Phone:   {phone}

Please follow up with this person at your earliest convenience.

---
This message was sent automatically from the NCP-CDK Kenya website.
            """.strip()
        )

        mail.send(msg)
        return jsonify({'success': True}), 200

    except Exception as e:
        print(f"[Partner Request Error]: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500