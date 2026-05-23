import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Smart Gaming Tournament Analytics System",
    layout="wide"
)

st.title("Smart Gaming Tournament Analytics System")
st.write("BIT1034 Advance Programming Project")

menu = st.sidebar.selectbox(
    "Navigation",
    ["Dashboard", "Upload CSV", "Players", "Rankings", "Database"]
)

conn = sqlite3.connect("tournament.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    player_id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT,
    team_name TEXT,
    wins INTEGER,
    losses INTEGER,
    points INTEGER
)
""")
conn.commit()

if menu == "Dashboard":
    st.header("Tournament Dashboard")

    df = pd.read_sql_query("SELECT * FROM players", conn)

    if df.empty:
        st.warning("No player data available. Please upload CSV first.")
    else:
        total_players = len(df)
        total_wins = df["wins"].sum()
        total_losses = df["losses"].sum()
        top_score = df["points"].max()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Players", total_players)
        col2.metric("Total Wins", total_wins)
        col3.metric("Total Losses", total_losses)
        col4.metric("Top Score", top_score)

        st.subheader("Player Points Chart")
        fig, ax = plt.subplots()
        ax.bar(df["player_name"], df["points"])
        ax.set_xlabel("Player")
        ax.set_ylabel("Points")
        ax.set_title("Player Ranking Points")
        st.pyplot(fig)

elif menu == "Upload CSV":
    st.header("Upload CSV Dataset")

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        st.subheader("Uploaded Dataset Preview")
        st.dataframe(df)

        if st.button("Save Data to Database"):
            for _, row in df.iterrows():
                cursor.execute("""
                INSERT INTO players (player_name, team_name, wins, losses, points)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    row["Player Name"],
                    row["Team"],
                    int(row["Wins"]),
                    int(row["Losses"]),
                    int(row["Points"])
                ))

            conn.commit()
            st.success("CSV data saved successfully into SQLite database.")

elif menu == "Players":
    st.header("Player Records")

    df = pd.read_sql_query("SELECT * FROM players", conn)
    st.dataframe(df)

elif menu == "Rankings":
    st.header("Automatic Player Rankings")

    df = pd.read_sql_query("SELECT * FROM players", conn)

    if df.empty:
        st.warning("No ranking data available.")
    else:
        df = df.sort_values(by=["points", "wins"], ascending=False)
        df["rank_position"] = range(1, len(df) + 1)

        st.dataframe(df[["rank_position", "player_name", "team_name", "wins", "losses", "points"]])

        st.subheader("Win and Loss Analysis")
        fig, ax = plt.subplots()
        ax.bar(df["player_name"], df["wins"], label="Wins")
        ax.bar(df["player_name"], df["losses"], bottom=df["wins"], label="Losses")
        ax.set_xlabel("Player")
        ax.set_ylabel("Matches")
        ax.set_title("Win and Loss Analysis")
        ax.legend()
        st.pyplot(fig)

elif menu == "Database":
    st.header("SQLite Database Information")

    st.write("Database name: `tournament.db`")
    st.write("Main table: `players`")

    df = pd.read_sql_query("SELECT * FROM players", conn)
    st.dataframe(df)

conn.close()