from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.orders import router as orders_router
from app.webhooks import router as webhooks_router
from app.schemas import CarOrderCreate, SponsorOrderCreate, VendorOrderCreate
from app.paypal import create_paypal_order
from app.supabase import insert_customer, insert_order
import os

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://registration-payment-form-c98899p8p-cramos2003s-projects.vercel.app",
        "https://registration-payment-form.vercel.app", # vite dev server
        "http://localhost:5173" # local dev
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
def health_check():
    return {"status":"ok"}

app.include_router(orders_router)
app.include_router(webhooks_router)