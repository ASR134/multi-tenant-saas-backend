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

        # return await resend.Emails.send_async(params) # returns response from resend's api
        response = await resend.Emails.send_async(params)

        print("RESEND RESPONSE:", response)

        return response