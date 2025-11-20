import yookassa
from yookassa import Payment, Configuration
import uuid
import logging

logger = logging.getLogger(__name__)

# Настройка ЮKassa (ТЕСТОВЫЕ КЛЮЧИ)
YOOKASSA_SHOP_ID = "WID1Xwp2NqxOeQ82EEEvsDhLI_dEcEGKeLrxr3qTKLk"
YOOKASSA_API_KEY = "test_WID1Xwp2NqxOeQ82EEEvsDhLI_dEcEGKeLrxr3qTKLk"

# Инициализация ЮKassa
Configuration.configure(YOOKASSA_SHOP_ID, YOOKASSA_API_KEY)

async def create_yookassa_payment(amount: float, user_id: int, description: str = "Пополнение баланса VPN"):
    """Создание платежа в ЮKassa"""
    try:
        idempotence_key = str(uuid.uuid4())
        
        payment = Payment.create({
            "amount": {
                "value": f"{amount:.2f}",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/your_bot"  # URL для возврата после оплаты
            },
            "capture": True,
            "description": f"{description} (User: {user_id})",
            "metadata": {
                "user_id": user_id
            }
        }, idempotence_key)
        
        logger.info(f"Создан платеж {payment.id} для пользователя {user_id}")
        
        return {
            "payment_id": payment.id,
            "confirmation_token": payment.confirmation.confirmation_token,
            "confirmation_url": payment.confirmation.confirmation_url
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания платежа: {e}")
        return None

async def check_payment_status(payment_id: str):
    """Проверить статус платежа"""
    try:
        payment = Payment.find_one(payment_id)
        return payment.status
    except Exception as e:
        logger.error(f"Ошибка проверки статуса платежа: {e}")
        return "unknown"
