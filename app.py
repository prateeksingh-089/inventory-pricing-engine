import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ==========================================
# 1. ENTERPRISE PAGE CONFIGURATION SETUP
# ==========================================
st.set_page_config(
    page_title="Automated Inventory Spoilage Mitigation Engine",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# 2. SECURE AUTHENTICATION GATEWAY
# ==========================================
def check_password():
    """Returns True if the user is authenticated via local session state variables."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        # Using var(--text-color) and var(--secondary-background-color) for full theme responsiveness
        st.markdown("""
        <div style='background-color: var(--secondary-background-color); padding:30px; border-radius:12px; border:1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05); text-align:center;'>
            <h1 style='color: var(--text-color); margin:0; font-size: 26px; font-weight:800; letter-spacing: 1px;'>LOGIN</h1>
            <p style='color: var(--text-color); opacity: 0.7; font-size:13px; margin-top:8px; margin-bottom:0;'>Enter administrative credentials to launch operations</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        username = st.text_input("Username ID", placeholder="e.g., admin")
        password = st.text_input("Password", type="password", placeholder="••••••••••••")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign In & Launch Engine", type="primary", use_container_width=True):
            if username == "admin" and password == "2626228":
                st.session_state.authenticated = True
                st.success("Authentication successful! Initializing system arrays...")
                st.rerun()
            else:
                st.error("❌ Access Denied. Invalid credentials.")
                
    return False

if check_password():

    # ==========================================
    # 3. PRE-LOADED STOCHASTIC DATA PRESETS
    # ==========================================
    INITIAL_PRODUCTS = [
        {"id": 1, "name": "Avocados (Pack of 3)", "base_price": 150.0, "current_price": 150.0, "stock": 40, "days_to_expiry": 7, "category": "🥦 Fruits & Veggies", "purchase_cost": 100.0},
        {"id": 2, "name": "Fresh Milk 1L", "base_price": 60.0, "current_price": 60.0, "stock": 15, "days_to_expiry": 2, "category": "🥛 Milk & Dairy", "purchase_cost": 45.0},
        {"id": 3, "name": "Gourmet Sourdough Bread", "base_price": 120.0, "current_price": 120.0, "stock": 20, "days_to_expiry": 3, "category": "🍞 Bread & Bakery", "purchase_cost": 80.0},
        {"id": 4, "name": "Strawberries 250g", "base_price": 200.0, "current_price": 200.0, "stock": 8, "days_to_expiry": 1, "category": "🥦 Fruits & Veggies", "purchase_cost": 140.0},
        {"id": 5, "name": "Mobile Charging Cable", "base_price": 450.0, "current_price": 450.0, "stock": 50, "days_to_expiry": 365, "category": "⚡ Electronics", "purchase_cost": 200.0},
        {"id": 6, "name": "AA Batteries (4-Pack)", "base_price": 180.0, "current_price": 180.0, "stock": 35, "days_to_expiry": 365, "category": "⚡ Electronics", "purchase_cost": 100.0},
        {"id": 7, "name": "Dishwash Liquid 500ml", "base_price": 159.0, "current_price": 159.0, "stock": 25, "days_to_expiry": 180, "category": "🧹 Cleaning Items", "purchase_cost": 110.0},
        {"id": 8, "name": "Cleaning Wipes Pack", "base_price": 99.0, "current_price": 99.0, "stock": 12, "days_to_expiry": 90, "category": "🧹 Cleaning Items", "purchase_cost": 60.0},
    ]

    if 'products' not in st.session_state:
        st.session_state.products = pd.DataFrame(INITIAL_PRODUCTS)
    if 'sales_history' not in st.session_state:
        st.session_state.sales_history = []
    if 'waste_history' not in st.session_state:
        st.session_state.waste_history = []
    if 'current_day' not in st.session_state:
        st.session_state.current_day = 1
    if 'day_metrics' not in st.session_state:
        st.session_state.day_metrics = {"total_revenue": 0.0, "total_profit": 0.0, "total_loss": 0.0}

    # ==========================================
    # 4. DATA CALCULATION PIPELINES
    # ==========================================
    def pass_one_day():
        df = st.session_state.products.copy()
        metrics = st.session_state.day_metrics.copy()
        
        for idx, row in df.iterrows():
            new_expiry = max(0, int(row['days_to_expiry']) - 1)
            current_stock = int(row['stock'])
            dynamic_price = float(row['base_price'])
            
            if new_expiry == 0:
                dynamic_price = 0.0
                if current_stock > 0:
                    calculated_loss = float(current_stock * row['purchase_cost'])
                    metrics['total_loss'] += calculated_loss
                    st.session_state.waste_history.append({
                        "Day Detected": f"Day {st.session_state.current_day}",
                        "Item Name": row['name'],
                        "Category": row['category'],
                        "Qty Spoiled": current_stock,
                        "Total Loss (₹)": calculated_loss
                    })
                    current_stock = 0 
            elif new_expiry <= 2:
                dynamic_price = float(row['base_price'] * 0.50) 
            elif new_expiry <= 4:
                dynamic_price = float(row['base_price'] * 0.75) 
            elif current_stock < 5:
                dynamic_price = float(row['base_price'] * 1.25) 

            df.at[idx, 'days_to_expiry'] = new_expiry
            df.at[idx, 'stock'] = current_stock
            df.at[idx, 'current_price'] = round(dynamic_price, 2)

        st.session_state.current_day += 1
        st.session_state.products = df
        st.session_state.day_metrics = metrics

    def reset_store():
        st.session_state.products = pd.DataFrame(INITIAL_PRODUCTS)
        st.session_state.sales_history = []
        st.session_state.waste_history = []
        st.session_state.current_day = 1
        st.session_state.day_metrics = {"total_revenue": 0.0, "total_profit": 0.0, "total_loss": 0.0}
        st.rerun()

    # ==========================================
    # 5. SIDEBAR CONTROL CENTER
    # ==========================================
    st.sidebar.markdown(f"## 🏪 Control Center <span style='font-size:15px; color:var(--text-color); opacity:0.6;'>(Day {st.session_state.current_day})</span>", unsafe_allow_html=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.products.empty:
        
        with st.sidebar.expander("🛒 Record Customer Transaction", expanded=True):
            with st.form(key="sale_entry_form", clear_on_submit=True):
                selected_item = st.selectbox("Product:", options=st.session_state.products['name'].tolist())
                quantity_sold = st.number_input("Quantity:", min_value=1, value=1, step=1)
                submit_sale = st.form_submit_button("💰 Complete Sale", use_container_width=True)
                
                if submit_sale:
                    df = st.session_state.products.copy()
                    metrics = st.session_state.day_metrics.copy()
                    idx = df[df['name'] == selected_item].index[0]
                    item_row = df.loc[idx]
                    
                    if item_row['stock'] == 0:
                        st.error(f"Out of stock.")
                    elif quantity_sold > item_row['stock']:
                        st.error(f"Insufficient stock. Remaining: {item_row['stock']}")
                    else:
                        actual_selling_price = float(item_row['current_price'])
                        revenue = actual_selling_price * quantity_sold
                        cost = float(item_row['purchase_cost']) * quantity_sold
                        profit = revenue - cost
                        
                        df.at[idx, 'stock'] = int(item_row['stock'] - quantity_sold)
                        if int(df.at[idx, 'stock']) < 5 and int(df.at[idx, 'days_to_expiry']) > 4:
                            df.at[idx, 'current_price'] = round(float(item_row['base_price'] * 1.25), 2)
                        
                        metrics['total_revenue'] += revenue
                        metrics['total_profit'] += profit
                        st.session_state.sales_history.append({
                            "time": len(st.session_state.sales_history) + 1, "item": selected_item,
                            "qty": quantity_sold, "rate": actual_selling_price, "total": revenue
                        })
                        st.session_state.products = df
                        st.session_state.day_metrics = metrics
                        st.rerun()

        with st.sidebar.expander("🔄 Reorder & Restock Broken Rows", expanded=False):
            spoiled_or_empty_options = st.session_state.products[
                (st.session_state.products['stock'] == 0) | (st.session_state.products['days_to_expiry'] == 0)
            ]['name'].tolist()
            
            if spoiled_or_empty_options:
                restock_item = st.selectbox("Select Empty/Expired Row:", options=spoiled_or_empty_options)
                restock_idx = st.session_state.products[st.session_state.products['name'] == restock_item].index[0]
                fresh_stock = st.number_input("Restock Quantity Unit Size:", min_value=1, value=20, step=1)
                fresh_expiry = st.number_input("Freshness Lifetime (Days):", min_value=1, value=7, step=1)
                
                if st.button("🚚 Deploy Supply Pipeline", use_container_width=True, type="primary"):
                    df_copy = st.session_state.products.copy()
                    df_copy.at[restock_idx, 'stock'] = int(fresh_stock)
                    df_copy.at[restock_idx, 'days_to_expiry'] = int(fresh_expiry)
                    df_copy.at[restock_idx, 'current_price'] = float(df_copy.at[restock_idx, 'base_price'])
                    st.session_state.products = df_copy
                    st.success("Logistics Restocked Successfully!")
                    st.rerun()
            else:
                st.info("All products are currently active and stocked.")

        with st.sidebar.expander("🔧 Manual Inventory Audit Overrides", expanded=False):
            stock_target_item = st.selectbox("Target Product Row:", options=st.session_state.products['name'].tolist(), key="stock_selector")
            prod_idx = st.session_state.products[st.session_state.products['name'] == stock_target_item].index[0]
            current_physical_stock = int(st.session_state.products.loc[prod_idx, 'stock'])
            new_stock_count = st.number_input(f"Override Stock Allocation", min_value=0, value=current_physical_stock, step=1, key="stock_input")
            current_expiry_days = int(st.session_state.products.loc[prod_idx, 'days_to_expiry'])
            new_expiry_days = st.number_input(f"Override Expiry Index (Days)", min_value=0, value=current_expiry_days, step=1, key="expiry_input")
            
            if st.button("💾 Apply Manual Audit Adjustments", use_container_width=True):
                df_copy = st.session_state.products.copy()
                df_copy.at[prod_idx, 'stock'] = int(new_stock_count)
                df_copy.at[prod_idx, 'days_to_expiry'] = int(new_expiry_days)
                
                updated_row = df_copy.loc[prod_idx]
                eval_price = float(updated_row['base_price'])
                if int(updated_row['days_to_expiry']) == 0:
                    eval_price = 0.0
                elif int(updated_row['days_to_expiry']) <= 2:
                    eval_price = float(updated_row['base_price'] * 0.50)
                elif int(updated_row['days_to_expiry']) <= 4:
                    eval_price = float(updated_row['base_price'] * 0.75)
                elif int(new_stock_count) < 5 and int(updated_row['days_to_expiry']) > 0:
                    eval_price = float(updated_row['base_price'] * 1.25)
                    
                df_copy.at[prod_idx, 'current_price'] = round(eval_price, 2)
                st.session_state.products = df_copy
                st.success("Audit records updated.")
                st.rerun()

        with st.sidebar.expander("📥 Add New Strategic Product Line", expanded=False):
            with st.form(key="add_new_catalog_form", clear_on_submit=True):
                new_name = st.text_input("Product Name Identifier")
                new_cat = st.selectbox("Operational Category Segment", ["🥦 Fruits & Veggies", "🥛 Milk & Dairy", "🍞 Bread & Bakery", "⚡ Electronics", "🧹 Cleaning Items", "📦 Other Essentials"])
                new_cost = st.number_input("Wholesale Purchase Price (₹)", min_value=1.0, value=50.0, step=1.0)
                new_base = st.number_input("Standard Target Retail Price (₹)", min_value=1.0, value=75.0, step=1.0)
                new_stock = st.number_input("Initial Shelf Entry Stock Count", min_value=1, value=20, step=1)
                new_expiry = st.number_input("Shelf Life Expiration Horizon (Days)", min_value=1, value=10, step=1)
                add_btn = st.form_submit_button("➕ Ingest Line Item", use_container_width=True)
                
                if add_btn and new_name:
                    current_df = st.session_state.products.copy()
                    next_id = int(current_df['id'].max() + 1) if not current_df.empty else 1
                    new_row = {
                        "id": next_id, "name": new_name, "base_price": float(new_base), "current_price": float(new_base), 
                        "stock": int(new_stock), "days_to_expiry": int(new_expiry), "category": new_cat, "purchase_cost": float(new_cost)
                    }
                    st.session_state.products = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
                    st.sidebar.success(f"Appended {new_name} smoothly.")
                    st.rerun()

        st.sidebar.markdown("<br><br>", unsafe_allow_html=True)
        if st.sidebar.button("🚪 Terminate Secure Session", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # ==========================================
    # 6. CANVAS DASHBOARD LAYOUT
    # ==========================================
    st.markdown("<p style='color:#2563eb; font-weight:700; font-size:12px; letter-spacing:1px; margin-bottom:4px;'>REAL-TIME SIMULATION CORE</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:32px; font-weight:800; color: var(--text-color); margin-top:0;'>Automated Inventory Spoilage Mitigation & Dynamic Pricing Engine</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--text-color); opacity: 0.7; font-size:14px; margin-bottom:24px;'>Operations optimization framework modeling elastic markdowns, real-time customer checkouts, and material loss tracking registers.</p>", unsafe_allow_html=True)

    # ROW SECTION 1: METRIC SCORECARDS GRID (UPDATED WITH VARIABLE THEMING)
    m = st.session_state.day_metrics
    cm1, cm2, cm3 = st.columns(3)

    cm1.markdown(f"""
    <div style='background-color: var(--secondary-background-color); border-radius:8px; padding:18px; border:1px solid #e2e8f0; border-left:4px solid #16a34a; box-shadow:0 1px 3px rgba(0,0,0,0.02);'>
        <p style='color: var(--text-color); opacity:0.6; font-weight:600; margin:0; font-size:13px; letter-spacing:0.5px;'>ACCUMULATED GROSS REVENUE</p>
        <p style='color:#16a34a; font-size:26px; font-weight:800; margin:4px 0 0 0;'>₹{m['total_revenue']:,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

    net_profit_color = "#2563eb" if m['total_profit'] >= 0 else "#dc2626"
    cm2.markdown(f"""
    <div style='background-color: var(--secondary-background-color); border-radius:8px; padding:18px; border:1px solid #e2e8f0; border-left:4px solid {net_profit_color}; box-shadow:0 1px 3px rgba(0,0,0,0.02);'>
        <p style='color: var(--text-color); opacity:0.6; font-weight:600; margin:0; font-size:13px; letter-spacing:0.5px;'>NET SPREAD MARGIN PROFIT</p>
        <p style='color:{net_profit_color}; font-size:26px; font-weight:800; margin:4px 0 0 0;'>₹{m['total_profit']:,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

    cm3.markdown(f"""
    <div style='background-color: var(--secondary-background-color); border-radius:8px; padding:18px; border:1px solid #e2e8f0; border-left:4px solid #dc2626; box-shadow:0 1px 3px rgba(0,0,0,0.02);'>
        <p style='color: var(--text-color); opacity:0.6; font-weight:600; margin:0; font-size:13px; letter-spacing:0.5px;'>WRITTEN-OFF PERISHABLE LOSS</p>
        <p style='color:#dc2626; font-size:26px; font-weight:800; margin:4px 0 0 0;'>₹{m['total_loss']:,.2f}</p>
    </div>
    """, unsafe_allow_html=True)

    # ROW SECTION 2: TABBED VISUALIZATION ENGINE
    st.markdown("<br>", unsafe_allow_html=True)
    tab_graphs, tab_shelf = st.tabs(["📊 Dynamic Analytical Graphs", "📋 Perpetual Inventory Shelf Monitor"])

    with tab_graphs:
        chart_data = pd.DataFrame({
            "Financial Metric": ["Gross Revenue", "Net Profit", "Spoilage Capital Loss"],
            "Value (₹)": [m['total_revenue'], m['total_profit'], m['total_loss']],
            "Color Theme": ["Revenue", "Profit", "Loss"]
        })
        
        g_col1, g_col2 = st.columns([1.2, 1])
        with g_col1:
            st.markdown("<h4 style='color: var(--text-color); font-size:16px; font-weight:700;'>Session Core Financial Health Status</h4>", unsafe_allow_html=True)
            fig_financials = px.bar(
                chart_data, x="Financial Metric", y="Value (₹)", color="Color Theme",
                text=chart_data["Value (₹)"].apply(lambda x: f"₹{x:,.2f}"),
                color_discrete_map={"Revenue": "#16a34a", "Profit": "#2563eb", "Loss": "#dc2626"},
                height=280
            )
            fig_financials.update_traces(textposition='outside', cliponaxis=False)
            
            # Updating chart properties to blend smoothly into light or dark canvases
            fig_financials.update_layout(
                showlegend=False, margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#64748b"),
                xaxis=dict(title=None), yaxis=dict(title=None, gridcolor="rgba(100,116,139,0.1)")
            )
            st.plotly_chart(fig_financials, use_container_width=True)

        with g_col2:
            st.markdown("<h4 style='color: var(--text-color); font-size:16px; font-weight:700;'>Perishable Capital Waste Breakdown</h4>", unsafe_allow_html=True)
            if st.session_state.waste_history:
                waste_analysis_df = pd.DataFrame(st.session_state.waste_history)
                category_waste = waste_analysis_df.groupby("Category")["Total Loss (₹)"].sum().reset_index()
                
                fig_waste = px.bar(
                    category_waste, y="Category", x="Total Loss (₹)", orientation='h',
                    color_discrete_sequence=["#ef4444"],
                    text=category_waste["Total Loss (₹)"].apply(lambda x: f"₹{x:,.0f}"),
                    height=280
                )
                fig_waste.update_traces(textposition='inside')
                fig_waste.update_layout(
                    margin=dict(l=10, r=10, t=10, b=10),
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#64748b"),
                    yaxis=dict(title=None), xaxis=dict(title=None, gridcolor="rgba(100,116,139,0.1)")
                )
                st.plotly_chart(fig_waste, use_container_width=True)
            else:
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.info("System Balance Maintained: No capital loss from spoilage logged in this session framework yet.")

    with tab_shelf:
        def display_status(row):
            if int(row['days_to_expiry']) == 0:
                return "❌ EXPIRED (Written Off)"
            elif int(row['stock']) == 0:
                return "⚠️ VACUUM OUT (Stock Empty)"
            elif float(row['current_price']) < float(row['base_price']):
                return "📉 CLEARNING MARKDOWN ACTIVE"
            elif int(row['stock']) < 5:
                return "🔥 SUPPLY DEFICIT (Surge Premium)"
            else:
                return "✅ STABLE EQUILIBRIUM"

        if not st.session_state.products.empty:
            grid_df = st.session_state.products.copy()
            grid_df['Operational Status'] = grid_df.apply(display_status, axis=1)
            grid_df.columns = ['ID', 'Product Description', 'Base Price (₹)', 'Elastic Price (₹)', 'Stock Count', 'Expiry Horizon (Days)', 'Operational Category', 'Wholesale Cost (₹)', 'Operational Status']
            
            st.dataframe(
                grid_df[['Operational Category', 'Product Description', 'Stock Count', 'Expiry Horizon (Days)', 'Base Price (₹)', 'Elastic Price (₹)', 'Operational Status']],
                use_container_width=True, hide_index=True
            )

    # ROW SECTION 3: SYSTEM TRANSACTION CONTROLS & LOGS LEDGER
    st.markdown("<br>", unsafe_allow_html=True)
    col_ledger, col_pipelines = st.columns([1.6, 1])

    with col_ledger:
        st.markdown("<h3 style='font-size:18px; font-weight:700; color: var(--text-color); margin-bottom:12px;'>📝 Active Operational Bill Book</h3>", unsafe_allow_html=True)
        if st.session_state.sales_history:
            log_df = pd.DataFrame(st.session_state.sales_history)
            log_df.columns = ['Txn ID', 'Asset Description', 'Units Dispatched', 'Strike Rate (₹)', 'Gross Receipt Total (₹)']
            st.dataframe(log_df, use_container_width=True, hide_index=True, height=180)
        else:
            st.caption("No micro-transactions dispatched during this running window framework.")

    with col_pipelines:
        st.markdown("<h3 style='font-size:18px; font-weight:700; color: var(--text-color); margin-bottom:12px;'>⏳ End-of-Day Closures</h3>", unsafe_allow_html=True)
        st.caption("Clicking below triggers programmatic date-stepping, calculating automated macro decay steps across item sets.")
        
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("🌙 Step Operational Day", type="primary", use_container_width=True):
                pass_one_day()
                st.rerun()
        with btn_c2:
            if st.button("🔄 Clear State & Reset", use_container_width=True):
                reset_store()

    # FOOTER LOG DATA GRID: HISTORICAL AUDIT
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:18px; font-weight:700; color: var(--text-color); margin-bottom:4px;'>🗑️ Spoilage Auditing Data Register</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: var(--text-color); opacity: 0.7; font-size:13px; margin-bottom:12px;'>Permanent chronological ledger documenting asset write-offs at lifecycle bounds.</p>", unsafe_allow_html=True)

    if st.session_state.waste_history:
        waste_df = pd.DataFrame(st.session_state.waste_history)
        st.dataframe(
            waste_df[['Day Detected', 'Category', 'Item Name', 'Qty Spoiled', 'Total Loss (₹)']],
            use_container_width=True, hide_index=True
        )
    else:
        st.info("Optimization Equilibrium Achieved: Zero expired items sitting inside the write-off arrays.")