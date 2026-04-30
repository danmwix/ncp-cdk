from flask_mail import Mail, Message
from flask import render_template_string, current_app, url_for
import os

mail = Mail()

def send_password_reset_email(user):
    """Send password reset email to user"""
    try:
        token = user.generate_password_reset_token()
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        subject = "🔐 Password Reset Request - NCP-CDK Kenya"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #e76f51; text-align: center;">Password Reset Request</h2>
                    
                    <p>Dear {user.name},</p>
                    
                    <p>We received a request to reset your password for your NCP-CDK Kenya account. If you didn't make this request, please ignore this email.</p>
                    
                    <p>To reset your password, click the link below (valid for 24 hours):</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" style="background: #e76f51; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            Reset Password
                        </a>
                    </div>
                    
                    <p>Or copy and paste this link in your browser:</p>
                    <p style="background: #f0f0f0; padding: 10px; word-break: break-all; border-radius: 5px;">
                        {reset_url}
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #666;">
                        This is an automated email. Please don't reply directly to this email. If you need further assistance, please contact our support team.
                    </p>
                    
                    <p style="font-size: 12px; color: #666;">
                        Best regards,<br>
                        NCP-CDK Kenya Team
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False

def send_notification_email(user, title, message, notification_type='info'):
    """Send notification email to user"""
    try:
        subject = f"📬 {title} - NCP-CDK Kenya"
        
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h2 style="color: #e76f51; text-align: center;">Notification</h2>
                    
                    <p>Dear {user.name},</p>
                    
                    <p>{message}</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{url_for('main.home', _external=True)}" style="background: #2a9d8f; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">
                            View Details
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #666;">
                        This is an automated notification from NCP-CDK Kenya. Please don't reply directly to this email.
                    </p>
                </div>
            </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body
        )
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending notification email: {str(e)}")
        return False
