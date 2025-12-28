import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase environment variables not set")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

async def insert_car(data: dict):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{SUPABASE_URL}/rest/v1/cars",
            headers=HEADERS,
            json=data
        )
        # res.raise_for_status()
        return res.json()

async def insert_customer(data: dict):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{SUPABASE_URL}/rest/v1/customers",
            headers=HEADERS,
            json=data,
        )
        # res.raise_for_status()
        return res.json()
    
async def insert_order(data: dict):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{SUPABASE_URL}/rest/v1/orders",
            headers=HEADERS,
            json=data,
        )
        # res.raise_for_status()
        return res.json()
    
async def insert_payment(data: dict):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{SUPABASE_URL}/rest/v1/payments",
            headers=HEADERS,
            json=data,
        )
        # res.raise_for_status()
        return res.json()
    
async def insert_sponsor(data: dict):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{SUPABASE_URL}/rest/v1/sponsors",
            headers=HEADERS,
            json=data
        )
        # res.raise_for_status()
        return res.json()
    
async def insert_vendor(data: dict):
    async with httpx.AsyncClient() as client: 
        res = await client.post(
            f"{SUPABASE_URL}/rest/v1/vendors",
            headers=HEADERS,
            json=data
        )
        # res.raise_for_status()
        return res.json()
    
async def update_order_status(paypal_order_id: str, status: str):
    async with httpx.AsyncClient() as client:
        res = await client.patch(
            f"{SUPABASE_URL}/rest/v1/orders",
            headers=HEADERS,
            params={"paypal_order_id": f"eq.{paypal_order_id}"},
            json={"status": status},
        )
        # res.raise_for_status()
        return res.json()

async def get_order_by_paypal_id(paypal_order_id: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{SUPABASE_URL}/rest/v1/orders",
            headers=HEADERS,
            params={"paypal_order_id": f"eq.{paypal_order_id}"}
        )
        # res.raise_for_status()
        return res.json()

async def payment_exists(paypal_capture_id: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{SUPABASE_URL}/rest/v1/payments",
            headers=HEADERS,
            params={"paypal_capture_id": f"eq.{paypal_capture_id}"}
        )
        return len(res.json()) > 0