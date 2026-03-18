import seaborn as sns
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('startup_cleaned.csv')
    df['investors'] = df['investors'].astype(str).str.strip()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df['year'] = df['date'].dt.year
    return df

df = load_data()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title('STARTUP ANALYSIS')
option = st.sidebar.selectbox(
    'SELECT ONE',
    ['OVERALL ANALYSIS', 'STARTUP', 'INVESTOR']
)

# =========================================================
# OVERALL ANALYSIS
# =========================================================
if option == 'OVERALL ANALYSIS':
    st.title('OVERALL ANALYSIS')

    total_startups = df['startup'].nunique()
    total_invested = df['amount'].sum()
    max_investment = df['amount'].max()
    avg_investment = df['amount'].mean()

    st.subheader('Total Startups and Investments')
    st.write(f"Total Startups: {total_startups}")
    st.write(f"Total Amount Invested: ${total_invested:,.2f}")
    st.write(f"Maximum Amount Invested: ${max_investment:,.2f}")
    st.write(f"Average Amount Invested: ${avg_investment:,.2f}")

    # Vertical Analysis
    vertical_analysis = df.groupby('vertical')['amount'].agg(['count', 'sum']).reset_index()
    top_vertical = vertical_analysis.loc[vertical_analysis['sum'].idxmax()]

    st.subheader('Vertical Analysis')
    st.write(
        f"Top Vertical: {top_vertical['vertical']} | Count: {top_vertical['count']} | Total: ${top_vertical['sum']:,.2f}"
    )

    plt.figure(figsize=(10, 5))
    sns.barplot(
        x='count',
        y='vertical',
        data=vertical_analysis.sort_values('count', ascending=False),
        palette='viridis'
    )
    st.pyplot(plt)
    plt.clf()

    # Rounds
    st.subheader('Types of Rounds')
    st.bar_chart(df['round'].value_counts())

    # City funding
    st.subheader('City-wise Funding')
    city_funding = df.groupby('city')['amount'].sum()
    st.bar_chart(city_funding)

    # Top startups
    st.subheader('Top Startups Overall')
    top_startups = df.groupby('startup')['amount'].sum().nlargest(5)
    st.write(top_startups)

    # Top investors
    st.subheader('Top Investors')
    top_investors = df.groupby('investors')['amount'].sum().nlargest(5)
    st.write(top_investors)

    # Heatmap
    st.subheader('Funding Heatmap')
    heatmap_data = df.pivot_table(
        index='year',
        columns='vertical',
        values='amount',
        aggfunc='sum'
    ).fillna(0)

    plt.figure(figsize=(10, 5))
    sns.heatmap(heatmap_data, cmap='Blues')
    st.pyplot(plt)


# =========================================================
# STARTUP ANALYSIS 
# =========================================================
elif option == 'STARTUP':

    selected_startup = st.sidebar.selectbox(
        'SELECT STARTUP',
        sorted(df['startup'].dropna().unique())
    )

    st.title(f'STARTUP ANALYSIS: {selected_startup}')

    startup_df = df[df['startup'] == selected_startup]

    if startup_df.empty:
        st.warning("No data found for this startup.")
    else:
        latest = startup_df.sort_values('date', ascending=False).iloc[0]

        st.subheader('Company POV')
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Name**: {latest['startup']}")
            st.write(f"**Investors**: {latest['investors']}")
            st.write(f"**Vertical**: {latest['vertical']}")
            st.write(f"**Sub Vertical**: {latest['subvertical']}")
            st.write(f"**Location**: {latest['city']}")
            st.write(f"**Funding Round**: {latest['round']}")
            st.write(f"**Amount**: {latest['amount']}")

        with col2:
            st.write(f"**Date**: {latest['date']}")
            st.write(f"**Total Funding**: {startup_df['amount'].sum():,.2f}")

        # Funding rounds distribution
        st.subheader('Funding Rounds Distribution')
        st.bar_chart(startup_df['round'].value_counts())

        # Funding over time
        st.subheader('Funding Over Time')
        funding_trend = startup_df.groupby('date')['amount'].sum()
        st.line_chart(funding_trend)


# =========================================================
# INVESTOR ANALYSIS
# =========================================================
else:

    investor_list = sorted(set(df['investors'].str.split(',').sum()))
    investor = st.sidebar.selectbox('SELECT INVESTOR', investor_list)

    st.title(f"Investor Analysis: {investor}")

    investor_data = df[df['investors'].str.contains(investor, na=False)]

    if investor_data.empty:
        st.warning("No data found for this investor.")
    else:
        # Recent investments
        st.subheader('Recent Investments')
        st.dataframe(
            investor_data.sort_values('date', ascending=False)[
                ['date', 'startup', 'vertical', 'city', 'round', 'amount']
            ].head()
        )

        # Top investments
        st.subheader('Top 5 Investments')
        top_inv = investor_data.nlargest(5, 'amount')
        st.bar_chart(top_inv.set_index('startup')['amount'])

        # Sector preference
        st.subheader('Preferred Sectors')
        st.bar_chart(investor_data['vertical'].value_counts())

        # City distribution
        st.subheader('City Distribution')
        fig, ax = plt.subplots()
        investor_data['city'].value_counts().plot.pie(ax=ax, autopct='%1.1f%%')
        st.pyplot(fig)

        # Yearly trend
        st.subheader('Year-on-Year Investment')
        yoy = investor_data.groupby('year')['amount'].sum()
        st.line_chart(yoy)

        # Similar investments
        st.subheader('Similar Investments')
        similar = df[df['vertical'].isin(investor_data['vertical'].unique())]
        st.dataframe(similar[['startup', 'vertical', 'city', 'amount']].drop_duplicates().head())