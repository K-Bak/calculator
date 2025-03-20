import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def calculate_roas_metrics(gross_margin, ad_spend, roas_target):
    # Beregn Break-even ROAS
    break_even_roas = 1 / (gross_margin / 100)
    
    # Beregn Total Revenue
    total_revenue = ad_spend * roas_target
    
    # Beregn Monthly Profit
    profit_margin = gross_margin / 100
    monthly_profit = (total_revenue * profit_margin) - ad_spend
    
    return break_even_roas, total_revenue, monthly_profit

def calculate_poas_metrics(ad_spend, sale_price, product_cost, variable_cost, sales_count):
    # Beregn Total Revenue (Omsætning)
    total_revenue = sales_count * sale_price
    
    # Beregn samlede omkostninger
    total_costs = (product_cost + variable_cost) * sales_count + ad_spend
    
    # Beregn Profit
    total_profit = total_revenue - total_costs
    
    # Beregn POAS
    poas = total_profit / ad_spend if ad_spend > 0 else 0
    
    return total_profit, poas

# Streamlit UI
st.image("generaxion-logo.png", width=200)  # Tilføj logo øverst på siden
st.title("📊 ROAS & POAS beregner")
st.write("Beregn din Return on Ad Spend (ROAS) eller Profit on Ad Spend (POAS)")

# Vælg beregner
calculator_type = st.radio("Vælg beregner", ["ROAS beregner", "POAS beregner"], index=0)

if calculator_type == "ROAS beregner":
    # ROAS beregner
    gross_margin = st.slider("Bruttomargin (%)", min_value=5, max_value=95, value=35, step=1)
    ad_spend = st.number_input("Annonceringsbudget (kr.)", min_value=100, value=10000, step=100)
    roas_target = st.slider("Mål-ROAS", min_value=1.0, max_value=20.0, value=2.0, step=0.1)
    
    # Beregn metrics
    break_even_roas, total_revenue, monthly_profit = calculate_roas_metrics(gross_margin, ad_spend, roas_target)
    
    # Resultater
    st.subheader("📊 Resultater")
    st.metric(label="Break-even ROAS", value=round(break_even_roas, 2))
    st.metric(label="Total Omsætning (kr.)", value=f"{total_revenue:,.2f} kr.")
    st.metric(label="Månedlig Profit (kr.)", value=f"{monthly_profit:,.2f} kr.", delta=round(monthly_profit, 2))
    
    # Visualisering af ROAS profit
    st.subheader("📉 Profit ved forskellige ROAS-mål")
    roas_values = [i for i in range(1, 21)]
    profits = [(ad_spend * roas * (gross_margin / 100)) - ad_spend for roas in roas_values]
    
    plt.figure(figsize=(8, 4))
    plt.scatter(roas_values, profits, color="blue", label="Profit vs. ROAS")
    plt.axhline(0, color="red", linestyle="--", label="Break-even")
    plt.xlabel("ROAS")
    plt.ylabel("Profit (kr.)")
    plt.title("Profit ved forskellige ROAS-mål (Scatter-plot)")
    plt.legend()
    st.pyplot(plt)

elif calculator_type == "POAS beregner":
    # POAS beregner
    gross_margin = st.slider("Bruttomargin (%)", min_value=5, max_value=95, value=35, step=1)
    ad_spend = st.number_input("Annonceringsbudget (kr.)", min_value=100, value=10000, step=100)
    roas_target = st.slider("Mål-ROAS", min_value=1.0, max_value=20.0, value=2.0, step=0.1)
    product_cost = st.number_input("Produktomkostninger pr. salg (kr.)", min_value=0, value=100, step=10)
    variable_cost = st.number_input("Variable omkostninger pr. salg (kr.)", min_value=0, value=50, step=10)
    sales_count = st.number_input("Antal salg", min_value=1, value=100, step=1)
    sale_price = st.number_input("Salgspris pr. enhed (kr.)", min_value=1, value=200, step=10)
    
    # Beregn POAS metrics
    total_profit, poas = calculate_poas_metrics(ad_spend, sale_price, product_cost, variable_cost, sales_count)
    
    # Resultater
    st.subheader("📊 Resultater")
    st.metric(label="Total Profit (kr.)", value=f"{total_profit:,.2f} kr.")
    st.metric(label="POAS", value=f"{poas:.2f}")
