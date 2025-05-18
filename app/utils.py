# app/utils.py
from babel.numbers import format_currency
import pandas as pd


# 🔹 Used throughout the app to trim long strings in DataFrames before displaying or exporting
def trim_text(text, max_len=16):
    return str(text)[:max_len] if pd.notnull(text) else ""


# 🔹 Used in monthly report to format total INR values as ₹ with Indian-style formatting
def format_inr(amount):
    return format_currency(round(amount), 'INR', locale='en_IN')


# 🔹 Used in Order Summary status classification (based on GRN quantity & QA Status)
def classify(row):
    if row['GRN Qty'] == 0:
        return "Shipped - No GRN" if "approved" in row['QA Status'] else "No Item Shipped"
    elif row['GRN Qty'] < row['Order Qty']:
        return "Shipped - Partial GRN"
    elif row['GRN Qty'] < row['Order Qty']:
        return "Shipped - Partial GRN"
    elif row['GRN Qty'] > row['Order Qty']:
        return "GRN > Ordered – Check"
    elif row['GRN Qty'] >= row['Order Qty'] and "approved" in row['QA Status']:
        return "All OK"
    else:
        return "Check Manually"


# 🔹 Used when viewing a specific Order No. — classifies individual line items
def classify_line(row):
    if row['GRN Qty'] == 0:
        return "Not Shipped"
    elif row['GRN Qty'] < row['Order Qty']:
        return "Partial GRN"
    else:
        return "Fully Shipped"


# 🔹 Used in Part Number search section to classify order-wise GRN status
def po_part_status(row):
    if row['GRN Qty'] == 0:
        return "Not Yet Shipped"
    elif row['GRN Qty'] < row['Order Qty']:
        return "Partial GRN"
    else:
        return "Fully Received"


# 🔹 Used in GRN tab (date-wise report) to classify GRN entries
def grn_status(row):
    if row['GRN Qty'] == 0:
        return "Not Shipped"
    elif row['GRN Qty'] < row['Order Qty']:
        return "Partial GRN"
    else:
        return "Fully Received"


# 🔹 Used in Stock-In entries (date-wise) to classify stock status
def stock_status(row):
    if row['Stock Qty'] == 0:
        return "Not Stocked"
    elif row['Stock Qty'] < row['GRN Qty']:
        return "Partial Stocked"
    else:
        return "Fully Stocked"


# 🔹 Used in Aircraft Code query (e.g., VT-XYZ) — classifies shipping at order level
def classify_ac(row):
    if row['GRN Qty'] == 0:
        return "Not Shipped"
    elif row['GRN Qty'] < row['Order Qty']:
        return "Partially Shipped"
    else:
        return "Fully Shipped"


# 🔹 Used in Aircraft Line-level breakdown — considers both shipping & GRN for fine-grained status
def classify_procurement(row):
    shipping_no = str(row['MAWB No. / Consignment No./  Bill of Lading No.']).strip()
    grn = row['GRN Qty']
    order = row['Order Qty']

    has_shipping = shipping_no != '' and shipping_no.lower() != 'nan'

    if not has_shipping and grn == 0:
        return "Not Shipped"
    elif has_shipping and grn == 0:
        return "Shipped – No GRN"
    elif has_shipping and 0 < grn < order:
        return "Partial GRN"
    elif has_shipping and grn >= order:
        return "Fully Received"
    else:
        return "Check Manually"


# 🔹 Used when showing unit price in Part No. search results (with ₹ or $ prefix)
def format_unit_price(row):
    if pd.isnull(row['Unit Price']):
        return "-"
    raw = str(row['Currency']).strip().upper()
    currency = (
        "INR" if "INR" in raw or "INDIAN" in raw else
        "USD" if "USD" in raw or "US DOLLAR" in raw else
        raw  # fallback
    )

    if currency in ["INR", "INDIAN RUPEE"]:
        return f"₹ {row['Unit Price']:.2f}"
    elif currency == "USD":
        return f"$ {row['Unit Price']:.2f}"
    else:
        return f"{currency} {row['Unit Price']:.2f}"  # fallback


# 🔹 Used in Part No. search section to generate Status column from GRN comparison
def determine_shipment_status(row):
    if row['GRN Qty'] == 0:
        return "Not Yet Shipped"
    elif row['GRN Qty'] < row['Order Qty']:
        return "Partial GRN"
    else:
        return "Fully Received"
