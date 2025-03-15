"""Streamlit app to explore water levels and rainfall in Toulouse, Occitanie.

Module done for the Hackaviz 2025 event.
"""

from datetime import datetime
from os import system
from os.path import exists, join

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

if not exists("hackaviz-2025/data"):
    system("git submodule update --init --recursive")


@st.cache_data
def load_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the datasets for water levels and rainfall."""
    datasets_location = "hackaviz-2025/data"
    df_water = pd.read_parquet(join(datasets_location, "hauteur_eau_quotidienne_toulouse.parquet"))
    df_rain = pd.read_parquet(join(datasets_location, "pluviometrie.parquet"))

    df_water["date"] = pd.to_datetime(df_water["date_observation"])
    df_rain["date"] = pd.to_datetime(df_rain["date_observation"])

    # Clean columns name
    df_water.rename(columns={"max(hauteur, na.rm = TRUE)": "water_height"}, inplace=True)
    # Filter impossible data
    df_water = df_water[df_water["water_height"] < 10000]
    return df_water, df_rain


@st.dialog("👋 Welcome to the Toulouse Water & Rainfall Explorer!", width="large")
def tutorial() -> None:
    """Display a quick tutorial on how to use the app."""
    st.markdown("""
    ### 📚 **Quick tutorial:**

    1. **🎛️ Sidebar Filters:**
        - Select observation date range for the water level on Toulouse.
        - Use the sidebar on the left to adjust the Top **N** rainfall stations to display on the map.

    2. **📈 Select a Date Range:**
        - Click and drag horizontally on the water level plot to select a specific date range.
        - **Reset selection** by double-clicking anywhere on the plot.
            > *Your selection immediately updates the rainfall stations shown on the map below.*
        - The color code is as follows:
          - **Burnt Orange** → Strong deceleration.
          - **Grey** → No significant change.
          - **Deep Purple** → Strong acceleration.


    3. **🗺️ Explore Rainfall Data:**
        - The map shows only if data are available for the selected date range. If days are missing value, those day value will be set to 0.
        - **Color on the map represents rainfall variation** (how inconsistent the rainfall has been at each station).
        - **Size of the markers represents total precipitation** at each station.
        - Hover over each station to see:
          - **Total precipitation** over the selected period.
          - **Variation in rainfall** (standard deviation).


    ---
    **🎬 Quick video:**

    [![Watch tutorial](https://img.youtube.com/vi/2wekZIu_DFI/0.jpg)](https://www.youtube.com/watch?v=2wekZIu_DFI)

    **Enjoy exploring!**
    """)
    if st.button("Got it! 🚀"):
        st.session_state.show_tutorial = False
        st.rerun()


st.set_page_config(
    layout="wide",
    page_title="Toulouse water levels and rainfall in Occitanie",
    page_icon="🌊",
)

st.title("🌊 Toulouse water levels and rainfall in Occitanie")

# Load datasets
df_water, df_rain = load_datasets()

# Initialize session state to show popup only at first load
if "show_tutorial" not in st.session_state:
    st.session_state.show_tutorial = True

# Show popup tutorial on startup
if st.session_state.show_tutorial:
    tutorial()


# Sidebar filters
with st.sidebar:
    st.header("🎛️ Filters")

    date_range = st.slider(
        "📅 Select observation date range:",
        min_value=df_water["date"].min().to_pydatetime(),  # Convert Timestamp to datetime
        max_value=df_water["date"].max().to_pydatetime(),
        value=(datetime(2000, 1, 1), df_water["date"].max().to_pydatetime()),
    )

    aggregation_method = "median"
    n_most_cumulative_precipitations = st.slider(
        "💧 Top N rainfall stations:",
        min_value=1,
        max_value=100,
        value=50,
    )
    st.markdown("---")
    if st.button("📚 Show tutorial again"):
        st.session_state.show_tutorial = True
        st.rerun()


start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df_water_filtered = df_water[(df_water["date"] >= start_date) & (df_water["date"] <= end_date)]

# Aggregate water data
df_water_filtered = (
    df_water_filtered.groupby("date")["water_height"].agg(aggregation_method).reset_index()
)

# Assuming df_water_agg exists (date, water_height)
df_water_filtered = df_water_filtered.sort_values("date").reset_index(drop=True)

# Calculate first derivative (rate of change)
df_water_filtered["delta_height"] = df_water_filtered["water_height"].diff()
df_water_filtered["delta_time"] = df_water_filtered["date"].diff().dt.total_seconds()
df_water_filtered["velocity"] = df_water_filtered["delta_height"] / df_water_filtered["delta_time"]

# Calculate second derivative (acceleration)
df_water_filtered["acceleration"] = (
    df_water_filtered["velocity"].diff() / df_water_filtered["delta_time"]
)

# Handle NaN values resulting from differentiation
df_water_filtered.fillna(0, inplace=True)

# Normalize acceleration for colorscale mapping
max_accel = df_water_filtered["acceleration"].abs().max()
df_water_filtered["normalized_acceleration"] = (
    df_water_filtered["acceleration"] / max_accel
)  # Scale to [-1, 1]


custom_colorscale = [
    [0.0, "#D55E00"],  # Strong deceleration
    [0.5, "rgba(128,128,128,0.1)"],  # Neutral acceleration (zero)
    [1.0, "#4B0082"],  # Strong acceleration
]

# Efficient plotting with a single trace
fig_water = go.Figure(
    go.Scatter(
        x=df_water_filtered["date"],
        y=df_water_filtered["water_height"],
        mode="lines",
        line=dict(width=4, color="rgba(0,0,0,0.2)"),
        hoverinfo="skip",
        showlegend=False,
    )
)

# Overlay points colored by acceleration
fig_water.add_trace(
    go.Scatter(
        x=df_water_filtered["date"],
        y=df_water_filtered["water_height"],
        mode="markers",
        marker=dict(
            size=7,
            color=df_water_filtered["normalized_acceleration"],
            colorscale=custom_colorscale,
            cmin=-1,  # Force colorbar to range from -1 to 1
            cmax=1,
            colorbar=dict(
                title="Acceleration",
                tickvals=[-1, 0, 1],
                ticktext=["Strongest deceleration", "Usual", "Strongest acceleration"],
            ),
            showscale=True,
        ),
        showlegend=False,
        hovertemplate="Date: %{x}<br>Water Height: %{y:.0f} mm<br>Acceleration: %{marker.color:.4f}<extra></extra>",
    )
)


fig_water.update_layout(
    title="📈 Water Height Colored by Acceleration",
    xaxis_title="Date",
    yaxis_title="Water Height (mm)",
)

fig_water.update_layout(
    dragmode="select", newselection=dict(line=dict(color="red")), selectdirection="h"
)

fig_water.update_layout(margin=dict(l=0, r=0, t=35, b=0))

event = st.plotly_chart(
    fig_water, use_container_width=True, key="date", theme="streamlit", on_select="rerun"
)

if len(event.selection.box) > 0:
    start_rain = pd.to_datetime(event.selection.box[0]["x"][0])
    end_rain = pd.to_datetime(event.selection.box[0]["x"][1])
    if start_rain > end_rain:
        start_rain, end_rain = end_rain, start_rain
else:
    start_rain, end_rain = start_date, end_date

# Filter rain data by selected date range
df_rain_filtered = df_rain[(df_rain["date"] >= start_rain) & (df_rain["date"] <= end_rain)]

# Aggregate rainfall by location
sum_data = (
    df_rain_filtered.groupby(["nom_usuel", "latitude", "longitude"], as_index=False)[
        "precipitation"
    ]
    .sum()
    .nlargest(n_most_cumulative_precipitations, "precipitation")
)
std_data = df_rain_filtered.groupby(["nom_usuel", "latitude", "longitude"], as_index=False)[
    "precipitation"
].std()


# Merge the two datasets to align the indices properly
agg_rain = sum_data.merge(
    std_data, on=["nom_usuel", "latitude", "longitude"], how="left", suffixes=("_sum", "_std")
)

# Handle NaN values in standard deviation (for stations with only one measurement)
agg_rain["precipitation_std"].fillna(0, inplace=True)

# Normalize variation for color mapping
max_variation = agg_rain["precipitation_std"].max()
if max_variation > 0:
    agg_rain["variation_norm"] = agg_rain["precipitation_std"] / max_variation
else:
    agg_rain["variation_norm"] = 0


if len(agg_rain) > 0:
    # Create interactive map
    fig_rain = px.scatter_mapbox(
        agg_rain,
        lat="latitude",
        lon="longitude",
        size="precipitation_sum",
        color="variation_norm",
        hover_name="nom_usuel",
        hover_data={
            "precipitation_sum": ":.2f",
            "precipitation_std": ":.2f",
            "latitude": False,
            "longitude": False,
            "variation_norm": False,
        },
        labels={
            "precipitation_sum": "Total Precipitation (mm)",
            "variation_norm": "Variation Level",
            "precipitation_std": "Standard Deviation",
        },
        color_continuous_scale="Turbo",  # High-contrast colormap for variation
        size_max=25,
        range_color=[0, 1],
        zoom=8,
        mapbox_style="carto-positron",
        title=f"🗺️ Top {n_most_cumulative_precipitations} Rainfall Stations ({start_date.date()} to {end_date.date()})",
        height=780,
    )

    fig_rain.update_layout(
        coloraxis_colorbar=dict(
            title="Variation Level<br>on Selected period",
            tickvals=[0, 0.5, 1.0],
            ticktext=["Lowest", "Medium", "Highest"],
        )
    )

    fig_rain.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_rain, use_container_width=True, theme="streamlit")
else:
    st.write(
        f"**🗺️ Top {n_most_cumulative_precipitations} stations by total rainfall ({start_rain.date()} to {end_rain.date()})**"
    )
    st.warning("No data available for the selected date range.")
