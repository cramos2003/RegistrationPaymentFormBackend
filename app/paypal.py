import os
import base64
import httpx
from dotenv import load_dotenv
load_dotenv()

PAYPAL_BASE_URL = os.getenv("PAYPAL_BASE_URL")
CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
SECRET = os.getenv("PAYPAL_SECRET")

async def get_access_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PAYPAL_BASE_URL}/v1/oauth2/token",
            auth=(CLIENT_ID, SECRET),
            data={"grant_type": "client_credentials"}
        )
            
    response.raise_for_status()
    return response.json()["access_token"]
    
def get_auth_header():
    auth = f"{CLIENT_ID}:{SECRET}"
    encode = base64.b64encode(auth.encode()).decode()
    return {"Authorization": f"Basic {encode}"}

async def create_paypal_order(amount: str):
    token = await get_access_token()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PAYPAL_BASE_URL}/v2/checkout/orders",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json={
                "intent": "CAPTURE",
                "purchase_units": [
                    {"amount": {"currency_code": "USD", "value": amount}}
                ],
            },
        )
    response.raise_for_status()
    return response.json()

async def capture_paypal_order(order_id: str):
    token = await get_access_token()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        response.raise_for_status()
        return response.json()
    
async def verify_webhook(headers: dict, body: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PAYPAL_BASE_URL}/v1/notifications/verify-webhook-signature",
            headers={
                **get_auth_header(),
                "Content-Type": "application/json",
            },
            json={
                "auth_algo": headers.get("paypal-auth-algo"),
                "cert_url": headers.get("paypal-cert-url"),
                "transmission_id": headers.get("paypal-transmission-id"),
                "transmission_sig": headers.get("paypal-transmission-sig"),
                "transmission_time": headers.get("paypal-transmission-time"),
                "webhook_id": os.getenv("PAYPAL_WEBHOOK_ID", "").strip(),
                "webhook_event": body,
            },
        )
        response.raise_for_status()
        return response.json()