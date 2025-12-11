"""
Email service using Resend API
"""

import os
from typing import Optional
import requests
from app.core.config import settings


class EmailService:
    """Email service for sending emails via Resend"""

    def __init__(self):
        self.api_key = os.getenv("RESEND_API_KEY")
        self.api_url = "https://api.resend.com/emails"
        self.from_email = os.getenv("FROM_EMAIL", "noreply@friction.app")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> dict:
        """
        Send an email using Resend API

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)

        Returns:
            dict: Response from Resend API
        """
        if not self.api_key:
            raise ValueError("RESEND_API_KEY environment variable not set")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": self.from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_content
        }

        if text_content:
            payload["text"] = text_content

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to send email: {str(e)}")

    def send_verification_email(self, to_email: str, verification_token: str, user_name: str) -> dict:
        """
        Send email verification link to user

        Args:
            to_email: User's email address
            verification_token: Unique verification token
            user_name: User's name

        Returns:
            dict: Response from Resend API
        """
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        verification_link = f"{frontend_url}/verify-email?token={verification_token}"

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
                    background: linear-gradient(135deg, #D97757 0%, #C96646 100%);
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    background: #ffffff;
                    padding: 40px 30px;
                    border: 1px solid #E8E4DF;
                    border-top: none;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 32px;
                    background: #D97757;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-weight: 600;
                }}
                .button:hover {{
                    background: #C96646;
                }}
                .footer {{
                    background: #F5F3EF;
                    padding: 20px 30px;
                    text-align: center;
                    font-size: 12px;
                    color: #6B6560;
                    border-radius: 0 0 10px 10px;
                }}
                .token {{
                    background: #F0EDE8;
                    padding: 10px;
                    border-radius: 6px;
                    font-family: monospace;
                    word-break: break-all;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚡ Friction</h1>
            </div>
            <div class="content">
                <h2>Welcome, {user_name}!</h2>
                <p>Thanks for signing up for Friction. We're excited to have you on board!</p>
                <p>To complete your registration and start discovering opportunities, please verify your email address by clicking the button below:</p>

                <div style="text-align: center;">
                    <a href="{verification_link}" class="button">Verify Email Address</a>
                </div>

                <p>Or copy and paste this link into your browser:</p>
                <div class="token">{verification_link}</div>

                <p>This verification link will expire in 24 hours.</p>

                <p>If you didn't create an account with Friction, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2024 Friction. All rights reserved.</p>
                <p>This is an automated message, please do not reply.</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Welcome to Friction, {user_name}!

        Thanks for signing up. To complete your registration, please verify your email address by visiting:

        {verification_link}

        This verification link will expire in 24 hours.

        If you didn't create an account with Friction, you can safely ignore this email.

        © 2024 Friction
        """

        return self.send_email(
            to_email=to_email,
            subject="Verify your email address - Friction",
            html_content=html_content,
            text_content=text_content
        )

    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str) -> dict:
        """
        Send password reset link to user

        Args:
            to_email: User's email address
            reset_token: Unique password reset token
            user_name: User's name

        Returns:
            dict: Response from Resend API
        """
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        reset_link = f"{frontend_url}/reset-password?token={reset_token}"

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
                    background: linear-gradient(135deg, #D97757 0%, #C96646 100%);
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    background: #ffffff;
                    padding: 40px 30px;
                    border: 1px solid #E8E4DF;
                    border-top: none;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 32px;
                    background: #D97757;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-weight: 600;
                }}
                .footer {{
                    background: #F5F3EF;
                    padding: 20px 30px;
                    text-align: center;
                    font-size: 12px;
                    color: #6B6560;
                    border-radius: 0 0 10px 10px;
                }}
                .token {{
                    background: #F0EDE8;
                    padding: 10px;
                    border-radius: 6px;
                    font-family: monospace;
                    word-break: break-all;
                    margin: 15px 0;
                }}
                .warning {{
                    background: #FEE2E2;
                    border-left: 4px solid #DC2626;
                    padding: 12px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚡ Friction</h1>
            </div>
            <div class="content">
                <h2>Password Reset Request</h2>
                <p>Hi {user_name},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>

                <div style="text-align: center;">
                    <a href="{reset_link}" class="button">Reset Password</a>
                </div>

                <p>Or copy and paste this link into your browser:</p>
                <div class="token">{reset_link}</div>

                <p>This password reset link will expire in 1 hour.</p>

                <div class="warning">
                    <strong>⚠️ Important:</strong> If you didn't request a password reset, please ignore this email or contact support if you have concerns about your account security.
                </div>
            </div>
            <div class="footer">
                <p>© 2024 Friction. All rights reserved.</p>
                <p>This is an automated message, please do not reply.</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Password Reset Request - Friction

        Hi {user_name},

        We received a request to reset your password. Visit the link below to create a new password:

        {reset_link}

        This password reset link will expire in 1 hour.

        If you didn't request a password reset, please ignore this email or contact support if you have concerns about your account security.

        © 2024 Friction
        """

        return self.send_email(
            to_email=to_email,
            subject="Reset your password - Friction",
            html_content=html_content,
            text_content=text_content
        )
    def send_notification_email(
        self,
        to_email: str,
        user_name: str,
        notification_title: str,
        notification_message: str,
        notification_link: Optional[str] = None
    ) -> dict:
        """
        Send notification email to user

        Args:
            to_email: User's email address
            user_name: User's name
            notification_title: Notification title
            notification_message: Notification message
            notification_link: Optional link to view notification

        Returns:
            dict: Response from Resend API
        """
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        view_link = f"{frontend_url}{notification_link}" if notification_link else f"{frontend_url}/notifications"

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
                    background: linear-gradient(135deg, #D97757 0%, #C96646 100%);
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    background: #ffffff;
                    padding: 40px 30px;
                    border: 1px solid #E8E4DF;
                    border-top: none;
                }}
                .notification-box {{
                    background: #F0EDE8;
                    border-left: 4px solid #D97757;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .notification-box h3 {{
                    margin-top: 0;
                    color: #D97757;
                }}
                .button {{
                    display: inline-block;
                    padding: 14px 32px;
                    background: #D97757;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    margin: 20px 0;
                    font-weight: 600;
                }}
                .footer {{
                    background: #F5F3EF;
                    padding: 20px 30px;
                    text-align: center;
                    font-size: 12px;
                    color: #6B6560;
                    border-radius: 0 0 10px 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>⚡ Friction</h1>
            </div>
            <div class="content">
                <h2>Hi {user_name}!</h2>
                <p>You have a new notification:</p>

                <div class="notification-box">
                    <h3>{notification_title}</h3>
                    <p>{notification_message}</p>
                </div>

                <div style="text-align: center;">
                    <a href="{view_link}" class="button">View Details</a>
                </div>

                <p style="margin-top: 30px; font-size: 14px; color: #6B6560;">
                    You can manage your notification preferences in your account settings.
                </p>
            </div>
            <div class="footer">
                <p>© 2024 Friction. All rights reserved.</p>
                <p>This is an automated message, please do not reply.</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Hi {user_name}!

        You have a new notification:

        {notification_title}
        {notification_message}

        View details: {view_link}

        You can manage your notification preferences in your account settings.

        © 2024 Friction
        """

        return self.send_email(
            to_email=to_email,
            subject=f"Friction: {notification_title}",
            html_content=html_content,
            text_content=text_content
        )


# Create a global instance
email_service = EmailService()
