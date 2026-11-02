"""Make the fake shop data (run once by the author; the CSVs are in the repo).
Batch 1 = the shop's first 6 months. Batch 2 = the next 2 weeks: new orders,
some old orders change status, one customer moves city, and one new status
'refunded' appears that our tests do not know about yet."""
import csv, random, datetime as dt
random.seed(42)
first = "Aarav Vivaan Aditya Ananya Diya Isha Kabir Meera Rohan Saanvi Arjun Kavya Neha Rahul Priya Vikram Sneha Karan Pooja Nikhil".split()
last = "Sharma Verma Iyer Nair Reddy Patel Gupta Singh Das Kulkarni Joshi Mehta Rao Khan Bose".split()
cities = ["Mumbai", "pune", "Bengaluru ", "chennai", "Hyderabad", "Delhi", "kolkata", "Jaipur", "Lucknow", "Ahmedabad"]
products = [  # id, name, category, price in paise
    (1, "Masala Chai 250g", "Beverages", 18000), (2, "Filter Coffee 500g", "Beverages", 42000),
    (3, "Basmati Rice 5kg", "Staples", 69900), (4, "Toor Dal 1kg", "Staples", 16500),
    (5, "Cold Pressed Oil 1L", "Staples", 32000), (6, "Mixed Namkeen 400g", "Snacks", 12000),
    (7, "Ragi Cookies 200g", "Snacks", 9500), (8, "Dark Chocolate 100g", "Snacks", 15000),
    (9, "Steel Bottle 1L", "Home", 54900), (10, "Cotton Towel", "Home", 39900)]
start = dt.datetime(2026, 1, 1, 9, 0)

def ts(d): return d.strftime("%Y-%m-%d %H:%M:%S")

def write(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

customers = []
for cid in range(1, 301):
    fn, ln = random.choice(first), random.choice(last)
    email = f"  {fn}.{ln}{cid}@Example.com " if cid % 7 == 0 else f"{fn.lower()}.{ln.lower()}{cid}@example.com"
    signup = start + dt.timedelta(days=random.randint(0, 150), minutes=random.randint(0, 600))
    customers.append([cid, fn, ln, email, random.choice(cities), signup.date().isoformat(), ts(signup)])

next_pay = [50001]

def pay_id():
    next_pay[0] += 1
    return next_pay[0] - 1

def make_orders(oid_from, n, day_from, day_to):
    orders, items, pays = [], [], []
    iid = oid_from * 10
    for oid in range(oid_from, oid_from + n):
        c = random.choice(customers)
        od = start + dt.timedelta(days=random.randint(day_from, day_to), minutes=random.randint(0, 800))
        status = random.choices(["placed", "shipped", "delivered", "cancelled", "returned"], [5, 10, 70, 10, 5])[0]
        if status != "placed" and random.random() < 0.3:
            status = status.upper()  # messy source system
        orders.append([oid, c[0], od.date().isoformat(), status, ts(od)])
        total = 0
        for p in random.sample(products, random.randint(1, 3)):
            q = random.randint(1, 3)
            items.append([iid, oid, p[0], p[1], p[2], q, p[3]]); iid += 1
            total += q * p[3]
        method = random.choices(["upi", "card", "cod", "wallet"], [55, 20, 15, 10])[0]
        if method == "upi" and random.random() < 0.15:  # part paid by wallet
            part = total // 2
            pays.append([pay_id(), oid, "wallet", part]); total -= part
        pays.append([pay_id(), oid, method, total])
    return orders, items, pays

H_C = ["customer_id", "first_name", "last_name", "email", "city", "signup_date", "updated_at"]
H_O = ["order_id", "customer_id", "order_date", "status", "updated_at"]
H_I = ["order_item_id", "order_id", "product_id", "product_name", "category", "quantity", "unit_price_paise"]
H_P = ["payment_id", "order_id", "payment_method", "amount_paise"]

o1, i1, p1 = make_orders(1001, 2000, 0, 180)
write("data/raw/batch1/customers.csv", H_C, customers)
write("data/raw/batch1/orders.csv", H_O, o1)
write("data/raw/batch1/order_items.csv", H_I, i1)
write("data/raw/batch1/payments.csv", H_P, p1)

# ---- batch 2: two weeks later ----
o2, i2, p2 = make_orders(3001, 150, 181, 195)
o2[10][3] = "refunded"; o2[20][3] = "refunded"            # a new status nobody told us about
updates = []
for o in random.sample([o for o in o1 if o[3].lower() == "shipped"], 40):
    when = start + dt.timedelta(days=random.randint(182, 195), minutes=random.randint(0, 800))
    updates.append([o[0], o[1], o[2], "delivered", ts(when)])   # shipped -> delivered
c_move = list(customers[4]); c_move[4] = "Bengaluru"
c_move[6] = ts(start + dt.timedelta(days=190))              # customer 5 moved city
write("data/raw/batch2/customers.csv", H_C, [c_move])
write("data/raw/batch2/orders.csv", H_O, o2 + updates)
write("data/raw/batch2/order_items.csv", H_I, i2)
write("data/raw/batch2/payments.csv", H_P, p2)
print("customers", len(customers), "orders", len(o1), "+", len(o2), "new and", len(updates), "updated")
