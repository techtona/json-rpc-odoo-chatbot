from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests
import os
from dotenv import load_dotenv

# Load .env config
load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

# Init FastAPI app
app = FastAPI()

# Authenticate and get UID
def get_uid():
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "login",
            "args": [ODOO_DB, ODOO_USER, ODOO_PASSWORD]
        },
        "id": 1
    }
    res = requests.post(f"{ODOO_URL}", json=payload).json()
    return res.get("result")

# Execute JSON-RPC call to object service
def odoo_execute_kw(model, method, args, kwargs=None):
    uid = get_uid()
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB, uid, ODOO_PASSWORD,
                model, method, args, kwargs or {}
            ]
        },
        "id": 2
    }
    response = requests.post(f"{ODOO_URL}/jsonrpc", json=payload).json()
    if "error" in response:
        raise Exception(response["error"])
    return response.get("result")

# Input schema for creating invoice via agent
class InvoiceRequest(BaseModel):
    customer_name: str
    product: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    due_days: Optional[int] = 30

@app.post("/agent/create-invoice")
async def create_invoice(request: InvoiceRequest):
    try:
        customers = odoo_execute_kw(
            'res.partner', 'search_read',
            [[['name', 'ilike', request.customer_name]]],
            {'fields': ['id', 'name'], 'limit': 1}
        )

        if not customers:
            raise HTTPException(status_code=404, detail="Customer not found")

        customer = customers[0]

        invoice_data = {
            "partner_id": customer['id'],
            "move_type": "out_invoice",
            "invoice_line_ids": [[0, 0, {
                "name": request.product or "Produk Default",
                "quantity": request.quantity or 1,
                "price_unit": request.price or 10000
            }]],
        }

        invoice_id = odoo_execute_kw('account.move', 'create', [invoice_data])

        return {
            "message": "Invoice created successfully in Odoo",
            "invoice_id": invoice_id,
            "customer": customer['name']
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def root():
    return {"message": "FastAPI is working"}

@app.get("/agent/view-invoice/{invoice_id}")
async def view_invoice(invoice_id: int):
    try:
        invoice = odoo_execute_kw(
            'account.move', 'read',
            [invoice_id],
            {'fields': ['name', 'partner_id', 'invoice_date', 'amount_total', 'amount_residual', 'state']}
        )

        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        return invoice[0]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
