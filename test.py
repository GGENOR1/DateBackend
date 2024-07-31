import asyncio
import httpx
from datetime import datetime

async def send_email_requests():
    url = "http://localhost:8000/auth/send_verify-email_to_registr"  # Замените на ваш фактический URL эндпоинта
    async with httpx.AsyncClient() as client:
        for i in range(700):
            email = f"cistakov966@gmail.com"  # Обновил адреса, чтобы не было повторов
            json_data = {
                "email": email,
                "password": "testpassword",
                "username": f"test",
                "registered_at": datetime.now().isoformat(),
                "role_id": 1  # Замените на соответствующий идентификатор роли
            }
            response = await client.post(url, json=json_data)
            print(response.status_code, response.json())

asyncio.run(send_email_requests())
