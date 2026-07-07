import os
import streamlit as pd_st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration for a premium, wide dashboard look
pd_st.set_page_config(
    page_title="ShopStream Analytics Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling via markdown
pd_st.markdown("""
<style>
    .main {
        background-color: #0f111a;
        color: #e6edf3;
    }
    .stMetric {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #161b22;
        border-radius: 8px 8px 0 0;
        gap: 2px;
        padding-top: 10px;
        padding-bottom: 10px;
        color: #8b949e;
        border: 1px solid #30363d;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f6feb;
        color: white;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Outfit', 'Inter', sans-serif;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to load exported CSV data
def load_data(file_name):
    path = os.path.join("data", "processed", f"{file_name}.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return None

# Load all exported files
df_daily_rev = load_data("mart_daily_revenue")
df_cust_ltv = load_data("mart_customer_lifetime_value")
df_prod_perf = load_data("mart_product_performance")
df_refund_an = load_data("mart_refund_analysis")
df_deliv_perf = load_data("mart_delivery_performance")
df_camp_perf = load_data("mart_campaign_performance")
df_orders = load_data("fact_orders")

# Sidebar navigation / Branding
pd_st.sidebar.markdown("<h2 style='text-align: center; color: #1f6feb;'>ShopStream</h2>", unsafe_allow_html=True)
pd_st.sidebar.markdown("<p style='text-align: center; font-size: 0.9em; color: #8b949e;'>E-Commerce Data Warehouse & ETL Pipeline</p>", unsafe_allow_html=True)
pd_st.sidebar.divider()

pd_st.sidebar.info(
    "💡 **Recruiter Tip**: This dashboard displays analytical tables generated from 50K+ raw transactions loaded to Postgres and compiled via dbt models."
)

# Check if data exists
if df_orders is None or df_daily_rev is None:
    pd_st.error("⚠️ Data files not found! Please run the pipeline script or `python scripts/export_marts.py` first to generate processed files.")
else:
    pd_st.title("📈 ShopStream Analytics Dashboard")
    pd_st.caption("Real-time Business Intelligence powered by dbt and PostgreSQL warehouse marts")
    pd_st.divider()
    
    # Define tabs
    tab_overview, tab_revenue, tab_customers, tab_products, tab_delivery, tab_quality = pd_st.tabs([
        "📊 Executive Overview",
        "💸 Revenue Analytics",
        "👥 Customer Analytics",
        "📦 Product Analytics",
        "🚚 Delivery Analytics",
        "🔍 Data Quality Report"
    ])
    
    # ----------------------------------------------------
    # TAB 1: EXECUTIVE OVERVIEW
    # ----------------------------------------------------
    with tab_overview:
        pd_st.subheader("Key Performance Indicators")
        
        # Calculate top metrics
        total_rev = df_orders[df_orders['order_status'] != 'cancelled']['net_revenue'].sum()
        total_orders_cnt = df_orders[df_orders['order_status'] != 'cancelled']['order_id'].nunique()
        aov = total_rev / total_orders_cnt if total_orders_cnt > 0 else 0
        
        repeat_rate = (df_cust_ltv['total_orders'] > 1).sum() / len(df_cust_ltv) * 100
        
        col1, col2, col3, col4 = pd_st.columns(4)
        col1.metric("Total Net Sales", f"${total_rev:,.2f}", delta="Target: +12%")
        col2.metric("Total Net Orders", f"{total_orders_cnt:,}", delta="Daily avg: 42")
        col3.metric("Average Order Value (AOV)", f"${aov:.2f}", delta="Threshold: $120")
        col4.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%", delta="Target: 40%")
        
        pd_st.divider()
        
        col_left, col_right = pd_st.columns(2)
        
        with col_left:
            pd_st.subheader("Monthly Revenue Growth")
            df_daily_rev['month'] = pd.to_datetime(df_daily_rev['order_date']).dt.to_period('M').astype(str)
            df_monthly = df_daily_rev.groupby('month')['net_revenue'].sum().reset_index()
            
            fig_monthly = px.bar(
                df_monthly, x='month', y='net_revenue',
                labels={'net_revenue': 'Net Revenue ($)', 'month': 'Month'},
                title="Net Sales by Month",
                template="plotly_dark",
                color_discrete_sequence=['#1f6feb']
            )
            pd_st.plotly_chart(fig_monthly, use_container_width=True)
            
        with col_right:
            pd_st.subheader("Marketing Attribution")
            fig_camp = px.pie(
                df_camp_perf, values='total_revenue', names='campaign_name',
                title="Revenue Contribution by Marketing Campaign",
                template="plotly_dark",
                hole=0.4
            )
            pd_st.plotly_chart(fig_camp, use_container_width=True)
            
    # ----------------------------------------------------
    # TAB 2: REVENUE ANALYTICS
    # ----------------------------------------------------
    with tab_revenue:
        pd_st.subheader("Daily Sales Trends")
        
        # Sort by date
        df_daily_rev_sorted = df_daily_rev.sort_values('order_date')
        
        fig_trend = px.line(
            df_daily_rev_sorted, x='order_date', y='net_revenue',
            labels={'net_revenue': 'Daily Net Revenue ($)', 'order_date': 'Date'},
            title="Daily Sales Run-rate ($)",
            template="plotly_dark",
            color_discrete_sequence=['#58a6ff']
        )
        pd_st.plotly_chart(fig_trend, use_container_width=True)
        
        pd_st.divider()
        col_left, col_right = pd_st.columns(2)
        
        with col_left:
            pd_st.subheader("Top Performing Channels by ROI")
            fig_roi = px.bar(
                df_camp_perf[df_camp_perf['campaign_id'] != 'organic'].sort_values('campaign_roi', ascending=False),
                x='campaign_roi', y='campaign_name',
                orientation='h',
                labels={'campaign_roi': 'ROI (Sales/Budget Ratio)', 'campaign_name': 'Campaign'},
                title="Marketing ROI by Campaign",
                template="plotly_dark",
                color='campaign_roi',
                color_continuous_scale=px.colors.sequential.Bluyl
            )
            pd_st.plotly_chart(fig_roi, use_container_width=True)
            
        with col_right:
            pd_st.subheader("Customer Segment Revenue Contribution")
            # Join cust ltv segment to orders
            df_cust_seg = df_cust_ltv.groupby('customer_segment')['lifetime_value'].sum().reset_index()
            fig_seg = px.pie(
                df_cust_seg, values='lifetime_value', names='customer_segment',
                title="Share of Total Spend by Customer Segment",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            pd_st.plotly_chart(fig_seg, use_container_width=True)
            
    # ----------------------------------------------------
    # TAB 3: CUSTOMER ANALYTICS
    # ----------------------------------------------------
    with tab_customers:
        pd_st.subheader("Customer Lifetime Value Analysis")
        
        col_metrics_l, col_metrics_r = pd_st.columns(2)
        
        with col_metrics_l:
            pd_st.subheader("Top 10 High-Value Customers")
            top_10 = df_cust_ltv.sort_values('lifetime_value', ascending=False).head(10)
            pd_st.dataframe(
                top_10[['full_name', 'email', 'customer_segment', 'total_orders', 'lifetime_value', 'average_order_value']],
                column_config={
                    "full_name": "Customer Name",
                    "email": "Email Address",
                    "customer_segment": "Segment",
                    "total_orders": "Order Count",
                    "lifetime_value": pd_st.column_config.NumberColumn("Lifetime Value", format="$%.2f"),
                    "average_order_value": pd_st.column_config.NumberColumn("Avg Order Value", format="$%.2f")
                },
                hide_index=True,
                use_container_width=True
            )
            
        with col_metrics_r:
            pd_st.subheader("Purchase Statistics by Customer Segment")
            df_seg_summary = df_cust_ltv.groupby('customer_segment').agg(
                customer_count=('customer_id', 'count'),
                avg_orders=('total_orders', 'mean'),
                avg_spend=('lifetime_value', 'mean')
            ).reset_index()
            
            fig_seg_spend = px.bar(
                df_seg_summary, x='customer_segment', y='avg_spend',
                labels={'avg_spend': 'Avg Spend per Customer ($)', 'customer_segment': 'Segment'},
                title="Average Spend per Customer by Segment",
                template="plotly_dark",
                color='avg_spend',
                color_continuous_scale='Mint'
            )
            pd_st.plotly_chart(fig_seg_spend, use_container_width=True)
            
    # ----------------------------------------------------
    # TAB 4: PRODUCT ANALYTICS
    # ----------------------------------------------------
    with tab_products:
        pd_st.subheader("Product Performance Matrix")
        
        col_prod_l, col_prod_r = pd_st.columns(2)
        
        with col_prod_l:
            pd_st.subheader("Revenue by Category")
            df_cat = df_prod_perf.groupby('category')['net_revenue'].sum().reset_index().sort_values('net_revenue', ascending=False)
            fig_cat = px.bar(
                df_cat, x='net_revenue', y='category',
                orientation='h',
                labels={'net_revenue': 'Net Revenue ($)', 'category': 'Category'},
                title="Revenue by Product Department ($)",
                template="plotly_dark",
                color_discrete_sequence=['#ffc83d']
            )
            pd_st.plotly_chart(fig_cat, use_container_width=True)
            
        with col_prod_r:
            pd_st.subheader("Product Profit Margins by Category")
            df_cat_margin = df_prod_perf.groupby('category').agg(
                total_rev=('net_revenue', 'sum'),
                total_cost=('total_cost', 'sum')
            ).reset_index()
            df_cat_margin['profit_margin'] = (df_cat_margin['total_rev'] - df_cat_margin['total_cost']) / df_cat_margin['total_rev'] * 100
            
            fig_margin = px.bar(
                df_cat_margin.sort_values('profit_margin', ascending=False),
                x='category', y='profit_margin',
                labels={'profit_margin': 'Gross Profit Margin (%)', 'category': 'Category'},
                title="Profit Margin % by Product Category",
                template="plotly_dark",
                color='profit_margin',
                color_continuous_scale='Oranges'
            )
            pd_st.plotly_chart(fig_margin, use_container_width=True)
            
        pd_st.divider()
        pd_st.subheader("Refund Rate by Product Category")
        df_refund_agg = df_prod_perf.groupby('category').agg(
            sales=('net_revenue', 'sum'),
            refunded_amt=('estimated_refund_amount', 'sum')
        ).reset_index()
        df_refund_agg['refund_pct'] = (df_refund_agg['refunded_amt'] / df_refund_agg['sales']) * 100
        
        fig_refund = px.bar(
            df_refund_agg.sort_values('refund_pct', ascending=False),
            x='refund_pct', y='category',
            orientation='h',
            labels={'refund_pct': 'Refund Value % of Sales', 'category': 'Category'},
            title="Refund Leakage % of Sales by Category",
            template="plotly_dark",
            color_discrete_sequence=['#ff7b72']
        )
        pd_st.plotly_chart(fig_refund, use_container_width=True)
        
    # ----------------------------------------------------
    # TAB 5: DELIVERY ANALYTICS
    # ----------------------------------------------------
    with tab_delivery:
        pd_st.subheader("Logistics and Shipping Performance")
        
        col_del_l, col_del_r = pd_st.columns(2)
        
        with col_del_l:
            pd_st.subheader("Carrier Delay Rates")
            fig_del_pct = px.bar(
                df_deliv_perf.sort_values('delay_rate'),
                x='delay_rate', y='shipping_provider',
                orientation='h',
                labels={'delay_rate': 'Shipment Delay Rate (%)', 'shipping_provider': 'Carrier'},
                title="Percentage of Delayed Shipments by Carrier",
                template="plotly_dark",
                color='delay_rate',
                color_continuous_scale=px.colors.sequential.Sunsetdark
            )
            pd_st.plotly_chart(fig_del_pct, use_container_width=True)
            
        with col_del_r:
            pd_st.subheader("Average Lead-Time duration (Days)")
            fig_del_days = px.bar(
                df_deliv_perf.sort_values('average_delivery_days'),
                x='shipping_provider', y='average_delivery_days',
                labels={'average_delivery_days': 'Average Days (Ship to Delivery)', 'shipping_provider': 'Carrier'},
                title="Average Shipping Lead Time",
                template="plotly_dark",
                color_discrete_sequence=['#2ea043']
            )
            pd_st.plotly_chart(fig_del_days, use_container_width=True)
            
    # ----------------------------------------------------
    # TAB 6: DATA QUALITY REPORT
    # ----------------------------------------------------
    with tab_quality:
        pd_st.subheader("ShopStream Pipeline Audit Logs")
        
        report_md_path = os.path.join("reports", "data_quality_report.md")
        if os.path.exists(report_md_path):
            with open(report_md_path, "r") as f:
                report_content = f.read()
            pd_st.markdown(report_content)
        else:
            pd_st.warning("⚠️ Data Quality Report file (`reports/data_quality_report.md`) is missing. Please run `python scripts/data_quality_report.py` to compile metrics.")
