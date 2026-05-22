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
# 2. STATE INITIALIZATION & DATA PRESETS
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
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# ==========================================
# 3. CORE DYNAMIC PRICING ENGINE PIPELINE
# ==========================================
def recalculate_dynamic_prices():
    """Applies strict automated dynamic pricing algorithms across the entire catalog."""
    df = st.session_state.products.copy()
    
    for idx, row in df.iterrows():
        base = float(row['base_price'])
        expiry = int(row['days_to_expiry'])
        stock = int(row['stock'])
        
        if expiry == 0:
            final_price = 0.0
        elif expiry <= 2:
            final_price = base * 0.50
        elif expiry <= 4:
            final_price = base * 0.75
        elif stock < 5 and stock > 0:
            final_price = base * 1.25
        else:
            final_price = base
            
        df.at[idx, 'current_price'] = round(final_price, 2)
        
    st.session_state.products = df

recalculate_dynamic_prices()

# ==========================================
# 4. LIFECYCLE CONTROLS
# ==========================================
def pass_one_day():
    df = st.session_state.products.copy()
    metrics = st.session_state.day_metrics.copy()
    
    for idx, row in df.iterrows():
        new_expiry = max(0, int(row['days_to_expiry']) - 1)
        current_stock = int(row['stock'])
        
        if new_expiry == 0 and current_stock > 0:
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
            
        df.at[idx, 'days_to_expiry'] = new_expiry
        df.at[idx, 'stock'] = current_stock

    st.session_state.current_day += 1
    st.session_state.products = df
    st.session_state.day_metrics = metrics
    recalculate_dynamic_prices()

def reset_store():
    st.session_state.products = pd.DataFrame(INITIAL_PRODUCTS)
    st.session_state.sales_history = []
    st.session_state.waste_history = []
    st.session_state.current_day = 1
    st.session_state.day_metrics = {"total_revenue": 0.0, "total_profit": 0.0, "total_loss": 0.0}
    recalculate_dynamic_prices()
    st.rerun()

# ==========================================
# 5. AUTHENTICATION WALL GATEKEEPER
# ==========================================
if not st.session_state.authenticated:
    # Render clean login architecture centered on screen
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    
    with c2:
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h2 style='margin-bottom:0;'>⚙️ Operational Portal Gateway</h2>
            <p style='opacity:0.6; font-size:14px;'>Inventory Spoilage Mitigation & Dynamic Pricing Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form(key="central_login_form"):
            username = st.text_input("Administrative User ID", value="admin")
            passphrase = st.text_input("Security Key Passphrase", type="password")
            login_btn = st.form_submit_button("Authenticate & Initialize Environment", use_container_width=True)
            
            if login_btn:
                if username == "admin" and passphrase == "IIM_2027_Success":
                    st.session_state.authenticated = True
                    st.success("Access Granted. Initializing pipelines...")
                    st.rerun()
                else:
                    st.error("Invalid secure credentials context.")
    st.stop() # Force execution halt so unauthorized users see absolutely nothing beyond the login form

# ==========================================
# 6. APPLICATION CANVAS (RUNS ONLY AFTER LOGGED IN)
# ==========================================
# SIDEBAR GATEWAY
st.sidebar.markdown(f"## 🏪 Operational Console <span style='font-size:14px; opacity:0.6;'>(Day {st.session_state.current_day})</span>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='margin-top:4px; margin-bottom:12px;'>", unsafe_allow_html=True)

if st.sidebar.button("🔒 Terminate Session / Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

# RECORD LIVE ORDER
if not st.session_state.products.empty:
    with st.sidebar.expander("💰 Record Live Customer Order", expanded=True):
        with st.form(key="sale_entry_form", clear_on_submit=True):
            available_items = st.session_state.products[st.session_state.products['stock'] > 0]
            if not available_items.empty:
                selected_item = st.selectbox("Product Line:", options=available_items['name'].tolist())
                quantity_sold = st.number_input("Order Quantity Unit Size:", min_value=1, value=1, step=1)
                submit_sale = st.form_submit_button("💰 Process Checkout Transaction", use_container_width=True)
                
                if submit_sale:
                    df = st.session_state.products.copy()
                    metrics = st.session_state.day_metrics.copy()
                    idx = df[df['name'] == selected_item].index[0]
                    item_row = df.loc[idx]
                    
                    if quantity_sold > item_row['stock']:
                        st.error(f"Insufficient stock. Remaining: {item_row['stock']}")
                    else:
                        actual_selling_price = float(item_row['current_price'])
                        revenue = actual_selling_price * quantity_sold
                        cost = float(item_row['purchase_cost']) * quantity_sold
                        profit = revenue - cost
                        
                        df.at[idx, 'stock'] = int(item_row['stock'] - quantity_sold)
                        metrics['total_revenue'] += revenue
                        metrics['total_profit'] += profit
                        
                        st.session_state.sales_history.append({
                            "time": len(st.session_state.sales_history) + 1, "item": selected_item,
                            "qty": quantity_sold, "rate": actual_selling_price, "total": revenue
                        })
                        st.session_state.products = df
                        st.session_state.day_metrics = metrics
                        recalculate_dynamic_prices()
                        st.rerun()
            else:
                st.write("❌ Whole warehouse out of stock.")

# LOGISTICS & AUDITS
with st.sidebar.expander("🚚 Pipeline Logistics Restocking", expanded=False):
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
            st.session_state.products = df_copy
            recalculate_dynamic_prices()
            st.success("Logistics Restocked!")
            st.rerun()
    else:
        st.info("All products currently active.")

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
        st.session_state.products = df_copy
        recalculate_dynamic_prices()
        st.success("Audit records updated.")
        st.rerun()

# MAIN VIEWBOARD CANVAS
st.markdown("<p style='color:#2563eb; font-weight:700; font-size:12px; letter-spacing:1px; margin-bottom:4px;'>PRODUCTION ANALYTICAL ENVIRONMENT</p>", unsafe_allow_html=True)
st.markdown("<h1 style='font-size:32px; font-weight:800; margin-top:0;'>Automated Inventory Spoilage Mitigation & Dynamic Pricing Engine</h1>", unsafe_allow_html=True)

m = st.session_state.day_metrics
cm1, cm2, cm3 = st.columns(3)
cm1.markdown(f"""<div style='background-color: var(--secondary-background-color); border-radius:8px; padding:18px; border:1px solid #e2e8f0; border-left:4px solid #16a34a;'><p style='opacity:0.6; font-weight:600; margin:0; font-size:13px;'>ACCUMULATED GROSS REVENUE</p><p style='color:#16a34a; font-size:26px; font-weight:800; margin:4px 0 0 0;'>₹{m['total_revenue']:,.2f}</p></div>""", unsafe_allow_html=True)
net_profit_color = "#2563eb" if m['total_profit'] >= 0 else "#dc2626"
cm2.markdown(f"""<div style='background-color: var(--secondary-background-color); border-radius:8px; padding:18px; border:1px solid #e2e8f0; border-left:4px solid {net_profit_color};'><p style='opacity:0.6; font-weight:600; margin:0; font-size:13px;'>NET SPREAD MARGIN PROFIT</p><p style='color:{net_profit_color}; font-size:26px; font-weight:800; margin:4px 0 0 0;'>₹{m['total_profit']:,.2f}</p></div>""", unsafe_allow_html=True)
cm3.markdown(f"""<div style='background-color: var(--secondary-background-color); border-radius:8px; padding:18px; border:1px solid #e2e8f0; border-left:4px solid #dc2626;'><p style='opacity:0.6; font-weight:600; margin:0; font-size:13px;'>WRITTEN-OFF PERISHABLE LOSS</p><p style='color:#dc2626; font-size:26px; font-weight:800; margin:4px 0 0 0;'>₹{m['total_loss']:,.2f}</p></div>""", unsafe_allow_html=True)

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
        fig_financials = px.bar(chart_data, x="Financial Metric", y="Value (₹)", color="Color Theme", text=chart_data["Value (₹)"].apply(lambda x: f"₹{x:,.2f}"), color_discrete_map={"Revenue": "#16a34a", "Profit": "#2563eb", "Loss": "#dc2626"}, height=280)
        fig_financials.update_traces(textposition='outside', cliponaxis=False)
        fig_financials.update_layout(showlegend=False, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title=None), yaxis=dict(title=None, gridcolor="rgba(100,116,139,0.1)"))
        st.plotly_chart(fig_financials, use_container_width=True)
    with g_col2:
        if st.session_state.waste_history:
            waste_analysis_df = pd.DataFrame(st.session_state.waste_history)
            category_waste = waste_analysis_df.groupby("Category")["Total Loss (₹)"].sum().reset_index()
            fig_waste = px.bar(category_waste, y="Category", x="Total Loss (₹)", orientation='h', color_discrete_sequence=["#ef4444"], text=category_waste["Total Loss (₹)"].apply(lambda x: f"₹{x:,.0f}"), height=280)
            fig_waste.update_layout(margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(title=None), xaxis=dict(title=None, gridcolor="rgba(100,116,139,0.1)"))
            st.plotly_chart(fig_waste, use_container_width=True)
        else:
            st.info("System Balance Maintained: No capital loss logged.")

with tab_shelf:
    def display_status(row):
        if int(row['days_to_expiry']) == 0: return "❌ EXPIRED (Written Off)"
        elif int(row['stock']) == 0: return "⚠️ VACUUM OUT (Stock Empty)"
        elif int(row['days_to_expiry']) <= 2: return "🔥 CRITICAL MARKDOWN (50% OFF)"
        elif int(row['days_to_expiry']) <= 4: return "📉 WARNING MARKDOWN (25% OFF)"
        elif int(row['stock']) < 5: return "⚡ SUPPLY DEFICIT (25% Surge Premium)"
        else: return "✅ STABLE EQUILIBRIUM"

    grid_df = st.session_state.products.copy()
    grid_df['Operational Status'] = grid_df.apply(display_status, axis=1)
    grid_df.columns = ['ID', 'Product Description', 'Base Price (₹)', 'Elastic Price (₹)', 'Stock Count', 'Expiry Horizon (Days)', 'Operational Category', 'Wholesale Cost (₹)', 'Operational Status']
    st.dataframe(grid_df[['Operational Category', 'Product Description', 'Stock Count', 'Expiry Horizon (Days)', 'Base Price (₹)', 'Elastic Price (₹)', 'Operational Status']], use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)
col_ledger, col_pipelines = st.columns([1.6, 1])

with col_ledger:
    st.markdown("<h3 style='font-size:18px; font-weight:700;'>📝 Active Operational Bill Book</h3>", unsafe_allow_html=True)
    if st.session_state.sales_history:
        log_df = pd.DataFrame(st.session_state.sales_history)
        log_df.columns = ['Txn ID', 'Asset Description', 'Units Dispatched', 'Strike Rate (₹)', 'Gross Receipt Total (₹)']
        st.dataframe(log_df, use_container_width=True, hide_index=True, height=180)

with col_pipelines:
    st.markdown("<h3 style='font-size:18px; font-weight:700;'>⏳ Lifecycle Operations</h3>", unsafe_allow_html=True)
    btn_c1, btn_c2 = st.columns(2)
    with btn_c1:
        if st.button("🌙 Step Operational Day", type="primary", use_container_width=True):
            pass_one_day()
            st.rerun()
    with btn_c2:
        if st.button("🔄 Clear State & Reset", use_container_width=True):
            reset_store()