from __future__ import annotations
from pathlib import Path
from datetime import datetime, timedelta, timezone
import random
import pandas as pd

def generate_retail_demo(out_dir: str, rows: int = 1000, seed: int = 42) -> list[Path]:
    random.seed(seed)
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)

    states = ["TX", "CA", "NY", "FL", "WA"]
    now = datetime.now(timezone.utc)

    customers = []
    for i in range(rows):
        cid = i if i % 37 else max(0, i - 1)  # deliberate duplicate IDs
        customers.append({
            "customer_id": cid,
            "first_name": f"Customer{i}",
            "email": None if i % 13 == 0 else f"customer{i}@example.com",
            "ssn": f"{100 + (i % 800):03d}-{10 + (i % 80):02d}-{1000 + (i % 8000):04d}",
            "state": random.choice(states),
            "updated_at": (now - timedelta(hours=random.randint(1, 72))).isoformat(),
        })

    orders = []
    for i in range(rows * 2):
        amount = round(random.uniform(5, 500), 2)
        if i % 101 == 0:
            amount = -amount
        orders.append({
            "order_id": i,
            "customer_id": random.randint(0, rows + 25),  # some unknown customers
            "amount": amount,
            "order_ts": (now - timedelta(hours=random.randint(0, 240))).isoformat(),
        })

    inventory = []
    for i in range(max(100, rows // 5)):
        qty = random.randint(0, 200)
        if i % 43 == 0:
            qty = -random.randint(1, 10)
        inventory.append({"sku_id": f"SKU-{i:05d}", "inventory": qty, "store_id": random.randint(1, 20)})

    outputs = []
    for name, data in [("customers.csv", customers), ("orders.csv", orders), ("inventory.csv", inventory)]:
        path = p / name
        pd.DataFrame(data).to_csv(path, index=False)
        outputs.append(path)
    return outputs
