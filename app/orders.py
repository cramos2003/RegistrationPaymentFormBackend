from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import os

from app.schemas import CarOrderCreate, SponsorOrderCreate, VendorOrderCreate
from app.paypal import create_paypal_order
from app.supabase import insert_customer, insert_order,insert_car, insert_sponsor, insert_vendor
from app.paypal import capture_paypal_order

load_dotenv()

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/capture/{order_id}")
async def capture_order(order_id: str):
    capture_result = await capture_paypal_order(order_id)
    return capture_result

@router.post("/create")
async def create_order(order: CarOrderCreate | SponsorOrderCreate | VendorOrderCreate):
    # SERVER CONTROLED PRICING
    # SCHEMA IDENTIFIER FOR DETERMINING PRICE OF FORM
    orderType = type(order)
    
    # - CarOrderCreate = $35
    if(CarOrderCreate == orderType):
        amount = os.getenv("CAR_PARTICIPANT_PAYMENT")
    # - SponsorOrderCreate = $250
    elif(SponsorOrderCreate == (orderType)):
        amount = os.getenv("SPONSOR_PAYMENT")
    # - VENDORORDERCREATE = $75 (small merch) | $140 (large merch) | $225 (food)
    elif(VendorOrderCreate == orderType):
        # CHECK IF SMALL MERCH VENDOR
        if(order.vendorType == "MV" and order.vendorSize == "10"):
            amount = os.getenv("MERCH_VENDOR_PAYMENT")
        # CHECK IF LARGER MERCH VENDOR
        elif(order.vendorType == "MV" and order.vendorSize == "20"):
            amount = os.getenv("LARGE_MERCH_VENDOR_PAYMENT")
        # CHECK IF EXTRA LARGE MERCH VENDOR
        elif(order.vendorType == "MV" and order.vendorSize == "30"):
            amount = os.getenv("EXTRA_LARGE_MERCH_VENDOR_PAYMENT")
        elif(order.vendorType == "FT" or order.vendorType == "FP"):
            amount = os.getenv("FOOD_VENDOR_PAYMENT")
            
    # IF NO AMOUNT RECEIVED
    if not amount:
        raise HTTPException(status_code=500, detail="Payment amount not configured")
    
    # SAVE CUSTOMER AND FORM DATA BASED ON SCHEMA
    if(CarOrderCreate == orderType):
        # DOESN'T CONTAIN company DATA
        customer = await insert_customer({
            "firstname": order.firstName,
            "lastname": order.lastName,
            "email": order.email,
            "phone": order.phone,
            "company": "",
            "address": order.address,
            "city": order.city,
            "state": order.state,
            "zip": order.zip,
            "customertype": "CAR" # INDICATES TYPE OF CUSTOMER
        })
        
        # INSERT INTO CARS TABLE
        car = await insert_car({
            "customer_id": customer[0]["id"],
            "carmake": order.carMake,
            "carmodel": order.carModel,
            "caryear": order.year
        })
        
    elif(SponsorOrderCreate == orderType):
        # INSERT INTO CUSTOMER TABLE
        customer = await insert_customer({
            "firstname": order.firstName,
            "lastname": order.lastName,
            "email": order.email,
            "phone": order.phone,
            "company": order.company,
            "address": order.address,
            "city": order.city,
            "state": order.state,
            "zip": order.zip,
            "customertype": "SPONSOR" # INDICATES TYPE OF CUSTOMER
        })       
         
        # INSERT INTO SPONSORS TABLE
        sponsor = await insert_sponsor({
            "customer_id": customer[0]["id"]
        })
        
    elif(VendorOrderCreate == orderType):
        # GET VENDOR TYPE
        if(order.vendorType == "MV"):
            vType = "MERCH"
        elif(order.vendorType == "FT" or order.vendorType == "FP"):
            vType = "FOOD"

        # INSERT INTO CUSTOMERS TABLE
        customer = await insert_customer({
            "firstname": order.firstName,
            "lastname": order.lastName,
            "email": order.email,
            "phone": order.phone,
            "company": order.company,
            "address": order.address,
            "city": order.city,
            "state": order.state,
            "zip": order.zip,
            "customertype": vType # INDICATES TYPE OF CUSTOMER
        })
        
        # INSERT INTO VENDORS TABLE
        vendor = await insert_vendor({
            "customer_id": customer[0]["id"],
            "vendortype": vType,
            "vendorsize": order.vendorSize,
            "businesslicense": order.businessLicense,
            "insurancenumber": order.insuranceNumber,
            "vendordescription": order.vendorDescription
        })

    # IF NO INSTANCE OF CUSTOMER LIST OR IS EMPTY CUSTOMER LIST
    if not isinstance(customer, list) or len(customer) == 0:
        raise HTTPException(status_code=500, detail="Customer insert returned empty response")
    
    customer_id = customer[0].get("id")
    
    # IF NO CUSTOMER ID
    if not customer_id:
        raise HTTPException(status_code=500, detail="Customer ID missing from response")
    
    # CREATE PAYPAL ORDER
    paypal_order = await create_paypal_order(amount)

    # SAVE STATUS OF ORDER
    order_result = await insert_order({
        "customer_id": customer_id,
        "paypal_order_id": paypal_order["id"],
        "amount": amount,
        "status": paypal_order["status"]
    })
        
    return {
        "orderID": paypal_order["id"]
    }