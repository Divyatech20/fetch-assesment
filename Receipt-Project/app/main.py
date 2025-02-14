from fastapi import FastAPI, HTTPException
from app.models import Receipt, Item
import uuid
import threading
from datetime import datetime, time
import math

# in memory storage
receipts = {}
lock = threading.Lock()

# fastapi setup
app = FastAPI()

# endpoints
@app.post("/receipts/process")
def process_receipt(receipt: Receipt):
    #generate uuid
    receipt_id = str(uuid.uuid4())
    
    # store in memory with lock
    with lock:
        receipts[receipt_id] = receipt.dict()
    
    return {"id": receipt_id}

@app.get("/receipts/{id}/points")
def get_points(id: str):
    with lock:
        receipt_data = receipts.get(id)
    
    if not receipt_data:
        raise HTTPException(status_code=404, detail="No receipt found for that ID")
    
    receipt = Receipt(**receipt_data)
    points = calculate_points(receipt)
    return {"points": points}

# points calculation
def calculate_points(receipt: Receipt) -> int:
    points = 0

    # Rule 1: alphanumeric character count in retailer name
    retailer_alnum = sum(c.isalnum() for c in receipt.retailer)
    points += retailer_alnum
    print(f"Retailer name points: {retailer_alnum}")

    # Rule 2: round dollar total
    total = float(receipt.total)
    if total == int(total):
        points += 50
        print("Round dollar total: +50 points")

    # Rule 3: multiple of 0.25
    if (total * 100) % 25 == 0:
        points += 25
        print("Multiple of 0.25: +25 points")

    # Rule 4: 5 points for every 2 items
    item_points = (len(receipt.items) // 2) * 5
    points += item_points
    print(f"Item points: {item_points}")

    # Rule 5: trim description length and calculate points
    desc_points = 0
    for item in receipt.items:
        trimmed_desc = item.shortDescription.strip()
        if len(trimmed_desc) % 3 == 0:
            price = float(item.price)
            item_desc_points = math.ceil(price * 0.2)
            desc_points += item_desc_points
            print(f"Item '{trimmed_desc}': +{item_desc_points} points")
    points += desc_points

    # Rule 6: purchase date is an odd day
    purchase_date = datetime.strptime(receipt.purchaseDate, "%Y-%m-%d")
    if purchase_date.day % 2 != 0:
        points += 6
        print("Odd purchase day: +6 points")

    # Rule 7: time between 2:00pm and 4:00pm
    purchase_time = datetime.strptime(receipt.purchaseTime, "%H:%M").time()
    if time(14, 0) <= purchase_time < time(16, 0):
        points += 10
        print("Time between 2:00pm and 4:00pm: +10 points")

    print(f"Total points: {points}")
    return points