from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Story, Notification, Resource, DisabilityCategory
from app.forms import AdminLoginForm
from app.email_utils import send_notification_email
from functools import wraps
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# Decorator to check if user is admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('❌ You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data) and user.is_admin:
            login_user(user, remember=form.remember.data)
            flash(f'Welcome Admin, {user.name.split()[0]}!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('❌ Invalid admin credentials or account is not an admin.', 'danger')
    
    return render_template('admin_login.html', form=form)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_users = User.query.count()
    total_admins = User.query.filter_by(is_admin=True).count()
    total_stories = Story.query.count()
    pending_stories = Story.query.filter_by(is_approved=False).count()
    
    stats = {
        'total_users': total_users,
        'total_admins': total_admins,
        'total_stories': total_stories,
        'pending_stories': pending_stories
    }
    
    # Get recent activities
    recent_stories = Story.query.order_by(Story.created_at.desc()).limit(5).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         recent_stories=recent_stories,
                         recent_users=recent_users)

@admin_bp.route('/approve_posts', methods=['GET', 'POST'])
@login_required
@admin_required
def approve_posts():
    page = request.args.get('page', 1, type=int)
    
    if request.method == 'POST':
        story_id = request.form.get('story_id')
        action = request.form.get('action')
        reason = request.form.get('reason', '')
        
        story = Story.query.get_or_404(story_id)
        
        if action == 'approve':
            story.is_approved = True
            story.status = "approved"          # ← Added as requested
            story.rejected_reason = None
            db.session.commit()
            
            # Send notification to author
            notification = Notification(
                user_id=story.author_id,
                title="✅ Your Story Was Approved!",
                message=f"Your story '{story.title}' has been approved and is now visible to the community.",
                notification_type="success"
            )
            db.session.add(notification)
            db.session.commit()
            
            send_notification_email(
                story.author,
                "Story Approved",
                f"Great news! Your story '{story.title}' has been approved and is now visible to the community."
            )
            
            flash(f'✅ Story approved: {story.title}', 'success')
        
        elif action == 'reject':
            story.is_approved = False
            story.status = "rejected"          # ← Added as requested
            story.rejected_reason = reason
            db.session.commit()
            
            # Send notification to author
            notification = Notification(
                user_id=story.author_id,
                title="📋 Your Story Needs Changes",
                message=f"Your story '{story.title}' was not approved. Reason: {reason}",
                notification_type="warning"
            )
            db.session.add(notification)
            db.session.commit()
            
            send_notification_email(
                story.author,
                "Story Needs Changes",
                f"Your story '{story.title}' was not approved.\n\nReason: {reason}\n\nPlease review and resubmit if you'd like us to reconsider."
            )
            
            flash(f'❌ Story rejected: {story.title}', 'info')
        
        return redirect(url_for('admin.approve_posts', page=page))
    
    # Get pending and approved stories
    # Updated to use status field as requested (fallback to is_approved for compatibility)
    pending_stories = Story.query.filter(
        (Story.status == "pending") | 
        ((Story.status.is_(None)) & (Story.is_approved == False))
    ).paginate(page=page, per_page=10)
    
    approved_stories = Story.query.filter_by(is_approved=True)\
                        .order_by(Story.created_at.desc()).limit(5).all()
    
    return render_template('approve_posts.html', 
                         pending_stories=pending_stories,
                         approved_stories=approved_stories)

@admin_bp.route('/manage_users', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '')
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        action = request.form.get('action')
        
        user = User.query.get_or_404(user_id)
        
        if action == 'make_admin':
            if not user.is_admin:
                user.is_admin = True
                db.session.commit()
                
                notification = Notification(
                    user_id=user.id,
                    title="👑 You're Now an Admin!",
                    message="Congratulations! You have been promoted to administrator. You can now manage users, approve posts, and add resources.",
                    notification_type="success"
                )
                db.session.add(notification)
                db.session.commit()
                
                send_notification_email(
                    user,
                    "Admin Promotion",
                    "Congratulations! You have been promoted to administrator. You can now manage users, approve posts, and add resources. Visit the admin dashboard to get started."
                )
                
                flash(f' {user.name} is now an admin', 'success')
        
        elif action == 'remove_admin':
            if user.is_admin and user.id != current_user.id:
                user.is_admin = False
                db.session.commit()
                
                notification = Notification(
                    user_id=user.id,
                    title="Admin Rights Removed",
                    message="Your admin rights have been removed.",
                    notification_type="warning"
                )
                db.session.add(notification)
                db.session.commit()
                
                flash(f'❌ {user.name} is no longer an admin', 'info')
            elif user.id == current_user.id:
                flash('⚠️ You cannot remove your own admin rights', 'warning')
        
        elif action == 'delete_user':
            if user.id != current_user.id:
                db.session.delete(user)
                db.session.commit()
                flash(f'🗑️ User {user.name} has been deleted', 'info')
            else:
                flash('⚠️ You cannot delete your own account', 'warning')
        
        return redirect(url_for('admin.manage_users', page=page, search=search_query))
    
    # Search users
    if search_query:
        users = User.query.filter(
            (User.name.ilike(f'%{search_query}%')) | 
            (User.email.ilike(f'%{search_query}%'))
        ).paginate(page=page, per_page=10)
    else:
        users = User.query.paginate(page=page, per_page=10)
    
    return render_template('manage_users.html', users=users, search_query=search_query)

@admin_bp.route('/add_resources', methods=['GET', 'POST'])
@login_required
@admin_required
def add_resources():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        resource_url = request.form.get('resource_url')
        resource_type = request.form.get('resource_type')
        disability_id = request.form.get('disability_id')
        
        if not title or not description or not resource_url or not resource_type:
            flash('❌ All fields are required', 'danger')
            return redirect(url_for('admin.add_resources'))
        
        resource = Resource(
            title=title,
            description=description,
            resource_url=resource_url,
            resource_type=resource_type,
            disability_id=disability_id if disability_id else None,
            created_by_id=current_user.id
        )
        
        db.session.add(resource)
        db.session.commit()
        
        flash(f'✅ Resource "{title}" added successfully!', 'success')
        return redirect(url_for('admin.view_resources'))
    
    disabilities = DisabilityCategory.query.all()
    return render_template('add_resources.html', disabilities=disabilities)

@admin_bp.route('/resources', methods=['GET', 'POST'])
@login_required
@admin_required
def view_resources():
    page = request.args.get('page', 1, type=int)
    
    if request.method == 'POST':
        resource_id = request.form.get('resource_id')
        action = request.form.get('action')
        
        resource = Resource.query.get_or_404(resource_id)
        
        if action == 'delete':
            db.session.delete(resource)
            db.session.commit()
            flash(f'🗑️ Resource "{resource.title}" deleted', 'info')
        
        return redirect(url_for('admin.view_resources', page=page))
    
    resources = Resource.query.paginate(page=page, per_page=10)
    return render_template('view_resources.html', resources=resources)

@admin_bp.route('/notifications', methods=['GET', 'POST'])
@login_required
@admin_required
def view_notifications():
    page = request.args.get('page', 1, type=int)
    
    if request.method == 'POST':
        notification_id = request.form.get('notification_id')
        notification = Notification.query.get_or_404(notification_id)
        db.session.delete(notification)
        db.session.commit()
        flash('✅ Notification deleted', 'success')
        return redirect(url_for('admin.view_notifications', page=page))
    
    notifications = Notification.query.order_by(Notification.created_at.desc()).paginate(page=page, per_page=15)
    return render_template('admin_notifications.html', notifications=notifications)

@admin_bp.route('/send_notification', methods=['GET', 'POST'])
@login_required
@admin_required
def send_notification():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        title = request.form.get('title')
        message = request.form.get('message')
        notification_type = request.form.get('notification_type', 'info')
        send_email = request.form.get('send_email') == 'on'
        
        if user_id == 'all':
            users = User.query.all()
        else:
            users = [User.query.get_or_404(user_id)]
        
        for user in users:
            notification = Notification(
                user_id=user.id,
                title=title,
                message=message,
                notification_type=notification_type
            )
            db.session.add(notification)
            
            if send_email:
                send_notification_email(user, title, message, notification_type)
        
        db.session.commit()
        flash(f'✅ Notification sent to {len(users)} user(s)', 'success')
        return redirect(url_for('admin.send_notification'))
    
    users = User.query.all()
    return render_template('send_notification.html', users=users)

@admin_bp.route('/api/user-stats')
@login_required
@admin_required
def api_user_stats():
    """API endpoint for user statistics"""
    users_by_county = db.session.query(User.county, db.func.count(User.id)).group_by(User.county).all()
    users_by_month = db.session.query(
        db.func.strftime('%Y-%m', User.created_at),
        db.func.count(User.id)
    ).group_by(db.func.strftime('%Y-%m', User.created_at)).all()
    
    return jsonify({
        'by_county': dict(users_by_county),
        'by_month': dict(users_by_month)
    })