import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")


def send_email(to: str, subject: str, activation_link: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to

    # plain text fallback
    msg.set_content(f"Перейдіть за посиланням для активації акаунта: {activation_link}")

    # HTML version
    msg.add_alternative(get_html_template(activation_link), subtype="html")

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            print(f"✅ Email sent to {to}")
    except Exception as e:
        print(f"❌ Failed to send email to {to}: {e}")


def get_html_template(activation_link: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Підтвердження акаунта</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #f4f4f7;
          color: #333;
          margin: 0;
          padding: 0;
        }}
        .container {{
          max-width: 600px;
          margin: 40px auto;
          background-color: #fff;
          border-radius: 10px;
          padding: 30px;
          box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        .logo {{
          text-align: center;
          margin-bottom: 30px;
        }}
        .logo h1 {{
          margin: 0;
          color: #4f46e5;
          font-size: 24px;
        }}
        h2 {{
          color: #111827;
        }}
        p {{
          line-height: 1.6;
        }}
        .button {{
          display: inline-block;
          background-color: black;
          color: white;
          padding: 12px 24px;
          text-decoration: none;
          border-radius: 6px;
          font-weight: bold;
          margin-top: 20px;
        }}
        .footer {{
          margin-top: 40px;
          font-size: 12px;
          text-align: center;
          color: #888;
        }}
        @media (prefers-color-scheme: dark) {{
          body {{
            background-color: #1f2937;
            color: #f9fafb;
          }}
          .container {{
            background-color: #111827;
            box-shadow: none;
          }}
          h2 {{
            color: #fff;
          }}
          .footer {{
            color: #aaa;
          }}
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="logo">
          <h1>I AM WEB MUSIC 🎵</h1>
        </div>
        <h2>Account activation</h2>
        <p>Hello! 👋</p>
        <p>Thanks for signing in <strong>I AM WEB MUSIC</strong>.</p>
        <p>To activate your account press the button below:</p>
        <a href="{activation_link}" class="button">Activate account</a>
        <div class="footer">
          &copy; 2025 I AM WEB MUSIC. Усі права захищено.
        </div>
      </div>
    </body>
    </html>
    """

def get_password_reset_template(link: str) -> str:
    return f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>Reset your password</h2>
        <p>Click the button below to reset your password:</p>
        <a href="{link}" style="display:inline-block;padding:10px 20px;background:#4f46e5;color:white;text-decoration:none;border-radius:5px;">Reset Password</a>
        <p>If you didn’t request this, just ignore this email.</p>
      </body>
    </html>
    """