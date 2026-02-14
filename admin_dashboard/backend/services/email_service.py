"""
Email Service using SMTP
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.settings import settings
from typing import List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailService:
    """SMTP Email Service"""
    
    @staticmethod
    async def send_email(
        to: List[str],
        subject: str,
        body: str,
        html: Optional[str] = None
    ) -> bool:
        """
        Send email via SMTP
        
        Args:
            to: List of recipient emails
            subject: Email subject
            body: Plain text body
            html: Optional HTML body
            
        Returns:
            True if sent successfully
        """
        try:
            message = MIMEMultipart("alternative")
            message["From"] = settings.smtp_from
            message["To"] = ", ".join(to)
            message["Subject"] = subject
            
            # Attach plain text
            message.attach(MIMEText(body, "plain"))
            
            # Attach HTML if provided
            if html:
                message.attach(MIMEText(html, "html"))
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password,
                start_tls=True,
            )
            
            logger.info(f"✅ Email sent to {to}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False
    
    @staticmethod
    def generate_interview_invitation_email(
        candidate_name: str,
        job_title: str,
        company_name: str = "Our Company"
    ) -> tuple[str, str]:
        """
        Generate interview invitation email
        
        Returns:
            Tuple of (plain_text, html)
        """
        subject = f"Interview Invitation - {job_title}"
        
        plain_text = f"""
Dear {candidate_name},

Congratulations! We are pleased to inform you that you have been shortlisted for the position of {job_title} at {company_name}.

We would like to schedule an interview with you. Please reply to this email with your availability for the next week, and we will arrange a suitable time.

Please provide at least 3 time slots when you are available.

Example:
- Monday, 2:00 PM - 4:00 PM
- Wednesday, 10:00 AM - 12:00 PM
- Friday, 3:00 PM - 5:00 PM

We look forward to speaking with you soon!

Best regards,
{company_name} HR Team
        """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; }}
                .footer {{ background: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                ul {{ background: #f9f9f9; padding: 20px 40px; border-left: 4px solid #667eea; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Interview Invitation</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{candidate_name}</strong>,</p>
                    
                    <p>Congratulations! We are pleased to inform you that you have been shortlisted for the position of <strong>{job_title}</strong> at {company_name}.</p>
                    
                    <p>We would like to schedule an interview with you. Please reply to this email with your availability for the next week.</p>
                    
                    <p><strong>Please provide at least 3 time slots when you are available:</strong></p>
                    
                    <ul>
                        <li>Monday, 2:00 PM - 4:00 PM</li>
                        <li>Wednesday, 10:00 AM - 12:00 PM</li>
                        <li>Friday, 3:00 PM - 5:00 PM</li>
                    </ul>
                    
                    <p>We look forward to speaking with you soon!</p>
                    
                    <p>Best regards,<br><strong>{company_name} HR Team</strong></p>
                </div>
                <div class="footer">
                    <p>© 2026 {company_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return plain_text.strip(), html.strip()
    
    @staticmethod
    def generate_interview_confirmation_email(
        candidate_name: str,
        job_title: str,
        interview_time: datetime,
        interview_link: str,
        company_name: str = "Our Company"
    ) -> tuple[str, str]:
        """
        Generate interview confirmation email
        
        Returns:
            Tuple of (plain_text, html)
        """
        time_str = interview_time.strftime("%A, %B %d, %Y at %I:%M %p")
        
        plain_text = f"""
Dear {candidate_name},

Your interview for the position of {job_title} has been scheduled!

Interview Details:
- Date & Time: {time_str}
- Interview Link: {interview_link}

Please make sure you are in a quiet environment with a stable internet connection.

The interview will be conducted by our AI interviewer, and you can start the interview by clicking the link above at the scheduled time.

Good luck!

Best regards,
{company_name} HR Team
        """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; }}
                .info-box {{ background: #f0f4ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
                .button {{ display: inline-block; padding: 15px 40px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .footer {{ background: #f5f5f5; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Interview Confirmed</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{candidate_name}</strong>,</p>
                    
                    <p>Your interview for the position of <strong>{job_title}</strong> has been scheduled!</p>
                    
                    <div class="info-box">
                        <p><strong>📅 Date & Time:</strong><br>{time_str}</p>
                        <p><strong>🔗 Interview Link:</strong><br><a href="{interview_link}">{interview_link}</a></p>
                    </div>
                    
                    <center>
                        <a href="{interview_link}" class="button">Join Interview</a>
                    </center>
                    
                    <p><strong>Important Notes:</strong></p>
                    <ul>
                        <li>Please be in a quiet environment</li>
                        <li>Ensure stable internet connection</li>
                        <li>Test your microphone and speakers beforehand</li>
                        <li>The interview will be conducted by our AI interviewer</li>
                    </ul>
                    
                    <p>Good luck!</p>
                    
                    <p>Best regards,<br><strong>{company_name} HR Team</strong></p>
                </div>
                <div class="footer">
                    <p>© 2026 {company_name}. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return plain_text.strip(), html.strip()


email_service = EmailService()
