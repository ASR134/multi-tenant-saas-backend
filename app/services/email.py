import resend # resend python sdk

from app.core.config import settings


class EmailService:

    def __init__(self):
        resend.api_key = settings.resend_api_key


    async def send_verification_email(
            self,
            email : str,
            verification_token : str,
    ):
        verification_url = f"{settings.frontend_url}/verify-email?token={verification_token}"

        params : resend.Emails.SendParams = {
            "from": settings.email_from,
            "to": [email],# list for mulitple recipients
            "subject": "Verify your email",
            "html": f"""
                <h2>Verify your email</h2>

                <p>
                    Thanks for signing up.
                    Please verify your email address by clicking the button below.
                </p>

                <p>
                    <a href="{verification_url}">
                        Verify Email
                    </a>
                </p>

                <p>
                    This verification link will expire in few minutes.
                </p>
            """,
        }

        return await resend.Emails.send_async(params) # returns response from resend's api


    async def send_password_reset_email(
            self,
            email : str,
            reset_token : str,
    ):
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"

        params: resend.Emails.SendParams = {
            "from": settings.email_from,
            "to": [email],
            "subject": "Reset your password",
            "html": f"""
                <h2>Reset your password</h2>

                <p>
                    We received a request to reset your password.
                </p>

                <p>
                    <a href="{reset_url}">
                        Reset Password
                    </a>
                </p>

                <p>
                    This link will expire in few
                    minutes.
                </p>

                <p>
                    If you did not request a password reset,
                    you can safely ignore this email.
                </p>
            """,
        }

        return await resend.Emails.send_async(params)