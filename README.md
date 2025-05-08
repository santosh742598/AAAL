
# ✈️ Procurement Monitoring Dashboard

This Streamlit application provides a comprehensive monitoring interface for Laminaar Excel-based procurement data.

🌐 Live App Access + Laminaar Export Instructions
You can access the live dashboard here:
🔗 Go to Dashboard → alliance.streamlit.app

📤 How to Export from Laminaar
        1. To use this dashboard, export data from Laminaar ERP (e.g., ARMS® or similar modules) as follows:
        2. Go to the Procurement Module → Select your filters (date range, supplier, order type)
        3. Choose the Order Tracker or PO Tracker module
        4. Export the results using the Excel (.xlsx) format
        5. Ensure the downloaded file contains these sheets: PURCHASE_ORDER, ADV_EXCHANGE_ORDER (optional, for exchange items)
        6. Upload or place this file into the dashboard interface
        7. Make sure the file includes fields like: Order No., Part No., Order Qty, GRN Qty, Stock Qty, Supplier, A/C Reg. No, MAWB No., GRN Date, Stock-In Date

## 📁 Upload Format

      The app expects an `.xlsx` Excel file exported from your **Order Tracker module** with two key sheets:
      - `ADV_EXCHANGE_ORDER`
      - `PURCHASE_ORDER`

      The sheets should contain columns like:
      - `Order No.`, `Part No.`, `Order Qty`, `GRN Qty`, `Stock Qty`, `Supplier`, `A/C Reg. No`, `MAWB No.`, `GRN Date`, `Stock-In Date`, etc.

---

## ✅ Key Features

### 📊 Order Summary
- Aggregated `Order Qty` and `GRN Qty` **without duplication**.
- Accurate classification into:
  - `All OK`
  - `Shipped – Partial GRN`
  - `Shipped – No GRN`
  - `No Item Shipped`

### 🚫 Not Yet Shipped
- Lists orders with zero GRN and missing shipping details (MAWB No.).

### 📦 Shipped But GRN Not Fully Done
- Identifies orders with MAWB info but incomplete GRN receipts.

### 🔧 Part Number Lookup
- Drill down by `Part No.` to view GRN and PO status across orders.

### 📅 Date-Wise Activity Report
- Select a date to view:
  - 🆕 New Orders
  - 🚚 Shipped Items
  - ✅ GRN Entries (summed across lines)
  - 📦 Stock-In Entries

### 🤖 Ask a Simple Question
- Natural language support for:
  - `supplier atr`
  - `204X1217`
  - `abc`
  - `not shipped`
  - `partial grn`

---

## 🛠️ How Grouping Works

To avoid inflated quantities:
- `Order Qty` is taken **once per (Order No., Part No.)**
- `GRN Qty` and `Stock Qty` are **summed** across all batches
- Statuses are derived cleanly using these totals

---

## 💡 Deployment

To run:
```bash
streamlit run streamlit_app.py
```

Place additional pages in the `/pages` folder if using multi-page mode.

---

## 📬 Support

For questions or suggestions, contact the dashboard developer.
