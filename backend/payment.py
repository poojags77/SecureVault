import razorpay
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User

load_dotenv("../.env")
payment_status = {}
router = APIRouter()

client = razorpay.Client(auth=(
    os.getenv("RAZORPAY_KEY_ID"),
    os.getenv("RAZORPAY_KEY_SECRET")
))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# STEP 1: Create Razorpay Order
@router.post("/create-order")
def create_order(username: str):
    order = client.order.create({
        "amount": 5000,  # $500 in cents
        "currency": "USD",
        "payment_capture": 1
    })

    return {
        "order_id": order["id"],
        "message": "Order created. Use this ID to pay."
    }

# STEP 2: Simulate Verification (Milestone 2)
@router.post("/verify-payment")
def verify_payment(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()

    if user:
        user.subscription = "premium"
        db.commit()

        return {"message": "Payment verified. Premium activated."}

    return {"error": "User not found"}

from fastapi.responses import HTMLResponse
import os

@router.get("/pay/{order_id}", response_class=HTMLResponse)
def pay(order_id: str):
    key_id = os.getenv("RAZORPAY_KEY_ID")

    return f"""
    <html>
    <head>
        <title>SecureVault Payment</title>
        <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(120deg, #1d2671, #c33764);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}

            .card {{
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                text-align: center;
                width: 350px;
            }}

            .title {{
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }}

            .price {{
                font-size: 28px;
                color: green;
                margin: 20px 0;
            }}

            .btn {{
                background: #3399cc;
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 16px;
                border-radius: 6px;
                cursor: pointer;
                width: 100%;
            }}

            .btn:hover {{
                background: #287ea5;
            }}

            .desc {{
                color: gray;
                margin-bottom: 20px;
            }}
        </style>
    </head>

    <body>
        <div class="card">
            <div class="title">SecureVault Premium</div>
            <div class="desc">Unlock premium security features</div>
            <div class="price">$50</div>

            <button class="btn" id="pay-btn">Pay with Razorpay</button>
        </div>

        <script>
            var options = {{
                "key": "{key_id}",
                "amount": "50000",
                "currency": "INR",
                "name": "SecureVault",
                "description": "Premium Subscription",
                "order_id": "{order_id}",

                "handler": function (response){{
                    fetch("/payment-success/{order_id}");
                    window.location.href = "/payment-success-page";
                }}
            }};

            var rzp = new Razorpay(options);

            rzp.on('payment.failed', function (response){{
                fetch("/payment-failed/{order_id}");
                window.location.href = "/payment-failed-page";
            }});

            document.getElementById('pay-btn').onclick = function(e){{
                rzp.open();
                e.preventDefault();
            }}
        </script>
    </body>
    </html>
    """

@router.get("/payment-success/{order_id}")
def payment_success(order_id: str):
    payment_status[order_id] = "success"
    return {"status": "success"}


@router.get("/payment-failed/{order_id}")
def payment_failed(order_id: str):
    payment_status[order_id] = "failed"
    return {"status": "failed"}


@router.get("/payment-status/{order_id}")
def get_payment_status(order_id: str):
    return {"status": payment_status.get(order_id, "pending")}

@router.get("/payment-success-page", response_class=HTMLResponse)
def payment_success_page():
    return """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(120deg, #1d2671, #c33764);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .card {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                text-align: center;
                width: 350px;
            }

            .success {
                color: green;
                font-size: 26px;
                font-weight: bold;
            }

            .btn {
                background: green;
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 16px;
                border-radius: 6px;
                margin-top: 20px;
                cursor: pointer;
            }
        </style>
    </head>

    <body>
        <div class="card">
            <div class="success">Payment Successful</div>
            <h3>Premium Activated</h3>
            <p>You can now return to the CLI.</p>
        </div>
    </body>
    </html>
    """
@router.get("/payment-failed-page", response_class=HTMLResponse)
def payment_failed_page():
    return """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(120deg, #1d2671, #c33764);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }

            .card {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                text-align: center;
                width: 350px;
            }

            .failed {
                color: red;
                font-size: 26px;
                font-weight: bold;
            }

            .btn {
                background: red;
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 16px;
                border-radius: 6px;
                margin-top: 20px;
                cursor: pointer;
            }
        </style>
    </head>

    <body>
        <div class="card">
            <div class="failed">Payment Failed</div>
            <h3>Please Try Again</h3>
            <p>You can close this page and retry from CLI.</p>
        </div>
    </body>
    </html>
    """