import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


async def send_confirmation_email(receiver_email, confirmation_code):
    print(f"Почта для отправки {receiver_email}")
    print(f"Код {confirmation_code}")

    smtp_server = "smtp.gmail.com"
    port = 587  # используйте порт 465 для SSL

    email = "rustke97@gmail.com"
    password = "xeam gftx whid lpry"

    # Создаем MIME сообщение
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = receiver_email
    msg['Subject'] = 'САЛАМ АЛЛЕКЙКУМ'

    # Добавляем тело письма
    body = f' РАЗМЕР ТВОЕГО ЧЛЕНА РАВЕН {confirmation_code} СМ'
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

# Пример использован
    
    
#     from_email = email
#     to_email = "recipient_email@example.com"
#     subject = "Тестовое сообщение"
#     message = "Привет, это тестовое сообщение, отправленное с помощью Python и SMTP."
    
#     server.sendmail(from_email, to_email, f"Subject: {subject}\n\n{message}")
    
#     # Создание сообщения
#     msg = MIMEMultipart()
#     msg['From'] = smtp_username
#     msg['To'] = receiver_email
#     msg['Subject'] = 'Confirmation Code'

#     # Текст сообщения с кодом подтверждения
#     message = f'Your confirmation code is: {confirmation_code}'
#     msg.attach(MIMEText(message, 'plain'))

#     # Отправка письма через SMTP сервер
#     with smtplib.SMTP(smtp_host, smtp_port) as server:
#         server.starttls()
#         server.login(smtp_username, smtp_password)
#         server.sendmail(smtp_username, receiver_email, msg.as_string())

# # Пример использования
# send_confirmation_email('recipient_email@example.com', '123456')
