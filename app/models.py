from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import secrets

# Many-to-Many relationship for child disabilities
child_disabilities = db.Table(
    'child_disabilities',
    db.Column('child_id', db.Integer, db.ForeignKey('child.id'), primary_key=True),
    db.Column('disability_id', db.Integer, db.ForeignKey('disability_category.id'), primary_key=True)
)

# Many-to-Many relationship for group members
group_members = db.Table(
    'group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('group_id', db.Integer, db.ForeignKey('support_group.id'), primary_key=True)
)

class DisabilityCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)  # e.g., ASD, VI

    # Back-reference to children
    children = db.relationship('Child', secondary=child_disabilities, back_populates='disabilities')
    # Support groups for this disability
    support_groups = db.relationship('SupportGroup', back_populates='disability')

    def __repr__(self):
        return f'<Disability {self.name}>'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100))
    county = db.Column(db.String(50))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    password_reset_token = db.Column(db.String(256), nullable=True)
    password_reset_expiration = db.Column(db.DateTime, nullable=True)

    # Relationship to children
    children = db.relationship('Child', back_populates='parent', cascade="all, delete-orphan")
    # Relationship to support groups
    groups = db.relationship('SupportGroup', secondary=group_members, back_populates='members')
    # Messages posted by user
    messages = db.relationship('GroupMessage', back_populates='author', cascade="all, delete-orphan")
    # Stories posted by user
    stories = db.relationship('Story', back_populates='author', cascade="all, delete-orphan")
    # Notifications for user
    notifications = db.relationship('Notification', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_password_reset_token(self):
        """Generate a password reset token"""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_expiration = datetime.utcnow() + timedelta(hours=24)
        return self.password_reset_token
    
    def verify_password_reset_token(self, token):
        """Verify if the password reset token is valid"""
        if self.password_reset_token != token:
            return False
        if self.password_reset_expiration < datetime.utcnow():
            return False
        return True
    
    def clear_password_reset_token(self):
        """Clear the password reset token after use"""
        self.password_reset_token = None
        self.password_reset_expiration = None

class Child(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parent = db.relationship('User', back_populates='children')

    disabilities = db.relationship('DisabilityCategory', secondary=child_disabilities, back_populates='children')

    def __repr__(self):
        return f'<Child {self.name}, Age {self.age}>'

class SupportGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disability_id = db.Column(db.Integer, db.ForeignKey('disability_category.id'), nullable=False)
    disability = db.relationship('DisabilityCategory', back_populates='support_groups')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('User', secondary=group_members, back_populates='groups')
    messages = db.relationship('GroupMessage', back_populates='group', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<SupportGroup {self.disability.name}>'

class GroupMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    file_name = db.Column(db.String(255), nullable=True)  # Original filename
    file_path = db.Column(db.String(500), nullable=True)  # Relative path in uploads
    file_type = db.Column(db.String(50), nullable=True)   # File MIME type
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('support_group.id'), nullable=False)
    
    # Relationships
    author = db.relationship('User', back_populates='messages')
    group = db.relationship('SupportGroup', back_populates='messages')
    
    def __repr__(self):
        return f'<Message by {self.author.name} at {self.created_at}>'

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f'<Event {self.title} on {self.date}>'

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=False)  # For moderation
    rejected_reason = db.Column(db.Text, nullable=True)  # Reason for rejection
    status = db.Column(db.String(20), default="pending")  
# values can be "pending", "approved", "rejected"

    
    # Relationships
    author = db.relationship('User', back_populates='stories')
    
    def __repr__(self):
        return f'<Story {self.title} by {self.author.name if not self.is_anonymous else "Anonymous"}>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default='info')  # 'info', 'warning', 'success', 'error'
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='notifications')
    
    def __repr__(self):
        return f'<Notification {self.title} for user {self.user_id}>'

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    resource_url = db.Column(db.String(500), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)  # e.g., 'link', 'pdf', 'video', 'guide'
    disability_id = db.Column(db.Integer, db.ForeignKey('disability_category.id'), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    disability = db.relationship('DisabilityCategory', foreign_keys=[disability_id])
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    
    def __repr__(self):
        return f'<Resource {self.title}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
