from fastapi import APIRouter, Request, HTTPException
from app.paypal import verify_webhook
from app.supabase import insert_payment, update_order_status, get_order_by_paypal_id, payment_exists
import logging

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/paypal")
async def paypal_webhook(request: Request):
    # GET JSON FROM REQUEST
    body = await request.json()
    
    # EXTRACT REQUEST HEADERS
    headers = request.headers

    # VERIFY WEBHOOK AUTHENTICITY
    verification = await verify_webhook(headers, body)
    
    # IF WEBHOOK IS NOT "SUCCESS"
    if verification.get("verification_status") != "SUCCESS":
        raise HTTPException(status_code=400, detail="Invalid PayPal webhook")

    # GET EVENT TYPE
    event_type = body.get("event_type")
    
    # ORDER APPROVAL
    if event_type == "CHECKOUT.ORDER.APPROVED":
        # GET RESOURCE DICT FROM BODY
        resource = body.get("resource", {})

        # EXTRACT ID FROM RESOURCE
        paypal_order_id = resource.get("id")
        
        # IF NO ID IN RESOURCE
        if not paypal_order_id:
            raise HTTPException(status_code=400, detail="Missing order id")
        
        # UPDATE ORDER STATUS WITH RESOURCE ID
        order_status_result = await update_order_status(paypal_order_id, "APPROVED")
        
    # PAYMENT COMPLETED
    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        # EXTRACT RESOURCE DICT FROM BODYt
        resource = body.get("resource", {})

        # EXTRACT CAPTURE ID FROM RESOURCE
        paypal_capture_id = resource.get("id")
        # EXTRACT AMOUNT DICT FROM RESOURCE AND GET VALUE
        amount = resource.get("amount", {}).get("value")
        # EXTRACT PAYEE INFO IN DICT AND GET EMAIL ADDRESS
        payer_email = resource.get("payee", {}).get("email_address")

        # EXTRACT SUPLEMENTARY DATA DICT, GET RELATED IDS DICT, AND GET ORDER ID
        paypal_order_id = (
            resource.get("supplementary_data", {})
            .get("related_ids", {})
            .get("order_id")
        )
        
        # GET ORDER BY ID
        order = await get_order_by_paypal_id(paypal_order_id)
        
        # IF PAYMENT ALREADY EXISTS, IGNORE PAYMENT
        if await payment_exists(paypal_capture_id):
            print("Duplicate ignored")
            return {"status": "duplicate ignored"}
                
        # INSERT TO PAYMENTS TABLE
        try:
            payment_result = await insert_payment({
                "order_id": order[0]["id"],
                "paypal_capture_id": paypal_capture_id,
                "amount": amount,
                "payer_email": payer_email,
                "status": "COMPLETED",
            })
        except Exception as e:
            # DUPLICATE WEBHOOK (ALREADY PROCESSED)
            logging.warning(f"Payment already exists: {paypal_capture_id}")

        # UPDATE ORDER STATUS TO PAID
        order_status = await update_order_status(paypal_order_id, "PAID")

        logging.info(f"Payment completed for order {paypal_order_id}")

    return {"status": "ok"}
