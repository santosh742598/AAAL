
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Procurement Monitoring Dashboard", layout="wide")

st.title("✈️ Procurement Monitoring Dashboard")

uploaded_file = st.file_uploader("Upload your Laminaar Excel file", type=["xlsx"])

if uploaded_file:
    try:
        xls = pd.ExcelFile(uploaded_file)
        st.write("Available Sheets:", xls.sheet_names)

        selected_sheet = st.selectbox("Select a sheet to process", xls.sheet_names)

        df = xls.parse(selected_sheet)

        df.columns = df.columns.str.strip()
        df['GRN Qty'] = df['GRN Qty'].fillna(0)
        df['Order Qty'] = df['Order Qty'].fillna(0)

        # Order Summary
        order_summary = df.groupby('Order No.').agg({
            'Supplier': 'first',
            'Order Qty': 'sum',
            'GRN Qty': 'sum',
            'QA Status': lambda x: ','.join(set(str(i).strip().lower() for i in x.dropna()))
        }).reset_index()

        def classify(row):
            if row['GRN Qty'] == 0:
                return "Shipped - No GRN" if "approved" in row['QA Status'] else "No Item Shipped"
            elif row['GRN Qty'] < row['Order Qty']:
                return "Shipped - Partial GRN"
            elif row['GRN Qty'] >= row['Order Qty'] and "approved" in row['QA Status']:
                return "All OK"
            else:
                return "Check Manually"

        order_summary['Status'] = order_summary.apply(classify, axis=1)
        status_counts = order_summary['Status'].value_counts()

        st.subheader("📊 Order Summary")
        st.dataframe(order_summary)

        st.subheader("📌 Status Breakdown")
        for status, count in status_counts.items():
            st.markdown(f"- **{status}**: {count} orders")

        st.subheader("🔍 Filter by Status")
        selected_status = st.selectbox("Choose status to filter", options=order_summary['Status'].unique())
        st.dataframe(order_summary[order_summary['Status'] == selected_status])

        st.subheader("🚫 Not Yet Shipped — By Order No")

        # Identify orders with GRN Qty = 0 and no MAWB/shipping info
        unshipped_orders = df[
            (df['GRN Qty'] == 0) &
            (
                    df['MAWB No. / Consignment No./  Bill of Lading No.'].isna() |
                    (df['MAWB No. / Consignment No./  Bill of Lading No.'].astype(str).str.strip() == "")
            )
            ]['Order No.'].dropna().unique()

        if len(unshipped_orders) > 0:
            selected_unshipped = st.selectbox("Select Order No. with no shipment info", sorted(unshipped_orders))
            filtered_unshipped = df[
                (df['Order No.'] == selected_unshipped) &
                (df['GRN Qty'] == 0) &
                (
                        df['MAWB No. / Consignment No./  Bill of Lading No.'].isna() |
                        (df['MAWB No. / Consignment No./  Bill of Lading No.'].astype(str).str.strip() == "")
                )
                ]

            # Show only selected columns
            columns_to_show = [
                'Order No.', 'Part No.', 'Description', 'Supplier',
                'Order Qty', 'GRN Qty', 'QA Status',
                'MAWB No. / Consignment No./  Bill of Lading No.', 'Mode of Transport'
            ]
            st.dataframe(filtered_unshipped[columns_to_show])
        else:
            st.success("✅ All orders have either shipment or GRN data.")

        st.subheader("📦 Shipped but GRN Not Fully Done — By Order No")

        # Group by Order No + Part No to compare totals
        grn_compare = df.groupby(['Order No.', 'Part No.']).agg({
            'Order Qty': 'first',
            'GRN Qty': 'sum',
            'MAWB No. / Consignment No./  Bill of Lading No.': lambda x: ', '.join(set(x.dropna().astype(str))),
            'Mode of Transport': lambda x: ', '.join(set(x.dropna().astype(str))),
            'Supplier': 'first',
            'Description': 'first'
        }).reset_index()

        # Filter: shipped (has mode or MAWB) but ordered ≠ GRN
        shipped_partial_grn = grn_compare[
            (grn_compare['Order Qty'] != grn_compare['GRN Qty']) &
            (
                    (grn_compare['MAWB No. / Consignment No./  Bill of Lading No.'].str.strip() != '') |
                    (grn_compare['Mode of Transport'].str.strip() != '')
            )

            ]

        if not shipped_partial_grn.empty:
            selected_partial_grn_order = st.selectbox(
                "Select Order No. (shipped but GRN not fully done)",
                sorted(shipped_partial_grn['Order No.'].unique())
            )

            st.dataframe(shipped_partial_grn[shipped_partial_grn['Order No.'] == selected_partial_grn_order][[
                'Order No.', 'Part No.', 'Description', 'Supplier',
                'Order Qty', 'GRN Qty', 'MAWB No. / Consignment No./  Bill of Lading No.', 'Mode of Transport'
            ]])
        else:
            st.success("✅ All shipped items have matching GRN.")

        st.subheader("🔎 Search by Part Number — PO Wise Status")

        all_parts = sorted(df['Part No.'].dropna().unique())
        selected_part = st.selectbox("Select Part Number to view order-wise status", all_parts)

        if selected_part:
            part_data = df[df['Part No.'] == selected_part]

            # Drop duplicate Order Qty rows BEFORE grouping
            dedup_part_data = part_data.drop_duplicates(subset=['Order No.', 'Part No.', 'Supplier', 'Order Qty'])

            part_po_wise = dedup_part_data.groupby(['Order No.', 'Part No.', 'Supplier']).agg({
                'Order Qty': 'first',  # Only once per order
                'GRN Qty': 'sum',  # Received in multiple lots is fine
                'Description': 'first'
            }).reset_index()


            # Status logic per PO
            def po_part_status(row):
                if row['GRN Qty'] == 0:
                    return "Not Yet Shipped"
                elif row['GRN Qty'] < row['Order Qty']:
                    return "Partial GRN"
                else:
                    return "Fully Received"


            part_po_wise['Status'] = part_po_wise.apply(po_part_status, axis=1)

            st.dataframe(part_po_wise.rename(columns={
                'Order No.': 'Order Number',
                'Order Qty': 'Ordered Qty',
                'GRN Qty': 'GRN Received Qty'
            }))

        st.subheader("🤖 Ask a Simple Question (Local Q&A)")

        user_question = st.text_input("Ask a question about your data:")

        if user_question:
            q = user_question.strip().lower()

            if "not shipped" in q:
                result = df[
                    (df['GRN Qty'] == 0) &
                    (
                            df['MAWB No. / Consignment No./  Bill of Lading No.'].isna() |
                            (df['MAWB No. / Consignment No./  Bill of Lading No.'].astype(str).str.strip() == "")
                    )
                    ]
                st.write("🔍 Orders not yet shipped:")
                st.dataframe(result)

            elif "partial grn" in q:
                grouped = df.groupby(['Order No.', 'Part No.']).agg({
                    'Order Qty': 'sum',
                    'GRN Qty': 'sum',
                    'Supplier': 'first'
                }).reset_index()
                partial = grouped[grouped['Order Qty'] != grouped['GRN Qty']]
                st.write("📦 Orders with Partial GRN:")
                st.dataframe(partial)

            elif "supplier" in q:
                words = q.split()
                supplier_name = [w for w in words if w.upper() in df['Supplier'].str.upper().unique()]
                if supplier_name:
                    result = df[df['Supplier'].str.upper().str.contains(supplier_name[0].upper())]
                    st.write(f"📋 Orders for Supplier: {supplier_name[0]}")
                    st.dataframe(result)
                else:
                    st.warning("❗ Supplier name not recognized in your question.")

            elif len(q.split()) == 1 and q.upper().strip() in df['Part No.'].astype(
                    str).str.upper().str.strip().unique():
                part_data = df[df['Part No.'].astype(str).str.upper().str.strip() == q.upper().strip()]

                # Extract 1 row per Order to get Order Qty correctly
                order_qty_info = part_data.drop_duplicates(subset=['Order No.', 'Part No.'])[
                    ['Order No.', 'Part No.', 'Supplier', 'Order Qty', 'Description']
                ]

                # Now sum GRN qty separately
                grn_sum = part_data.groupby(['Order No.', 'Part No.'])['GRN Qty'].sum().reset_index()

                # Merge both
                grouped = pd.merge(order_qty_info, grn_sum, on=['Order No.', 'Part No.'], how='left')


                # Status logic
                def status(row):
                    if row['GRN Qty'] == 0:
                        return "Not Yet Shipped"
                    elif row['GRN Qty'] < row['Order Qty']:
                        return "Partial GRN"
                    else:
                        return "Fully Received"


                grouped['Status'] = grouped.apply(status, axis=1)

                st.write(f"🔎 Results for Part No: {q.upper().strip()}")
                st.dataframe(grouped.rename(columns={
                    'Order No.': 'Order Number',
                    'Order Qty': 'Ordered Qty',
                    'GRN Qty': 'GRN Received Qty'
                }))



            elif len(q.split()) == 1 and q.upper() in df['Order No.'].str.upper().unique():
                order_data = df[df['Order No.'].str.upper() == q.upper()]

                # Extract Order Qty once per Part No
                order_qty_info = order_data.drop_duplicates(subset=['Order No.', 'Part No.'])[
                    ['Part No.', 'Supplier', 'Order Qty', 'Description']
                ]

                grn_sum = order_data.groupby(['Part No.'])['GRN Qty'].sum().reset_index()

                grouped = pd.merge(order_qty_info, grn_sum, on='Part No.', how='left')


                def item_status(row):
                    if row['GRN Qty'] == 0:
                        return "Not Yet Shipped"
                    elif row['GRN Qty'] < row['Order Qty']:
                        return "Partial GRN"
                    else:
                        return "Fully Received"


                grouped['Status'] = grouped.apply(item_status, axis=1)

                st.write(f"📦 Items under Order No: {q.upper()}")
                st.dataframe(grouped.rename(columns={
                    'Part No.': 'Part Number',
                    'Order Qty': 'Ordered Qty',
                    'GRN Qty': 'GRN Received Qty'
                }))




            elif len(q) == 3 and q.isalpha():
                aircraft_code = f"VT-{q.upper()}"
                ac_col = 'A/C Reg. No'

                single_ac_df = df[
                    df[ac_col].astype(str).str.upper().str.contains(aircraft_code) &
                    (df[ac_col].astype(str).str.count(',') == 0)
                ]

                if single_ac_df.empty:
                    st.info(f"🛬 No dedicated records found for aircraft code '{aircraft_code}'.")
                else:
                    agg_dict = {
                        'Order Qty': 'sum',
                        'GRN Qty': 'sum',
                        ac_col: 'first'
                    }
                    if 'PO Date' in df.columns:
                        agg_dict['PO Date'] = 'first'

                    ac_summary = single_ac_df.groupby('Order No.').agg(agg_dict).reset_index()

                    def classify_ac(row):
                        if row['GRN Qty'] == 0:
                            return "Not Shipped"
                        elif row['GRN Qty'] < row['Order Qty']:
                            return "Partially Shipped"
                        else:
                            return "Fully Shipped"

                    ac_summary['Status'] = ac_summary.apply(classify_ac, axis=1)

                    total_orders = ac_summary.shape[0]
                    fully = ac_summary[ac_summary['Status'] == 'Fully Shipped']['Order No.'].tolist()
                    partial = ac_summary[ac_summary['Status'] == 'Partially Shipped']['Order No.'].tolist()
                    not_shipped = ac_summary[ac_summary['Status'] == 'Not Shipped']['Order No.'].tolist()

                    st.markdown(f"### 📦 Aircraft Summary for `{aircraft_code}`")
                    st.markdown(f"- **Total Orders Placed**: {total_orders}")
                    if 'PO Date' in ac_summary.columns:
                        st.markdown(f"- **Order Dates**: {', '.join(sorted(set(ac_summary['PO Date'].astype(str))))}")

                    st.markdown(f"- ✅ **Fully Shipped Orders** ({len(fully)}): {', '.join(fully) if fully else 'None'}")
                    st.markdown(f"- 🟡 **Partially Shipped Orders** ({len(partial)}): {', '.join(partial) if partial else 'None'}")
                    st.markdown(f"- 🔴 **Not Yet Shipped Orders** ({len(not_shipped)}): {', '.join(not_shipped) if not_shipped else 'None'}")

                    with st.expander("📋 Full Order-wise Summary"):
                        st.dataframe(ac_summary)






            else:
                st.info(
                    "🤖 I didn't understand that. Try keywords like 'partial grn', 'not shipped', 'supplier XYZ', or enter a part number.")





    except Exception as e:
        st.error(f"Error processing file: {e}")



