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


    async def send_invitation_email(
            self,
            email : str,
            invitation_token : str,
            organization_name : str,
    ):

        invitation_url = f"{settings.frontend_url}/accept-invitation/token={invitation_token}"

        params: resend.Emails.SendParams = {
            "from": settings.email_from,
            "to": [email],
            "subject": f"You're invited to join {organization_name}",
            "html": f"""
                <h2>You're invited to join {organization_name}</h2>

                <p>
                    You have been invited to become a member of
                    <strong>{organization_name}</strong>.
                </p>

                <p>
                    Click the button below to accept the invitation
                    and join the organization.
                </p>

                <p>
                    <a href="{invitation_url}">
                        Accept Invitation
                    </a>
                </p>

                <p>
                    This invitation will expire in a few days.
                </p>

                <p>
                    If you were not expecting this invitation, you can safely
                    ignore this email.
                </p>
            """,
        }

        return await resend.Emails.send_async(params)


    async def send_invitation_accepted_notification(# this is to notify the inviter
            self,
            inviter_email : str,
            invitee_email : str,
            organization_name : str,
    ):
        params: resend.Emails.SendParams = {
            "from": settings.email_from,
            "to": [inviter_email],
            "subject": "Invitation accepted",
            "html": f"""
                <h2>Invitation Accepted</h2>

                <p>
                    <strong>{invitee_email}</strong> has accepted your invitation
                    and joined <strong>{organization_name}</strong>.
                </p>

                <p>
                    They are now a member of your organization.
                </p>
            """,
        }