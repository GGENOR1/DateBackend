import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


async def send_confirmation_email(receiver_email, confirmation_code):
    print(f"Почта для отправки {receiver_email}")
    print(f"Код {confirmation_code}")

    smtp_server = "smtp.gmail.com"
    port = 587  # используйте порт 465 для SSL

    email = "example@gmail.com"
    password = "example"

    # Создаем MIME сообщение
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = receiver_email
    msg['Subject'] = 'Код подтверждения'

    # Добавляем тело письма
    body = f' Код подтверждения {confirmation_code}'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # обновляем соединение с использованием TLS-шифрования
        server.login(email, password)

        # Отправка письма
        text = msg.as_string()
        server.sendmail(email, receiver_email, text)
        return True
    except Exception as _ex:
        print(_ex)
        return False
    finally:
        server.quit()  # закрываем соединение
    
async def generate_confirmation_code():
    return f"{random.randint(100000, 999999)}"


