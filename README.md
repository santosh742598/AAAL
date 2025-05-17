# ✈️ Procurement Monitoring Dashboard

A powerful Streamlit-based tool to analyze procurement activity using Excel reports from the Laminaar system. Supports tracking of orders, GRN, shipment status, daily and monthly activity, and exports to PDF and Excel formats.

---

## 📦 Features

- Upload and parse Laminaar Excel files
- Visual summaries of:
  - Unshipped orders
  - Partial/complete GRN and stock-in entries
  - Status by Order, Part Number, or Aircraft
- 📅 Date-wise Activity Breakdown with full PDF & Excel export
- 📆 Monthly Procurement Report with currency normalization (USD to INR)
- 📤 Export:
  - Daily PDF reports with summary and detailed tables
  - Monthly PDF reports in **landscape** orientation with summary at the top
  - Excel reports for both daily and monthly activities

---

## 🛠️ Installation

```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `streamlit`
- `pandas`
- `xlsxwriter`
- `reportlab`
- `babel`

---

## ▶️ How to Run

```bash
streamlit run streamlit_procurement_app.py
```

Then open in your browser at the local URL provided (typically `http://localhost:8501`).

---

## 📥 Input Format

Upload an Excel file generated from Laminaar’s "Order Tracker" module, ensuring it contains relevant columns like:

- `Order No.`, `Part No.`, `Order Qty`, `GRN Qty`
- `MAWB No.`, `Stock Qty`, `Unit Price`, `Currency`

---

## 🧾 PDF Exports

### Daily Report PDF
- Generated in **portrait** mode
- Includes summary counts and 4 sections:
  - New Orders
  - Shipped Items
  - GRN Entries
  - Stock-In Entries

### Monthly Report PDF
- Generated in **landscape** mode
- Shows:
  - Total value in INR
  - 7.5% highlight
  - Tabular breakdown (S. No., Vendor, PO, Part, Quantity, Value)

---

## 📌 Notes

- Ensure font file `NotoSans-Regular.ttf` is present in the same directory for PDF generation.
- For proper number formatting, exchange rate input is required for USD values in monthly reports.
- Use the AI Q&A section to interactively filter data by supplier, PO, aircraft code, etc.

---

## 📄 License

This project is licensed under the MIT License – see the LICENSE file for details.
