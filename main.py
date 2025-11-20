from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from payments import create_yookassa_payment, check_payment_status
from database import init_db, get_user_balance, update_user_balance

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="VPN Service API")

# CORS для Telegram Mini App
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация БД при старте
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("✅ Бэкенд запущен")

# ================== API РОУТЫ ==================

@app.get("/")
async def root():
    return {"message": "VPN Service API", "status": "running"}

@app.get("/api/user/{user_id}/balance")
async def get_balance(user_id: int):
    """Получить баланс пользователя"""
    try:
        balance = get_user_balance(user_id)
        return {"user_id": user_id, "balance": balance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/payment/create")
async def create_payment(user_id: int, amount: float):
    """Создать платеж в ЮKassa"""
    try:
        if amount < 10:
            raise HTTPException(status_code=400, detail="Минимальная сумма 10 рублей")
        
        payment_data = await create_yookassa_payment(amount, user_id)
        
        if not payment_data:
            raise HTTPException(status_code=500, detail="Ошибка создания платежа")
        
        return {
            "success": True,
            "payment_id": payment_data["payment_id"],
            "confirmation_token": payment_data["confirmation_token"],
            "amount": amount
        }
        
    except Exception as e:
        logger.error(f"Ошибка создания платежа: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/payment/status/{payment_id}")
async def payment_status(payment_id: str):
    """Проверить статус платежа"""
    try:
        status = await check_payment_status(payment_id)
        return {"payment_id": payment_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/payment/confirm")
async def confirm_payment(payment_id: str):
    """Подтвердить успешный платеж и пополнить баланс"""
    try:
        status = await check_payment_status(payment_id)
        
        if status == "succeeded":
            # Здесь должна быть логика получения user_id из платежа
            # и обновления баланса
            user_id = 1  # Временная заглушка
            amount = 100  # Временная заглушка
            
            update_user_balance(user_id, amount)
            
            return {
                "success": True,
                "message": "Платеж подтвержден",
                "new_balance": get_user_balance(user_id)
            }
        else:
            return {
                "success": False,
                "status": status,
                "message": "Платеж не завершен"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
