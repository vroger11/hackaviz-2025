# Toulouse Water & Rainfall Explorer

This project is a Streamlit application developed for the Hackaviz 2025 competition. It allows users to explore water levels and rainfall data in Toulouse, Occitanie.

## Features

- **Interactive Water Level Plot**: Visualize water height over time, colored by acceleration.
- **Rainfall Data Map**: Explore rainfall data on an interactive map, showing total precipitation and variation at different stations.
- **Date Range Selection**: Filter data by selecting a specific date range.
- **Top N Rainfall Stations**: Display the top N rainfall stations based on cumulative precipitation.

## Installation

You need to have [uv](https://docs.astral.sh/uv/) on your system to install this project.

1. Clone the repository:
    ```sh
    git clone https://github.com/vroger11/hackaviz-2025.git
    cd hackaviz-2025
    ```

2. Install the required dependencies:
    ```sh
    uv sync
    ```

3. Run the Streamlit app on your local machine:
    ```sh
    uv run streamlit run main.py
    ```

## Usage

1. **Sidebar Filters**: Use the sidebar to select the observation date range and the number of top rainfall stations to display.
2. **Water Level Plot**: Click and drag horizontally on the water level plot to select a specific date range. Double-click to reset the selection.
3. **Rainfall Data Map**: Explore the map to see total precipitation and variation at different stations.

## Live Demo

Check out the live demo [here](https://vroger11-hackaviz-2025.streamlit.app/).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## References and Acknowledgements

- [Hackaviz 2025](https://github.com/Toulouse-Dataviz/hackaviz-2025)

Special thanks to the Hackaviz 2025 organizers and the Toulouse Dataviz members for providing the data and support for this project.
