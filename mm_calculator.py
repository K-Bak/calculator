import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import openai

# Indsæt din OpenAI API-nøgle
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

st.markdown(
    """
    <style>
        .stButton>button {
            background-color: #FF6F41;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
        }
        .stButton>button:hover {
            background-color: #FFB8A3;
        }
    </style>
    """,
    unsafe_allow_html=True
)

import openai

def generate_ai_analysis(context, data):
    prompt = f"{context}\n\nData:\n{data}\n\nGiv en kort analyse og forslag til forbedringer."

    client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du er en AI-marketingekspert."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

def calculate_metrics(budget, cpc, cvr, aov, is_seo=False, seo_volume=0, seo_ctr=0):
    if is_seo:
        clicks = seo_volume * (seo_ctr / 100)  # SEO trafik baseret på volumen og CTR
    else:
        clicks = (budget / cpc) if cpc > 0 else 0
    conversions = clicks * (cvr / 100)
    revenue = conversions * aov
    roas = revenue / budget if budget > 0 else 0
    return clicks, conversions, revenue, roas

if "page" not in st.session_state:
    st.session_state.page = "home"

def go_home():
    st.session_state.page = "home"

if st.session_state.page == "home":
    st.image("generaxion-logo.png", use_container_width=True)
    st.markdown("<h1 style='text-align: center;'>📊 Vælg beregner</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📈 ROAS/POAS Beregner", key="roas_button"):
            st.session_state.page = "roas"
            st.rerun()
    with col2:
        if st.button("📉 Marketing Mix Beregner", key="mix_button"):
            st.session_state.page = "mix"
            st.rerun()

elif st.session_state.page == "roas":
    st.button("🔙 Tilbage", on_click=go_home, key="back_button", help="Gå tilbage til forsiden")
    st.image("generaxion-logo.png", width=150)
    st.title("📈 ROAS & POAS Beregner")

    # Vælg beregner
    calculator_type = st.radio("Vælg beregner", ["ROAS beregner", "POAS beregner"], index=0)

    if calculator_type == "ROAS beregner":
        gross_margin = st.slider("Bruttomargin (%)", min_value=5, max_value=95, value=35, step=1)
        ad_spend = st.number_input("Annonceringsbudget (kr.)", min_value=100, value=10000, step=100)
        roas_target = st.slider("Mål-ROAS", min_value=1.0, max_value=20.0, value=2.0, step=0.1)

        if ad_spend > 0:
            break_even_roas = 1 / (gross_margin / 100)
            total_revenue = ad_spend * roas_target
            monthly_profit = (total_revenue * (gross_margin / 100)) - ad_spend

            st.subheader("📊 Resultater")
            st.metric(label="Break-even ROAS", value=round(break_even_roas, 2))
            st.metric(label="Total Omsætning (kr.)", value=f"{total_revenue:,.2f} kr.")
            st.metric(label="Månedlig Profit (kr.)", value=f"{monthly_profit:,.2f} kr.", delta=round(monthly_profit, 2))

            # Visualisering af ROAS profit
            st.subheader("📉 Profit ved forskellige ROAS-mål")
            roas_values = [i for i in range(1, 21)]
            profits = [(ad_spend * roas * (gross_margin / 100)) - ad_spend for roas in roas_values]

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.scatter(roas_values, profits, color="#367EF7", label="Profit vs. ROAS")
            ax.axhline(0, color="red", linestyle="--", label="Break-even")
            ax.set_xlabel("ROAS", color="#367EF7")
            ax.set_ylabel("Profit (kr.)", color="#367EF7")
            ax.set_title("Profit ved forskellige ROAS-mål (Scatter-plot)", color="#367EF7")
            ax.legend()
            st.pyplot(fig)

            if st.button("🧠 Generer AI-analyse"):
                data = f"Bruttomargin: {gross_margin}%, Ad Spend: {ad_spend} kr., ROAS Mål: {roas_target}, Total Omsætning: {total_revenue:,.2f} kr., Månedlig Profit: {monthly_profit:,.2f} kr."
                analysis = generate_ai_analysis("ROAS & POAS analyse", data)
                st.subheader("🔍 AI-analyse")
                st.write(analysis)

    elif calculator_type == "POAS beregner":
        ad_spend = st.number_input("Annonceringsbudget (kr.)", min_value=100, value=10000, step=100)
        product_cost = st.number_input("Produktomkostninger pr. salg (kr.)", min_value=0, value=100, step=10)
        variable_cost = st.number_input("Variable omkostninger pr. salg (kr.)", min_value=0, value=50, step=10)
        sales_count = st.number_input("Antal salg", min_value=1, value=100, step=1)
        sale_price = st.number_input("Salgspris pr. enhed (kr.)", min_value=1, value=200, step=10)

        if ad_spend > 0 and sales_count > 0:
            total_revenue = sales_count * sale_price
            total_costs = (product_cost + variable_cost) * sales_count + ad_spend
            total_profit = total_revenue - total_costs
            poas = total_profit / ad_spend if ad_spend > 0 else 0

            st.subheader("📊 Resultater")
            st.metric(label="Total Profit (kr.)", value=f"{total_profit:,.2f} kr.")
            st.metric(label="POAS", value=f"{poas:.2f}")

            # Generer POAS-værdier for forskellige antal salg
            sales_range = range(1, max(5, sales_count + 1))
            poas_values = [((s * sale_price - ((product_cost + variable_cost) * s + ad_spend)) / ad_spend if ad_spend > 0 else 0) for s in sales_range]

            # Opret POAS graf
            st.subheader("📈 POAS udvikling ved forskellige antal salg")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(sales_range, poas_values, marker="o", linestyle="-", color="#367EF7", label="POAS vs. Antal salg")
            ax.axhline(1, color="red", linestyle="--", label="Break-even POAS")
            ax.set_xlabel("Antal salg", color="#367EF7")
            ax.set_ylabel("POAS", color="#367EF7")
            ax.set_title("POAS udvikling ved forskellige antal salg", color="#367EF7")
            ax.legend()
            st.pyplot(fig)

            if st.button("🧠 Generer AI-analyse"):
                data = f"Ad Spend: {ad_spend} kr., Produktomkostninger: {product_cost} kr., Variable omkostninger: {variable_cost} kr., Antal salg: {sales_count}, Salgspris: {sale_price} kr., Total Profit: {total_profit:,.2f} kr., POAS: {poas:.2f}"
                analysis = generate_ai_analysis("POAS analyse", data)
                st.subheader("🔍 AI-analyse")
                st.write(analysis)

elif st.session_state.page == "mix":
    st.button("🔙 Tilbage", on_click=go_home, key="mix_back_button", help="Gå tilbage til forsiden")
    st.image("generaxion-logo.png", width=150)
    st.title("📉 Marketing Mix Beregner")

    # Valg af kanaler
    default_channels = ["Google Ads", "Facebook Ads", "SEO", "E-mail", "Display"]
    st.sidebar.header("📌 Vælg aktive kanaler")
    selected_channels = []
    for channel in default_channels:
        if st.sidebar.checkbox(channel, value=True):
            selected_channels.append(channel)

    st.sidebar.header("🔢 Input dine marketingdata")
    channel_data = {}
    for channel in selected_channels:
        st.sidebar.subheader(channel)
        budget = st.sidebar.number_input(f"Budget for {channel} (DKK)", min_value=0, value=5000, step=1000)

        if channel == "SEO":
            seo_volume = st.sidebar.number_input(f"Søgevolumen for {channel}", min_value=0, value=10000, step=1000)
            seo_ctr = st.sidebar.number_input(f"CTR fra Google for {channel} (%)", min_value=0.1, max_value=100.0, value=5.0, step=0.1)
            cpc, ctr = 0, 0
            email_recipients, email_open_rate = 0, 0  # Placeholder for ikke-e-mail kanaler

        elif channel == "E-mail":
            email_recipients = st.sidebar.number_input(f"Antal modtagere for {channel}", min_value=0, value=5000, step=100)
            email_open_rate = st.sidebar.number_input(f"Åbningsrate for {channel} (%)", min_value=0.1, max_value=100.0, value=20.0, step=0.1)
            ctr = st.sidebar.number_input(f"CTR for {channel} (%)", min_value=0.1, max_value=100.0, value=5.0, step=0.1)
            cpc, seo_volume, seo_ctr = 0, 0, 0  # Placeholder for ikke-CPC kanaler

        else:
            cpc = st.sidebar.number_input(f"CPC for {channel} (DKK)", min_value=0.1, value=5.0, step=0.1)
            seo_volume, seo_ctr, email_recipients, email_open_rate = 0, 0, 0, 0  # Placeholder for ikke-SEO/E-mail kanaler

        cvr = st.sidebar.number_input(f"Konverteringsrate for {channel} (%)", min_value=0.1, max_value=100.0, value=2.0, step=0.1)
        aov = st.sidebar.number_input(f"Gennemsnitlig ordre-/kundepris for {channel} (DKK)", min_value=1, value=500, step=10)

        # Beregn forventede klik baseret på kanaltype
        if channel == "SEO":
            clicks = seo_volume * (seo_ctr / 100)
        elif channel == "E-mail":
            clicks = email_recipients * (email_open_rate / 100) * (ctr / 100)
        else:
            clicks = (budget / cpc) if cpc > 0 else 0

        # Beregn konverteringer, omsætning og ROAS
        conversions = clicks * (cvr / 100)
        revenue = conversions * aov
        roas = revenue / budget if budget > 0 else 0

        channel_data[channel] = [budget, clicks, conversions, revenue, roas]

    st.subheader("📊 Resultater")
    st.dataframe(pd.DataFrame.from_dict(channel_data, orient='index', columns=["Budget", "Kliks", "Konverteringer", "Omsætning", "ROAS"]))

    # Visualisering
    st.subheader("📉 Budgetallokering")
    fig, ax = plt.subplots()
    ax.pie([data[0] for data in channel_data.values()], labels=selected_channels, autopct='%1.1f%%', startangle=140, colors=["#367EF7", "#00A999", "#F1A1D9", "#FF6F41"], textprops={'fontsize': 12})
    ax.set_title("Budgetfordeling på tværs af kanaler", color="#333333", fontsize=14)
    st.pyplot(fig)

    st.subheader("📈 ROAS pr. kanal")
    fig, ax = plt.subplots()
    ax.bar([channel for channel in channel_data.keys()], [data[4] for data in channel_data.values()], color="#367EF7")
    ax.set_ylabel("ROAS", color="#333333", fontsize=12)
    ax.set_xlabel("Marketingkanal", color="#333333", fontsize=12)
    ax.set_title("ROAS på tværs af kanaler", color="#333333", fontsize=14)
    st.pyplot(fig)

    if st.button("🧠 Generer AI-analyse"):
        data_summary = "\n".join([f"{ch}: Budget {data[0]} kr., ROAS {data[4]:.2f}" for ch, data in channel_data.items()])
        analysis = generate_ai_analysis("Marketing Mix analyse", data_summary)
        st.subheader("🔍 AI-analyse")
        st.write(analysis)

    st.button("🔙 Tilbage", on_click=go_home)