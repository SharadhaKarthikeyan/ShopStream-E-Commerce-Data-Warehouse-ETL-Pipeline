import os
import random
import uuid
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

def main():
    print("Starting optimized synthetic data generation...")
    
    # Initialize Faker and random seeds for reproducibility
    fake = Faker()
    Faker.seed(42)
    random.seed(42)
    np.random.seed(42)
    
    # Ensure data directory exists
    raw_data_dir = os.path.join("data", "raw")
    os.makedirs(raw_data_dir, exist_ok=True)
    
    # ----------------------------------------------------
    # 1. Generate Marketing Campaigns (100)
    # ----------------------------------------------------
    print("Generating 100 marketing campaigns...")
    campaigns = []
    channels = ['Google Ads', 'Facebook', 'Email', 'Affiliate', 'Influencer', 'TikTok', 'Instagram']
    segments = ['New Customers', 'Seniors', 'Tech Enthusiasts', 'Fashionistas', 'General', 'Gamers', 'Outdoor']
    
    start_base = datetime(2023, 1, 1)
    campaign_intervals = []
    
    for i in range(1, 101):
        camp_id = f"MC{i:03d}"
        channel = random.choice(channels)
        # Mix casing for dirty data occasionally
        if random.random() < 0.05:
            channel = channel.upper()
        elif random.random() < 0.05:
            channel = channel.lower()
            
        start_date = start_base + timedelta(days=random.randint(0, 1200))
        end_date = start_date + timedelta(days=random.randint(7, 60))
        budget = round(random.uniform(500, 15000), 2)
        
        campaigns.append({
            'campaign_id': camp_id,
            'campaign_name': f"Campaign {fake.word().capitalize()} {camp_id}",
            'channel': channel,
            'budget': budget,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'target_segment': random.choice(segments)
        })
        
        campaign_intervals.append({
            'campaign_id': camp_id,
            'start_dt': start_date,
            'end_dt': end_date
        })
        
    df_campaigns = pd.DataFrame(campaigns)
    
    # ----------------------------------------------------
    # 2. Generate Customers (10,000)
    # ----------------------------------------------------
    print("Generating 10,000 customers...")
    customers = []
    customer_segments = ['General', 'Seniors', 'Tech Enthusiasts', 'Fashionistas', 'Gamers', 'Outdoor']
    states_cities = [
        ('CA', 'Los Angeles'), ('CA', 'San Francisco'), ('CA', 'San Jose'),
        ('NY', 'New York'), ('NY', 'Buffalo'),
        ('TX', 'Houston'), ('TX', 'Austin'), ('TX', 'Dallas'),
        ('FL', 'Miami'), ('FL', 'Orlando'), ('FL', 'Tampa'),
        ('IL', 'Chicago'),
        ('WA', 'Seattle'),
        ('MA', 'Boston'),
        ('CO', 'Denver'),
        ('GA', 'Atlanta')
    ]
    
    cust_signup_dict = {}
    
    for i in range(1, 10001):
        cust_id = f"CUST{i:05d}"
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}.{i}@example.com"
        signup_date = start_base + timedelta(days=random.randint(0, 1200))
        state, city = random.choice(states_cities)
        
        cust_segment = random.choice(customer_segments)
        # Dirty data: mixed casing in segment
        if random.random() < 0.05:
            cust_segment = cust_segment.upper()
            
        customers.append({
            'customer_id': cust_id,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'signup_date': signup_date.strftime('%Y-%m-%d'),
            'city': city,
            'state': state,
            'country': 'USA',
            'customer_segment': cust_segment
        })
        
        cust_signup_dict[cust_id] = signup_date
        
    df_customers = pd.DataFrame(customers)
    
    # ----------------------------------------------------
    # 3. Generate Products (2,000)
    # ----------------------------------------------------
    print("Generating 2,000 products...")
    products = []
    categories = {
        'Electronics': ['Smartphones', 'Laptops', 'Headphones', 'Smartwatches', 'Cameras'],
        'Apparel': ['Shirts', 'Jeans', 'Jackets', 'Shoes', 'Socks'],
        'Home & Kitchen': ['Blenders', 'Coffee Makers', 'Cookware', 'Bedding', 'Vacuums'],
        'Beauty & Personal Care': ['Skincare', 'Makeup', 'Haircare', 'Perfume', 'Tools'],
        'Sports & Outdoors': ['Tents', 'Bicycles', 'Backpacks', 'Fitness Gear', 'Water Bottles']
    }
    
    brands = ['Sony', 'Apple', 'Samsung', 'Nike', 'Adidas', 'Patagonia', 'KitchenAid', 'Dyson', 'Loreal', 'Estee Lauder']
    product_prices = {}
    product_costs = {}
    
    product_keys = list(categories.keys())
    for i in range(1, 2001):
        prod_id = f"PROD{i:04d}"
        category = random.choice(product_keys)
        subcategory = random.choice(categories[category])
        brand = random.choice(brands)
        
        cost_price = round(random.uniform(2.0, 400.0), 2)
        unit_price = round(cost_price * random.uniform(1.2, 2.5), 2)
        
        # Casing issues in categories/subcategories occasionally
        if random.random() < 0.05:
            category = category.upper()
        if random.random() < 0.05:
            subcategory = subcategory.lower()
            
        active_flag = 'True' if random.random() < 0.95 else 'False'
        if random.random() < 0.05:
            active_flag = 'ACTIVE' if active_flag == 'True' else 'INACTIVE'
            
        products.append({
            'product_id': prod_id,
            'product_name': f"{brand} {subcategory} Model {random.randint(100, 999)}",
            'category': category,
            'subcategory': subcategory,
            'brand': brand,
            'unit_price': unit_price,
            'cost_price': cost_price,
            'active_flag': active_flag
        })
        
        product_prices[prod_id] = unit_price
        product_costs[prod_id] = cost_price
        
    df_products = pd.DataFrame(products)
    
    # ----------------------------------------------------
    # 4. Generate Orders (50,000)
    # ----------------------------------------------------
    print("Generating 50,000 orders...")
    orders = []
    order_statuses = ['completed', 'shipped', 'returned', 'cancelled', 'pending']
    status_weights = [0.65, 0.20, 0.08, 0.05, 0.02]
    
    customer_ids = df_customers['customer_id'].tolist()
    cust_weights = np.random.zipf(1.8, size=len(customer_ids))
    cust_weights = cust_weights / cust_weights.sum()
    
    order_date_dict = {}
    order_status_dict = {}
    
    # Pre-select customers and statuses for efficiency
    selected_customers = np.random.choice(customer_ids, size=50000, p=cust_weights)
    selected_statuses = np.random.choice(order_statuses, size=50000, p=status_weights)
    
    for i in range(1, 50001):
        ord_id = f"ORD{i:05d}"
        cust_id = selected_customers[i-1]
        
        cust_signup = cust_signup_dict[cust_id]
        order_date = cust_signup + timedelta(days=random.randint(0, 1000))
        
        if order_date > datetime.now():
            order_date = datetime.now() - timedelta(days=random.randint(1, 10))
            
        status = selected_statuses[i-1]
        if random.random() < 0.05:
            status = status.upper()
            
        # Fast Campaign attribution
        camp_id = None
        if random.random() < 0.25:
            active_camps = [
                c['campaign_id'] for c in campaign_intervals 
                if c['start_dt'] <= order_date <= c['end_dt']
            ]
            if active_camps:
                camp_id = random.choice(active_camps)
                
        orders.append({
            'order_id': ord_id,
            'customer_id': cust_id,
            'order_date': order_date.strftime('%Y-%m-%d'),
            'order_status': status,
            'campaign_id': camp_id
        })
        
        order_date_dict[ord_id] = order_date
        order_status_dict[ord_id] = status
        
    df_orders = pd.DataFrame(orders)
    
    # ----------------------------------------------------
    # 5. Generate Order Items (120,000)
    # ----------------------------------------------------
    print("Generating 120,000 order items...")
    order_items = []
    order_ids = df_orders['order_id'].tolist()
    product_ids = df_products['product_id'].tolist()
    
    # Step 1: Assign 1 item to each order to guarantee referential sanity
    for idx, ord_id in enumerate(order_ids):
        prod_id = random.choice(product_ids)
        price = product_prices[prod_id]
        qty = random.randint(1, 3)
        discount = 0.0
        if random.random() < 0.15:
            discount = round(price * qty * random.uniform(0.05, 0.20), 2)
            
        tax = round((price * qty - discount) * 0.08, 2)
        total = round((price * qty - discount) + tax, 2)
        
        order_items.append({
            'order_item_id': f"ITEM{idx+1:06d}",
            'order_id': ord_id,
            'product_id': prod_id,
            'quantity': qty,
            'unit_price': price,
            'discount': discount,
            'tax': tax,
            'item_total': total
        })
        
    # Step 2: Assign remaining 70,000 items randomly
    for idx in range(50001, 120001):
        ord_id = random.choice(order_ids)
        prod_id = random.choice(product_ids)
        price = product_prices[prod_id]
        qty = random.randint(1, 4)
        
        if random.random() < 0.0001:
            qty = 0
        elif random.random() < 0.0001:
            qty = -1
            
        discount = 0.0
        if random.random() < 0.15:
            discount = round(price * qty * random.uniform(0.05, 0.20), 2)
            
        tax = round((price * qty - discount) * 0.08, 2)
        total = round((price * qty - discount) + tax, 2)
        
        order_items.append({
            'order_item_id': f"ITEM{idx:06d}",
            'order_id': ord_id,
            'product_id': prod_id,
            'quantity': qty,
            'unit_price': price,
            'discount': discount,
            'tax': tax,
            'item_total': total
        })
        
    df_order_items = pd.DataFrame(order_items)
    
    # ----------------------------------------------------
    # 6. Generate Payments (50,000)
    # ----------------------------------------------------
    print("Generating 50,000 payments...")
    payments = []
    payment_methods = ['credit_card', 'paypal', 'bank_transfer', 'apple_pay']
    order_totals = df_order_items.groupby('order_id')['item_total'].sum().to_dict()
    
    for idx, (ord_id, ord_status) in enumerate(zip(order_ids, df_orders['order_status'])):
        pay_id = f"PAY{idx+1:05d}"
        method = random.choice(payment_methods)
        
        status = 'success'
        clean_status = str(ord_status).lower()
        if 'cancelled' in clean_status:
            status = 'failed' if random.random() < 0.70 else 'success'
        elif 'pending' in clean_status:
            status = 'pending'
            
        if random.random() < 0.05:
            status = status.upper()
            
        amount = order_totals[ord_id]
        if status.lower() == 'success' and random.random() < 0.0001:
            amount = -50.0
            
        order_date = order_date_dict[ord_id]
        payment_date = order_date + timedelta(minutes=random.randint(2, 120))
        
        payments.append({
            'payment_id': pay_id,
            'order_id': ord_id,
            'payment_method': method,
            'payment_status': status,
            'payment_amount': amount,
            'currency': 'USD',
            'transaction_id': f"TXN-{uuid.uuid4().hex[:12].upper()}",
            'payment_date': payment_date.strftime('%Y-%m-%d %H:%M:%S')
        })
        
    df_payments = pd.DataFrame(payments)
    
    # ----------------------------------------------------
    # 7. Generate Shipments (45,000)
    # ----------------------------------------------------
    print("Generating 45,000 shipments...")
    shipments = []
    shipping_providers = ['FedEx', 'UPS', 'DHL', 'USPS']
    
    # Select 45,000 orders
    shipped_orders = df_orders[~df_orders['order_status'].str.lower().isin(['pending', 'cancelled'])]
    
    if len(shipped_orders) < 45000:
        selected_order_ids = random.sample(order_ids, 45000)
    else:
        selected_order_ids = random.sample(shipped_orders['order_id'].tolist(), 45000)
        
    for idx, ord_id in enumerate(selected_order_ids):
        shp_id = f"SHP{idx+1:05d}"
        
        order_date = order_date_dict[ord_id]
        ship_date = order_date + timedelta(days=random.randint(1, 3))
        expected_delivery = ship_date + timedelta(days=random.randint(2, 7))
        provider = random.choice(shipping_providers)
        
        ord_status = order_status_dict[ord_id].lower()
        if 'returned' in ord_status:
            status = 'delivered'
        elif 'shipped' in ord_status:
            status = 'in_transit' if random.random() < 0.60 else 'delayed'
        else:
            status = 'delivered'
            
        actual_delivery = None
        if status in ['delivered', 'returned']:
            if random.random() < 0.15:
                actual_delivery = expected_delivery + timedelta(days=random.randint(1, 5))
                status = 'delayed'
            else:
                actual_delivery = expected_delivery - timedelta(days=random.randint(0, 2))
                
        actual_delivery_str = actual_delivery.strftime('%Y-%m-%d') if actual_delivery else None
        
        if random.random() < 0.05:
            status = status.upper()
            
        shipments.append({
            'shipment_id': shp_id,
            'order_id': ord_id,
            'shipment_date': ship_date.strftime('%Y-%m-%d'),
            'expected_delivery_date': expected_delivery.strftime('%Y-%m-%d'),
            'actual_delivery_date': actual_delivery_str,
            'shipping_provider': provider,
            'shipment_status': status
        })
        
    df_shipments = pd.DataFrame(shipments)
    
    # ----------------------------------------------------
    # 8. Generate Refunds (5,000)
    # ----------------------------------------------------
    print("Generating 5,000 refunds...")
    refunds = []
    refund_reasons = ['damaged_item', 'defective_item', 'wrong_item_shipped', 'late_delivery', 'buyer_remorse']
    refund_statuses = ['processed', 'pending', 'rejected']
    
    returned_orders = df_orders[df_orders['order_status'].str.lower() == 'returned']['order_id'].tolist()
    
    if len(returned_orders) < 5000:
        other_orders = df_orders[~df_orders['order_id'].isin(returned_orders)]['order_id'].tolist()
        selected_refund_orders = returned_orders + random.sample(other_orders, 5000 - len(returned_orders))
    else:
        selected_refund_orders = random.sample(returned_orders, 5000)
        
    for idx, ord_id in enumerate(selected_refund_orders):
        ref_id = f"REF{idx+1:05d}"
        
        order_date = order_date_dict[ord_id]
        refund_date = order_date + timedelta(days=random.randint(5, 20))
        reason = random.choice(refund_reasons)
        status = np.random.choice(refund_statuses, p=[0.85, 0.10, 0.05])
        
        total_order_amt = order_totals[ord_id]
        
        if random.random() < 0.80:
            ref_amt = total_order_amt
        else:
            ref_amt = round(total_order_amt * random.uniform(0.1, 0.9), 2)
            
        if random.random() < 0.0002:
            ref_amt = total_order_amt + 500.0
            
        if random.random() < 0.05:
            status = status.upper()
            
        refunds.append({
            'refund_id': ref_id,
            'order_id': ord_id,
            'refund_reason': reason,
            'refund_status': status,
            'refund_amount': ref_amt,
            'refund_date': refund_date.strftime('%Y-%m-%d')
        })
        
    df_refunds = pd.DataFrame(refunds)
    
    # ----------------------------------------------------
    # Inject Duplicate Rows (~0.1%)
    # ----------------------------------------------------
    print("Injecting duplicate rows...")
    df_customers = pd.concat([df_customers, df_customers.sample(n=10, random_state=42)], ignore_index=True)
    df_products = pd.concat([df_products, df_products.sample(n=5, random_state=42)], ignore_index=True)
    df_orders = pd.concat([df_orders, df_orders.sample(n=50, random_state=42)], ignore_index=True)
    df_order_items = pd.concat([df_order_items, df_order_items.sample(n=120, random_state=42)], ignore_index=True)
    df_payments = pd.concat([df_payments, df_payments.sample(n=50, random_state=42)], ignore_index=True)
    df_shipments = pd.concat([df_shipments, df_shipments.sample(n=45, random_state=42)], ignore_index=True)
    df_refunds = pd.concat([df_refunds, df_refunds.sample(n=5, random_state=42)], ignore_index=True)
    
    # ----------------------------------------------------
    # Save datasets
    # ----------------------------------------------------
    print("Saving CSV files...")
    df_campaigns.to_csv(os.path.join(raw_data_dir, "marketing_campaigns.csv"), index=False)
    df_customers.to_csv(os.path.join(raw_data_dir, "customers.csv"), index=False)
    df_products.to_csv(os.path.join(raw_data_dir, "products.csv"), index=False)
    df_orders.to_csv(os.path.join(raw_data_dir, "orders.csv"), index=False)
    df_order_items.to_csv(os.path.join(raw_data_dir, "order_items.csv"), index=False)
    df_payments.to_csv(os.path.join(raw_data_dir, "payments.csv"), index=False)
    df_shipments.to_csv(os.path.join(raw_data_dir, "shipments.csv"), index=False)
    df_refunds.to_csv(os.path.join(raw_data_dir, "refunds.csv"), index=False)
    
    print("Data generation complete!")
    print(f"Generated Marketing Campaigns: {len(df_campaigns)}")
    print(f"Generated Customers: {len(df_customers)}")
    print(f"Generated Products: {len(df_products)}")
    print(f"Generated Orders: {len(df_orders)}")
    print(f"Generated Order Items: {len(df_order_items)}")
    print(f"Generated Payments: {len(df_payments)}")
    print(f"Generated Shipments: {len(df_shipments)}")
    print(f"Generated Refunds: {len(df_refunds)}")

if __name__ == "__main__":
    main()
