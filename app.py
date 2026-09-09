import hashlib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 1. PAGE SETUP & DOM HARDENING
# ==========================================
st.set_page_config(
    page_title="Enterprise Inventory Spoilage Mitigation Engine",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
        #MainMenu {visibility: hidden !important;}
        footer {visibility: hidden !important;}
        .stDeployButton {display:none !important;}
        [data-testid="stAppDeployButton"] {display: none !important;}
        div[data-testid="stDecoration"] {display: none !important;}
        button[title="Manage app"] {display: none !important;}
        iframe[title="Manage app"] {display: none !important;}
        header[data-testid="stHeader"] {background: transparent !important;}
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 2. RBAC CREDENTIAL REPOSITORY & CRYPTO
# ==========================================
# PBKDF2-HMAC-SHA256 salted credentials
USER_REGISTRY = {
    "admin": {
        "salt": "a4f891e2b3c4d5e6",
        # Hashed password for "admin2026"
        "hash": hashlib.pbkdf2_hmac(
            "sha256", "admin2026".encode(), b"a4f891e2b3c4d5e6", 100000
        ).hex(),
        "role": "admin",
        "name": "System Administrator",
    },
    "cashier": {
        "salt": "f1e2d3c4b5a69788",
        # Hashed password for "pos123"
        "hash": hashlib.pbkdf2_hmac(
            "sha256", "pos123".encode(), b"f1e2d3c4b5a69788", 100000
        ).hex(),
        "role": "cashier",
        "name": "Terminal Cashier",
    },
}


def verify_login(user: str, secret: str):
    user_data = USER_REGISTRY.get(user.strip().lower())
    if not user_data:
        return None
    test_hash = hashlib.pbkdf2_hmac(
        "sha256", secret.strip().encode(), user_data["salt"].encode(), 100000
    ).hex()
    if test_hash == user_data["hash"]:
        return {"user": user, "role": user_data["role"], "name": user_data["name"]}
    return None


# ==========================================
# 3. STATE INITIALIZATION
# ==========================================
INITIAL_PRODUCTS = [
    {"id": 1, "name": "Avocados (Pack of 3)", "base_price": 150.0, "current_price": 150.0, "stock": 40, "days_to_expiry": 7, "category": "🥦 Fruits & Veggies", "purchase_cost": 100.0, "base_demand": 4.0},
    {"id": 2, "name": "Fresh Milk 1L", "base_price": 60.0, "current_price": 60.0, "stock": 15, "days_to_expiry": 2, "category": "🥛 Milk & Dairy", "purchase_cost": 45.0, "base_demand": 6.0},
    {"id": 3, "name": "Gourmet Sourdough Bread", "base_price": 120.0, "current_price": 120.0, "stock": 20, "days_to_expiry": 3, "category": "🍞 Bread & Bakery", "purchase_cost": 80.0, "base_demand": 5.0},
    {"id": 4, "name": "Strawberries 250g", "base_price": 200.0, "current_price": 200.0, "stock": 8, "days_to_expiry": 1, "category": "🥦 Fruits & Veggies", "purchase_cost": 140.0, "base_demand": 3.0},
    {"id": 5, "name": "Mobile Charging Cable", "base_price": 450.0, "current_price": 450.0, "stock": 50, "days_to_expiry": 365, "category": "⚡ Electronics", "purchase_cost": 200.0, "base_demand": 2.0},
    {"id": 6, "name": "AA Batteries (4-Pack)", "base_price": 180.0, "current_price": 180.0, "stock": 35, "days_to_expiry": 365, "category": "⚡ Electronics", "purchase_cost": 100.0, "base_demand": 3.0},
    {"id": 7, "name": "Dishwash Liquid 500ml", "base_price": 159.0, "current_price": 159.0, "stock": 25, "days_to_expiry": 180, "category": "🧹 Cleaning Items", "purchase_cost": 110.0, "base_demand": 2.5},
    {"id": 8, "name": "Cleaning Wipes Pack", "base_price": 99.0, "current_price": 99.0, "stock": 12, "days_to_expiry": 90, "category": "🧹 Cleaning Items", "purchase_cost": 60.0, "base_demand": 2.0},
]


def recalculate_dynamic_prices():
    df = st.session_state.products
    base = df["base_price"]
    expiry = df["days_to_expiry"]
    stock = df["stock"]

    conditions = [
        expiry == 0,
        expiry <= 2,
        expiry <= 4,
        (stock < 5) & (stock > 0),
    ]
    choices = [0.0, base * 0.50, base * 0.75, base * 1.25]
    df["current_price"] = np.select(conditions, choices, default=base).round(2)
    st.session_state.products = df


if "products" not in st.session_state:
    st.session_state.products = pd.DataFrame(INITIAL_PRODUCTS)
    recalculate_dynamic_prices()

if "sales_history" not in st.session_state:
    st.session_state.sales_history = []
if "waste_history" not in st.session_state:
    st.session_state.waste_history = []
if "current_day" not in st.session_state:
    st.session_state.current_day = 1
if "day_metrics" not in st.session_state:
    st.session_state.day_metrics = {"total_revenue": 0.0, "total_profit": 0.0, "total_loss": 0.0}
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

# ==========================================
# 4. PRICE ELASTICITY SIMULATION ENGINE
# ==========================================
def simulate_daily_sales():
    """Simulates market demand based on price elasticity (E = -1.5)."""
    df = st.session_state.products.copy()
    metrics = st.session_state.day_metrics.copy()
    elasticity_coefficient = -1.5

    for idx, row in df.iterrows():
        stock = int(row["stock"])
        expiry = int(row["days_to_expiry"])
        if stock <= 0 or expiry <= 0:
            continue

        base_p = float(row["base_price"])
        curr_p = float(row["current_price"])
        base_d = float(row.get("base_demand", 3.0))

        # Relative price change
        price_ratio = curr_p / base_p
        
        # Expected demand adjusted for price sensitivity
        # Q = Q0 * (P / P0) ^ E
        demand_factor = np.power(price_ratio, elasticity_coefficient)
        simulated_demand = int(np.random.poisson(lam=max(0.5, base_d * demand_factor)))
        units_sold = min(stock, simulated_demand)

        if units_sold > 0:
            rev = curr_p * units_sold
            cost = float(row["purchase_cost"]) * units_sold
            profit = rev - cost

            df.at[idx, "stock"] = stock - units_sold
            metrics["total_revenue"] += rev
            metrics["total_profit"] += profit

            st.session_state.sales_history.append(
                {
                    "Txn ID": f"TXN-D{st.session_state.current_day}-{len(st.session_state.sales_history)+1:04d}",
                    "Day": f"Day {st.session_state.current_day}",
                    "Asset Description": row["name"],
                    "Units Dispatched": units_sold,
                    "Strike Rate (₹)": curr_p,
                    "Gross Receipt Total (₹)": rev,
                }
            )

    st.session_state.products = df
    st.session_state.day_metrics = metrics


def pass_one_day():
    simulate_daily_sales()
    df = st.session_state.products.copy()
    metrics = st.session_state.day_metrics.copy()

    for idx, row in df.iterrows():
        new_expiry = max(0, int(row["days_to_expiry"]) - 1)
        current_stock = int(row["stock"])

        if new_expiry == 0 and current_stock > 0:
            loss = float(current_stock * row["purchase_cost"])
            metrics["total_loss"] += loss
            st.session_state.waste_history.append(
                {
                    "Day Detected": f"Day {st.session_state.current_day}",
                    "Item Name": row["name"],
                    "Category": row["category"],
                    "Qty Spoiled": current_stock,
                    "Total Loss (₹)": loss,
                }
            )
            current_stock = 0

        df.at[idx, "days_to_expiry"] = new_expiry
        df.at[idx, "stock"] = current_stock

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
# 5. AUTHENTICATION GATEWAY
# ==========================================
if not st.session_state.auth_user:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    _, c2, _ = st.columns([1, 1.4, 1])
    with c2:
        st.markdown(
            """
            <div style='text-align: center; margin-bottom: 20px;'>
                <h2 style='margin-bottom:0;'>⚙️ Operational Portal Gateway</h2>
                <p style='opacity:0.6; font-size:14px;'>Inventory Spoilage Mitigation & Dynamic Pricing Platform</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.form(key="login_form"):
            user_input = st.text_input("User ID", placeholder="admin or cashier")
            pass_input = st.text_input("Passphrase", type="password")
            submitted = st.form_submit_button("Authenticate Session", use_container_width=True)
            if submitted:
                auth = verify_login(user_input, pass_input)
                if auth:
                    st.session_state.auth_user = auth
                    st.rerun()
                else:
                    st.error("Authentication failed. Invalid username or security passphrase.")
        st.info("Demo Roles: `admin` (pwd: `admin2026`) | `cashier` (pwd: `pos123`)")
    st.stop()

# Role-check variable
current_role = st.session_state.auth_user["role"]
user_label = st.session_state.auth_user["name"]

# ==========================================
# 6. SIDEBAR CONTROLS (RBAC GATED)
# ==========================================
st.sidebar.markdown(
    f"## 🏪 Console <span style='font-size:13px; opacity:0.6;'>(Day {st.session_state.current_day})</span>",
    unsafe_allow_html=True,
)
st.sidebar.caption(f"Authenticated as: **{user_label}** (`{current_role.upper()}`)")
st.sidebar.markdown("<hr style='margin:8px 0;'>", unsafe_allow_html=True)

if st.sidebar.button("🔒 Sign Out", use_container_width=True):
    st.session_state.auth_user = None
    st.rerun()

# 6.1 RECORD TRANSACTION (Accessible to Cashier & Admin)
with st.sidebar.expander("💰 POS Manual Checkout", expanded=True):
    with st.form(key="sale_entry_form", clear_on_submit=True):
        active_items = st.session_state.products[
            (st.session_state.products["stock"] > 0) & (st.session_state.products["days_to_expiry"] > 0)
        ]
        if not active_items.empty:
            selected_item = st.selectbox("Product Line:", options=active_items["name"].tolist())
            qty_sold = st.number_input("Units:", min_value=1, value=1, step=1)
            
            if st.form_submit_button("Process Sale Transaction", use_container_width=True):
                df = st.session_state.products.copy()
                metrics = st.session_state.day_metrics.copy()
                idx = df[df["name"] == selected_item].index[0]
                item_row = df.loc[idx]

                if qty_sold > item_row["stock"]:
                    st.error(f"Insufficient stock. Available: {item_row['stock']}")
                else:
                    selling_price = float(item_row["current_price"])
                    rev = selling_price * qty_sold
                    cost = float(item_row["purchase_cost"]) * qty_sold

                    df.at[idx, "stock"] = int(item_row["stock"] - qty_sold)
                    metrics["total_revenue"] += rev
                    metrics["total_profit"] += rev - cost

                    st.session_state.sales_history.append(
                        {
                            "Txn ID": f"TXN-M{st.session_state.current_day}-{len(st.session_state.sales_history)+1:04d}",
                            "Day": f"Day {st.session_state.current_day}",
                            "Asset Description": selected_item,
                            "Units Dispatched": qty_sold,
                            "Strike Rate (₹)": selling_price,
                            "Gross Receipt Total (₹)": rev,
                        }
                    )
                    st.session_state.products = df
                    st.session_state.day_metrics = metrics
                    recalculate_dynamic_prices()
                    st.rerun()
        else:
            st.info("No salable inventory in warehouse.")

# 6.2 CATALOG INGESTION (Admin Only)
if current_role == "admin":
    with st.sidebar.expander("➕ Ingest Catalog Item", expanded=False):
        with st.form(key="add_new_catalog_form", clear_on_submit=True):
            new_name = st.text_input("Product Name:").strip()
            new_cat = st.selectbox(
                "Category:",
                [
                    "🥦 Fruits & Veggies",
                    "🥛 Milk & Dairy",
                    "🍞 Bread & Bakery",
                    "⚡ Electronics",
                    "🧹 Cleaning Items",
                    "📦 Other Essentials",
                ],
            )
            new_cost = st.number_input("Wholesale Cost (₹):", min_value=1.0, value=50.0, step=1.0)
            new_base = st.number_input("Retail Base Price (₹):", min_value=1.0, value=75.0, step=1.0)
            new_stock = st.number_input("Initial Shelf Units:", min_value=1, value=20, step=1)
            new_expiry = st.number_input("Expiry Life (Days):", min_value=1, value=10, step=1)
            new_demand = st.number_input("Base Daily Demand (Units):", min_value=0.5, value=3.0, step=0.5)

            if st.form_submit_button("Register Product Line", use_container_width=True):
                current_df = st.session_state.products.copy()
                if not new_name:
                    st.error("Item name required.")
                elif new_name.lower() in current_df["name"].str.lower().values:
                    st.error("Product already exists in catalog.")
                else:
                    next_id = int(current_df["id"].max() + 1) if not current_df.empty else 1
                    new_row = {
                        "id": next_id,
                        "name": new_name,
                        "base_price": float(new_base),
                        "current_price": float(new_base),
                        "stock": int(new_stock),
                        "days_to_expiry": int(new_expiry),
                        "category": new_cat,
                        "purchase_cost": float(new_cost),
                        "base_demand": float(new_demand),
                    }
                    st.session_state.products = pd.concat([current_df, pd.DataFrame([new_row])], ignore_index=True)
                    recalculate_dynamic_prices()
                    st.rerun()

    # 6.3 LOGISTICS RESTOCKING (Admin Only)
    with st.sidebar.expander("🚚 Logistics Restocking", expanded=False):
        depleted_items = st.session_state.products[
            (st.session_state.products["stock"] == 0) | (st.session_state.products["days_to_expiry"] == 0)
        ]["name"].tolist()

        if depleted_items:
            restock_item = st.selectbox("Depleted Item:", options=depleted_items)
            fresh_units = st.number_input("Replenish Count:", min_value=1, value=25, step=1)
            fresh_days = st.number_input("Freshness Window (Days):", min_value=1, value=7, step=1)

            if st.button("Confirm Logistics Order", use_container_width=True, type="primary"):
                idx = st.session_state.products[st.session_state.products["name"] == restock_item].index[0]
                st.session_state.products.at[idx, "stock"] = int(fresh_units)
                st.session_state.products.at[idx, "days_to_expiry"] = int(fresh_days)
                recalculate_dynamic_prices()
                st.rerun()
        else:
            st.info("No out-of-stock items requiring logistics orders.")

# ==========================================
# 7. MAIN VIEWPORT & KPI METRICS
# ==========================================
st.markdown(
    "<p style='color:#2563eb; font-weight:700; font-size:12px; letter-spacing:1px; margin-bottom:4px;'>AUTOMATED SUPPLY CHAIN ENVIRONMENT</p>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h1 style='font-size:30px; font-weight:800; margin-top:0;'>Inventory Spoilage Mitigation & Dynamic Pricing Platform</h1>",
    unsafe_allow_html=True,
)

m = st.session_state.day_metrics
cm1, cm2, cm3 = st.columns(3)
cm1.markdown(
    f"""<div style='background-color: var(--secondary-background-color); border-radius:8px; padding:16px; border:1px solid #e2e8f0; border-left:4px solid #16a34a;'><p style='opacity:0.6; font-weight:600; margin:0; font-size:12px;'>GROSS REVENUE</p><p style='color:#16a34a; font-size:24px; font-weight:800; margin:4px 0 0 0;'>₹{m['total_revenue']:,.2f}</p></div>""",
    unsafe_allow_html=True,
)
p_color = "#2563eb" if m["total_profit"] >= 0 else "#dc2626"
cm2.markdown(
    f"""<div style='background-color: var(--secondary-background-color); border-radius:8px; padding:16px; border:1px solid #e2e8f0; border-left:4px solid {p_color};'><p style='opacity:0.6; font-weight:600; margin:0; font-size:12px;'>NET PROFIT SPREAD</p><p style='color:{p_color}; font-size:24px; font-weight:800; margin:4px 0 0 0;'>₹{m['total_profit']:,.2f}</p></div>""",
    unsafe_allow_html=True,
)
cm3.markdown(
    f"""<div style='background-color: var(--secondary-background-color); border-radius:8px; padding:16px; border:1px solid #e2e8f0; border-left:4px solid #dc2626;'><p style='opacity:0.6; font-weight:600; margin:0; font-size:12px;'>WRITTEN-OFF PERISHABLE LOSS</p><p style='color:#dc2626; font-size:24px; font-weight:800; margin:4px 0 0 0;'>₹{m['total_loss']:,.2f}</p></div>""",
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)
tab_graphs, tab_shelf, tab_exports = st.tabs(
    ["📊 Dynamic Analytical Graphs", "📋 Perpetual Inventory Monitor", "📥 Audit Exports & Reports"]
)

with tab_graphs:
    chart_data = pd.DataFrame(
        {
            "Metric": ["Gross Revenue", "Net Profit", "Spoilage Capital Loss"],
            "Value": [m["total_revenue"], m["total_profit"], m["total_loss"]],
            "Type": ["Revenue", "Profit", "Loss"],
        }
    )
    g1, g2 = st.columns([1.2, 1])
    with g1:
        fig_fin = px.bar(
            chart_data,
            x="Metric",
            y="Value",
            color="Type",
            text=chart_data["Value"].apply(lambda x: f"₹{x:,.2f}"),
            color_discrete_map={"Revenue": "#16a34a", "Profit": "#2563eb", "Loss": "#dc2626"},
            height=280,
        )
        fig_fin.update_traces(textposition="outside", cliponaxis=False)
        fig_fin.update_layout(
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(title=None),
            yaxis=dict(title=None, gridcolor="rgba(100,116,139,0.1)"),
        )
        st.plotly_chart(fig_fin, use_container_width=True)
    with g2:
        if st.session_state.waste_history:
            w_df = pd.DataFrame(st.session_state.waste_history)
            cat_waste = w_df.groupby("Category")["Total Loss (₹)"].sum().reset_index()
            fig_w = px.bar(
                cat_waste,
                y="Category",
                x="Total Loss (₹)",
                orientation="h",
                color_discrete_sequence=["#ef4444"],
                text=cat_waste["Total Loss (₹)"].apply(lambda x: f"₹{x:,.0f}"),
                height=280,
            )
            fig_w.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(title=None),
                xaxis=dict(title=None, gridcolor="rgba(100,116,139,0.1)"),
            )
            st.plotly_chart(fig_w, use_container_width=True)
        else:
            st.info("Equilibrium preserved: Zero capital write-offs logged.")

with tab_shelf:
    def assign_status(row):
        if int(row["days_to_expiry"]) == 0:
            return "❌ EXPIRED"
        if int(row["stock"]) == 0:
            return "⚠️ OUT OF STOCK"
        if int(row["days_to_expiry"]) <= 2:
            return "🔥 CRITICAL (-50%)"
        if int(row["days_to_expiry"]) <= 4:
            return "📉 MARKDOWN (-25%)"
        if int(row["stock"]) < 5:
            return "⚡ SCARCITY SURGE (+25%)"
        return "✅ BALANCED"

    view_df = st.session_state.products.copy()
    view_df["Status"] = view_df.apply(assign_status, axis=1)
    st.dataframe(
        view_df[
            [
                "category",
                "name",
                "stock",
                "days_to_expiry",
                "base_price",
                "current_price",
                "base_demand",
                "Status",
            ]
        ].rename(
            columns={
                "category": "Category",
                "name": "Product",
                "stock": "Units in Stock",
                "days_to_expiry": "Expiry Horizon",
                "base_price": "Base (₹)",
                "current_price": "Dynamic Elastic (₹)",
                "base_demand": "Base Daily Demand",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

with tab_exports:
    st.markdown("### 📥 Compliance & Audit Ledger Downloads")
    exp_c1, exp_c2 = st.columns(2)
    
    with exp_c1:
        st.markdown("**Sales Transaction Journal**")
        if st.session_state.sales_history:
            sales_export_df = pd.DataFrame(st.session_state.sales_history)
            st.download_button(
                label="📄 Export Sales CSV",
                data=sales_export_df.to_csv(index=False).encode("utf-8"),
                file_name=f"sales_ledger_day_{st.session_state.current_day}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.caption("No sales transactions available to export.")

    with exp_c2:
        st.markdown("**Spoilage & Perishable Write-Offs**")
        if st.session_state.waste_history:
            waste_export_df = pd.DataFrame(st.session_state.waste_history)
            st.download_button(
                label="📄 Export Waste Audit CSV",
                data=waste_export_df.to_csv(index=False).encode("utf-8"),
                file_name=f"spoilage_audit_day_{st.session_state.current_day}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.caption("No perishable write-offs on record.")

# ==========================================
# 8. LIFECYCLE OPERATIONS & RECENT LEDGER
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
col_ledger, col_pipelines = st.columns([1.6, 1])

with col_ledger:
    st.markdown("### 📝 Live Transaction Terminal Feed")
    if st.session_state.sales_history:
        st.dataframe(
            pd.DataFrame(st.session_state.sales_history).tail(10),
            use_container_width=True,
            hide_index=True,
            height=200,
        )
    else:
        st.caption("No transactions logged in this session.")

with col_pipelines:
    st.markdown("### ⏳ Operational Pipeline Steps")
    if current_role == "admin":
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("🌙 Simulate Day Step", type="primary", use_container_width=True):
                pass_one_day()
                st.rerun()
        with c_btn2:
            if st.button("🔄 System Reset", use_container_width=True):
                reset_store()
    else:
        st.info("System day transitions and state resets require **Administrator** privileges.")