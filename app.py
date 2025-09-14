import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Retail Sales Dashboard", layout="wide")
st.title("Retail Sales Dashboard")

# Load cleaned dataset safely
try:
    df = pd.read_csv("Retail_Cleaned.csv")
except FileNotFoundError:
    st.error("File `Retail_Cleaned.csv` not found. Please upload or place it in the same folder.")
    st.stop()

# Show basic info for debugging
st.subheader("Dataset Overview")
st.write("Shape of dataset:", df.shape)
st.write(df.head(20))

# Ensure required columns exist
required_cols = ["City", "ProductCategory", "TotalAmount", "Gender", "PurchaseDate"]
missing = [col for col in required_cols if col not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# Sidebar filters
cities = st.sidebar.multiselect(
    "Select Cities",
    options=df['City'].dropna().unique(),
    default=df['City'].dropna().unique()
)
categories = st.sidebar.multiselect(
    "Select Categories",
    options=df['ProductCategory'].dropna().unique(),
    default=df['ProductCategory'].dropna().unique()
)

# Filter dataframe
df_filtered = df[(df['City'].isin(cities)) & (df['ProductCategory'].isin(categories))]

#Show & edit dataset
st.subheader("Edit the Data Below")
edited_df = st.data_editor(df.head(20), num_rows="dynamic", use_container_width=True)

# KPIs
st.subheader("Key Metrics")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Revenue", f"${df_filtered['TotalAmount'].sum():,.0f}")
with col2:
    st.metric("Total Transactions", f"{df_filtered.shape[0]:,}")

# Gender distribution
gender_counts = df_filtered['Gender'].value_counts()
fig1 = px.pie(
    names=gender_counts.index,
    values=gender_counts.values,
    title="Gender Distribution",
    color=gender_counts.index,
    color_discrete_map={"Male": "blue", "Female": "pink", "Other": "green"}
)
st.plotly_chart(fig1, use_container_width=True)
# Sales by category
fig2 = px.bar(
    df_filtered.groupby("ProductCategory", as_index=False)["TotalAmount"].sum(),
    x="ProductCategory", y="TotalAmount",
    title="Sales by Category"
)
st.plotly_chart(fig2, use_container_width=True)
# Monthly sales trend
df_filtered["PurchaseDate"] = pd.to_datetime(df_filtered["PurchaseDate"], errors="coerce")
monthly_sales = (
    df_filtered.groupby(df_filtered["PurchaseDate"].dt.to_period("M"))["TotalAmount"]
    .sum()
    .reset_index()
)
monthly_sales["PurchaseDate"] = monthly_sales["PurchaseDate"].astype(str)

fig3 = px.line(
    monthly_sales,
    x="PurchaseDate", y="TotalAmount",
    title="Monthly Sales Trend",
    markers=True
)
st.plotly_chart(fig3, use_container_width=True)
# City-wise revenue
city_rev = (
    df_filtered.groupby("City")["TotalAmount"]
    .sum()
    .reset_index()
    .sort_values("TotalAmount", ascending=False)
)

fig4 = px.bar(city_rev, x="City", y="TotalAmount", title="City-wise Revenue")
st.plotly_chart(fig4, use_container_width=True)
