import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = os.getenv("FROM_NAME", "VideoHook")
        
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email notification
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (optional)
            
        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.smtp_username or not self.smtp_password:
            print(f"[Email] Email not configured. Would send to {to_email}: {subject}")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            print(f"[Email] Successfully sent email to {to_email}")
            return True
            
        except Exception as e:
            print(f"[Email] Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_video_posted_notification(
        self,
        to_email: Optional[str] = None,
        username: str = "User",
        platform: str = "social media",
        post_url: Optional[str] = None,
        video_url: Optional[str] = None,
        caption: Optional[str] = None
    ) -> bool:
        """
        Send notification email when video is posted to social media
        
        Args:
            to_email: User's email address
            username: User's username
            platform: Social media platform name
            post_url: URL to the posted content
            video_url: URL to the video file
            caption: Post caption
            
        Returns:
            True if email sent successfully, False otherwise
        """
        platform_names = {
            "instagram": "Instagram",
            "linkedin": "LinkedIn",
            "x": "X (Twitter)",
            "tiktok": "TikTok"
        }
        
        platform_display = platform_names.get(platform.lower(), platform.capitalize())
        
        # Always send to nagurivindapalli@gmail.com for now
        to_email = "nagurivindapalli@gmail.com"
        
        subject = f"🎬 Your video has been posted to {platform_display}!"
        
        # HTML email template
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9fafb;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #6b7280;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎬 Video Posted Successfully!</h1>
            </div>
            <div class="content">
                <p>Hi {username},</p>
                
                <p>Great news! Your video has been successfully posted to <strong>{platform_display}</strong>.</p>
                
                {f'<p><strong>Caption:</strong> {caption[:200]}{"..." if caption and len(caption) > 200 else ""}</p>' if caption else ''}
                
                {f'<p><a href="{post_url}" class="button">View Post on {platform_display}</a></p>' if post_url else ''}
                
                {f'<p><a href="{video_url}" class="button" style="background: #10b981;">Download Video</a></p>' if video_url else ''}
                
                <p>Thank you for using VideoHook!</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from VideoHook.</p>
                <p>You can manage your email preferences in your account settings.</p>
            </div>
        </body>
        </html>
        """
        
        # Plain text version
        text_content = f"""
        Hi {username},
        
        Great news! Your video has been successfully posted to {platform_display}.
        
        {f'Caption: {caption}' if caption else ''}
        
        {f'View your post: {post_url}' if post_url else ''}
        {f'Download video: {video_url}' if video_url else ''}
        
        Thank you for using VideoHook!
        """
        
        return self.send_email(to_email, subject, html_content, text_content)


