import streamlit as st
import pandas as pd
import plotly.express as px
from data_cleaning import df_2025, df_1996

st.set_page_config(page_title="NBA Player Performance Tracker", layout="wide")
st.title("NBA Player Performance Tracker")
st.subheader("2024-25 vs 1995-96 Season Comparison")
st.markdown("This comparison includes only players with 40+ games played and 20+ minutes per game. This was done to filter in key players who played a significant role in the season.")

# --------------------------------------------------
# Combine both seasons into one DataFrame with a Season column
# --------------------------------------------------
df_2025_labeled = df_2025.copy()
df_2025_labeled["Season"] = "2024-25"
df_1996_labeled = df_1996.copy()
df_1996_labeled["Season"] = "1995-96"
combined = pd.concat([df_2025_labeled, df_1996_labeled], ignore_index=True)

# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
with st.sidebar:
    st.header("Filters")
    season = st.multiselect(
        "Season",
        combined["Season"].unique(),
        default=combined["Season"].unique(),
    )
    position = st.multiselect(
        "Position",
        combined["Pos"].unique(),
        default=combined["Pos"].unique(),
    )

filtered_df = combined[
    combined["Season"].isin(season)
    & combined["Pos"].isin(position)
]

# --------------------------------------------------
# Tabs
# --------------------------------------------------
tab_table, tab_stats, tab_viz = st.tabs(["Table", "Statistics", "Visualizations"])

# --------------------------------------------------
# Table tab
# --------------------------------------------------
with tab_table:
    st.subheader("Player Data")
    st.dataframe(filtered_df.reset_index(drop=True))

    st.download_button(
        label="Download as CSV",
        data=filtered_df.to_csv(index=False),
        file_name="nba_filtered_data.csv",
        mime="text/csv",
    )

# --------------------------------------------------
# Statistics tab
# --------------------------------------------------
with tab_stats:
    st.subheader("Top 10 Scorers")

    selected_seasons = filtered_df["Season"].unique()

    if len(selected_seasons) == 2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**2024-25**")
            top_2025 = (
                filtered_df[filtered_df["Season"] == "2024-25"][["Player", "PTS"]]
                .sort_values("PTS", ascending=False)
                .head(10)
                .reset_index(drop=True)
            )
            st.dataframe(top_2025)
        with col2:
            st.markdown("**1995-96**")
            top_1996 = (
                filtered_df[filtered_df["Season"] == "1995-96"][["Player", "PTS"]]
                .sort_values("PTS", ascending=False)
                .head(10)
                .reset_index(drop=True)
            )
            st.dataframe(top_1996)
    else:
        top_scorers = (
            filtered_df[["Player", "PTS"]]
            .sort_values("PTS", ascending=False)
            .head(10)
            .reset_index(drop=True)
        )
        st.dataframe(top_scorers)

    st.subheader("Average PPG by Position (Table)")
    ppg_table = (
        filtered_df.groupby(["Pos", "Season"])["PTS"]
        .mean()
        .round(1)
        .unstack("Season")
    )
    st.dataframe(ppg_table)

    st.subheader("Average Steals by Position (Table)")
    stl_table = (
        filtered_df.groupby(["Pos", "Season"])["STL"]
        .mean()
        .round(2)
        .unstack("Season")
    )
    st.dataframe(stl_table)

    st.subheader("Average Minutes Per Game by Position (Table)")
    mpg_table = (
        filtered_df.groupby(["Pos", "Season"])["MP"]
        .mean()
        .round(3)
        .unstack("Season")
    )
    st.dataframe(mpg_table)

    st.subheader("Average Rebounds by Position (Table)")
    trb_table = (
        filtered_df.groupby(["Pos", "Season"])["TRB"]
        .mean()
        .round(2)
        .unstack("Season")
    )
    st.dataframe(trb_table)

    st.subheader("Average Assists by Position (Table)")
    ast_table = (
        filtered_df.groupby(["Pos", "Season"])["AST"]
        .mean()
        .round(2)
        .unstack("Season")
    )
    st.dataframe(ast_table)

    if "BLK" in filtered_df.columns:
        st.subheader("Average blocks by Position (Table)")
        blk_table = (
            filtered_df.groupby(["Pos", "Season"])["BLK"]
            .mean()
            .round(2)
            .unstack("Season")
        )
        st.dataframe(blk_table)

    st.subheader("Average 3-Point Percentage by Position (Table)")
    fg3_table = (
        filtered_df.groupby(["Pos", "Season"])["3P%"]
        .mean()
        .round(2)
        .unstack("Season")
    )
    st.dataframe(fg3_table)

# --------------------------------------------------
# Visualizations tab
# --------------------------------------------------
with tab_viz:
    #st.subheader("Average PPG by Position")
    
    ppg_chart_data = filtered_df.groupby(["Pos", "Season"])["PTS"].mean().round(1).reset_index()
    ppg_fig = px.bar(
        ppg_chart_data,
        x="Pos",
        y="PTS",
        color="Season",
        barmode="group",
        title="Average PPG by Position",
        labels={"Pos": "Position", "PTS": "Points Per Game"},
    )
    st.plotly_chart(ppg_fig, use_container_width=True)

    #st.subheader("Average Steals by Position")
    stl_chart_data = filtered_df.groupby(["Pos", "Season"])["STL"].mean().round(2).reset_index()
    stl_fig = px.bar(
        stl_chart_data,
        x="Pos",
        y="STL",
        color="Season",
        barmode="group",
        title="Average Steals by Position",
        labels={"Pos": "Position", "STL": "Steals Per Game"},
    )
    st.plotly_chart(stl_fig, use_container_width=True)

    if "BLK" in filtered_df.columns:
        blk_chart_data = filtered_df.groupby(["Pos", "Season"])["BLK"].mean().round(2).reset_index()
        blk_fig = px.line(
            blk_chart_data,
            x="Pos",
            y="BLK",
            color="Season",
            title="Average Blocks Per Game by Position",
            labels={"Pos": "Position", "BLK": "Blocks Per Game"},
        )
        st.plotly_chart(blk_fig, use_container_width=True)

    ast_box_data = filtered_df[["Pos", "AST", "Season"]].copy()
    box_fig = px.box(
        ast_box_data,
        x="Pos",
        y="AST",
        color="Season",
        title="Assists Per Game Distribution by Position",
        labels={"Pos": "Position", "AST": "Assists Per Game"},
    )
    st.plotly_chart(box_fig, use_container_width=True)

    hist_fig = px.histogram(
        filtered_df,
        x="3P%",
        color="Season",
        barmode="overlay",
        opacity=0.6,
        title="3-Point % Distribution Across Eras",
    )
    st.plotly_chart(hist_fig, use_container_width=True)
    