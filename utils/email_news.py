import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from gmail_api import sender_email, smtp_server, smtp_port, smtp_user, smtp_password

def build_email_body(articles, mode):
    if mode == "law":
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .article { margin-bottom: 25px; }
                .title { font-size: 16px; font-weight: bold; }
                .published { font-size: 12px; color: gray; }
                .summary { margin-top: 5px; }
            </style>
        </head>
        <body>
            <h2>📰 Weekly Employment and Labor Law News Summary</h2>
        """
    else:
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .article { margin-bottom: 25px; }
                .title { font-size: 16px; font-weight: bold; }
                .published { font-size: 12px; color: gray; }
                .summary { margin-top: 5px; }
            </style>
        </head>
        <body>
            <h2>📰 Daily News Summary</h2>
        """

    for article in articles:
        html += f"""
        <div class="article">
            <div class="title"><a href="{article['link']}" target="_blank">{article['title']}</a></div>
            <div class="published">{article['published']}</div>
            <div class="summary">{article['summary']}</div>
        </div>
        """

    html += "</body></html>"
    return html

def send_email(html_content, receiver_email, mode):
    if mode == "law":
        subject = "Weekly Employment and Labor Law News Summary"
    else:
        subject = "Daily News Summary"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    part = MIMEText(html_content, "html")
    msg.attach(part)

    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
        server.login(smtp_user, smtp_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())