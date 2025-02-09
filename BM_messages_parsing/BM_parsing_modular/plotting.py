import matplotlib.pyplot as plt
import pandas as pd



# def plot_data(grouped_data, unique_node_ids, wave_data, spotter_id):
#     """
#     Generate detailed plots for wave height, managed sensors, and unmanaged data.
#
#     Args:
#         grouped_data (dict): Parsed data grouped by Node ID or sensor position.
#         unique_node_ids (set): Unique Node IDs from unmanaged data.
#         wave_data (dict): Parsed wave data.
#         spotter_id (str): Spotter ID for labeling.
#     """
#     marker_size = 2
#     line_alpha = 0.5
#     scatter_alpha = 1.0
#     plt.rcParams['font.family'] = 'Arial'
#
#     # Sofar Dashboard Color Palette
#     color_blue_light = '#1ca8dd'
#     color_blue_bright = '#0066FF'
#     color_blue_deep = '#0050A0'
#     color_green_dark = '#228B22'
#     color_brown_light = '#8B4513'
#     color_red_dark = '#B22222'
#
#     # Conversion Factors
#     meter_to_feet = 3.28084
#     m_per_s_to_knots = 1.94384
#     newton_to_lbf = 0.224809
#     rad_to_deg = 57.2958
#
#     # Debug: Print grouped_data to ensure load cell data is present
#     print(f"DEBUG: Data available for plotting, Node IDs: {unique_node_ids}")
#     for node_id in unique_node_ids:
#         if node_id in grouped_data:
#             print(f"DEBUG: Data for Node ID {node_id}:")
#             print(grouped_data[node_id])
#
#     # Setup plot layout
#     fig, axs = plt.subplots(4, 1, figsize=(12, 16), sharex=True)
#     fig.suptitle(f"Time Series Data for Spotter ID: {spotter_id}", fontsize=16)
#
#     # Plot 1: Significant Wave Height
#     wave_df = pd.DataFrame(wave_data["waves"])
#     wave_df["timestamp"] = pd.to_datetime(wave_df["timestamp"])
#     wave_height_m = wave_df["significantWaveHeight"]
#     axs[0].plot(wave_df["timestamp"], wave_height_m, color=color_blue_light, linestyle='-', alpha=line_alpha,
#                 label="Wave Height (m)")
#     axs[0].scatter(wave_df["timestamp"], wave_height_m, color=color_blue_light, s=marker_size ** 2, alpha=scatter_alpha)
#     axs[0].set_ylabel("Wave Height (m)")
#     ax_wave_ft = axs[0].twinx()
#     ax_wave_ft.set_ylabel("Wave Height (ft)")
#     ax_wave_ft.set_ylim(wave_height_m.min() * meter_to_feet, wave_height_m.max() * meter_to_feet)
#     axs[0].legend(loc="upper left")
#
#     # Plot Managed Sensor Data
#     row_idx = 1
#     for node_id, data in grouped_data.items():
#         node_data = pd.DataFrame(data)
#         node_data["timestamp"] = pd.to_datetime(node_data["timestamp"])
#
#     # Iterate through managed sensor positions
#     for sensor_position, node_data in grouped_data.items():
#         print(f"DEBUG: Processing sensor position {sensor_position}")
#
#         # Identify sensors to plot (e.g., "pressure")
#         for sensor in ["pressure_mean", "pressure_stdev"]:  # Add more managed types if needed
#             if sensor == "pressure_mean":
#                 print(f"DEBUG: Plotting RBR pressure data for {sensor_position}")
#
#                 # Filter data
#                 rbr_mean = node_data[node_data["parsed_type"] == "pressure_mean"].copy()
#                 rbr_mean["value"] = rbr_mean["value"].astype(float)
#
#                 rbr_std = node_data[node_data["parsed_type"] == "pressure_stdev"].copy()
#                 rbr_std["value"] = rbr_std["value"].astype(float)
#
#                 # Align timestamps
#                 merged_rbr = pd.merge(
#                     rbr_mean[["timestamp", "value"]],
#                     rbr_std[["timestamp", "value"]],
#                     on="timestamp",
#                     suffixes=("_mean", "_std")
#                 )
#
#                 # Plot the data
#                 axs[row_idx].plot(
#                     merged_rbr["timestamp"],
#                     merged_rbr["value_mean"],
#                     color="blue",
#                     label=f"{sensor_position} Pressure Mean",
#                     linestyle='-', alpha=0.7
#                 )
#                 axs[row_idx].fill_between(
#                     merged_rbr["timestamp"],
#                     merged_rbr["value_mean"] - merged_rbr["value_std"],
#                     merged_rbr["value_mean"] + merged_rbr["value_std"],
#                     color="lightblue", alpha=0.2, label="Std Dev"
#                 )
#                 axs[row_idx].set_ylabel(f"Pressure ({rbr_mean['units'].iloc[0]})")
#                 axs[row_idx].legend(loc="upper left")
#
#     # Plot Aanderaa data
#     aanderaa_types = {
#         "speed": ["aanderaa_abs_speed_mean_15bits", "aanderaa_abs_speed_std_15bits"],
#         "tilt": ["aanderaa_abs_tilt_mean_8bits", "aanderaa_std_tilt_mean_8bits"],
#     }
#
#     for sensor, (mean_type, std_type) in aanderaa_types.items():
#         mean_data = node_data[node_data["data_type_name"] == mean_type]
#         std_data = node_data[node_data["data_type_name"] == std_type]
#
#         # Align mean and std data by timestamp
#         if not mean_data.empty and not std_data.empty:
#             aligned_data = pd.merge(
#                 mean_data, std_data, on="timestamp", suffixes=("_mean", "_std"), how="inner"
#             )
#             aligned_data["value_mean"] = aligned_data["value_mean"].astype(float) * (0.01 if sensor == "speed" else 1.0)
#             aligned_data["value_std"] = aligned_data["value_std"].astype(float) * (0.01 if sensor == "speed" else 1.0)
#
#             # Extract units
#             units = mean_data["units"].iloc[0] if "units" in mean_data else "units"
#
#             # Plot mean data
#             axs[row_idx].plot(
#                 aligned_data["timestamp"], aligned_data["value_mean"],
#                 color=color_blue_deep, linestyle='-', alpha=line_alpha,
#                 label=f"Aanderaa {sensor.capitalize()} ({node_id})"
#             )
#             axs[row_idx].fill_between(
#                 aligned_data["timestamp"],
#                 aligned_data["value_mean"] - aligned_data["value_std"],
#                 aligned_data["value_mean"] + aligned_data["value_std"],
#                 color=color_blue_deep, alpha=0.2
#             )
#
#             # Left Y-axis
#             if sensor == "speed":
#                 axs[row_idx].set_ylabel(f"Current Speed (m/s)")
#                 # Right Y-axis for speed in knots
#                 ax_speed_knots = axs[row_idx].twinx()
#                 ax_speed_knots.set_ylabel("Speed (knots)")
#                 ax_speed_knots.set_ylim(axs[row_idx].get_ylim()[0] * m_per_s_to_knots,
#                                         axs[row_idx].get_ylim()[1] * m_per_s_to_knots)
#                 ax_speed_knots.tick_params(axis='y', labelcolor='black')
#             elif sensor == "tilt":
#                 axs[row_idx].set_ylabel("Tilt (radians)")
#                 # Right Y-axis for tilt in degrees
#                 ax_tilt_deg = axs[row_idx].twinx()
#                 ax_tilt_deg.set_ylabel("Tilt (degrees)")
#                 ax_tilt_deg.set_ylim(axs[row_idx].get_ylim()[0] * rad_to_deg, axs[row_idx].get_ylim()[1] * rad_to_deg)
#                 ax_tilt_deg.tick_params(axis='y', labelcolor='black')
#
#             axs[row_idx].legend(loc="upper left")
#             row_idx += 1
#
#     # # Plot Load Cell Data for Unmanaged Nodes
#     # for node_id in unique_node_ids:
#     #     node_data = pd.DataFrame(grouped_data[node_id])
#     #     node_data["timestamp"] = pd.to_datetime(node_data["timestamp"])
#     #     load_cell_data = node_data[node_data["data_type_name"] == "binary_hex_encoded"]
#     #     if not load_cell_data.empty:
#     #         mean_force = load_cell_data["mean_force"].astype(float)
#     #         max_force = load_cell_data["max_force"].astype(float)
#     #         axs[row_idx].plot(load_cell_data["timestamp"], mean_force, color=color_brown_light, linestyle='-',
#     #                           alpha=line_alpha, label=f"Load Cell Mean ({node_id})")
#     #         axs[row_idx].scatter(load_cell_data["timestamp"], mean_force, color=color_brown_light, s=marker_size ** 2,
#     #                              alpha=scatter_alpha)
#     #         axs[row_idx].plot(load_cell_data["timestamp"], max_force, color=color_red_dark, linestyle='-',
#     #                           alpha=line_alpha, label=f"Load Cell Max ({node_id})")
#     #         axs[row_idx].scatter(load_cell_data["timestamp"], max_force, color=color_red_dark, s=marker_size ** 2,
#     #                              alpha=scatter_alpha)
#     #         axs[row_idx].set_ylabel("Force (N)")
#     #         ax_force_lbf = axs[row_idx].twinx()
#     #         ax_force_lbf.set_ylabel("Force (lbf)")
#     #         ax_force_lbf.set_ylim(axs[row_idx].get_ylim()[0] * newton_to_lbf,
#     #                               axs[row_idx].get_ylim()[1] * newton_to_lbf)
#     #         axs[row_idx].legend(loc="upper left")
#     #         row_idx += 1
#     # Plot Load Cell Data for Unmanaged Nodes
#     for node_id in unique_node_ids:
#         node_data = pd.DataFrame(grouped_data[node_id])
#         node_data["timestamp"] = pd.to_datetime(node_data["timestamp"])
#
#         # Filter for load cell data
#         load_cell_data = node_data[node_data["data_type_name"] == "binary_hex_encoded"]
#         if not load_cell_data.empty:
#             # Debug: Check if load cell data has the expected fields
#             print(f"DEBUG: Load cell data for Node ID {node_id}:")
#             print(load_cell_data[["timestamp", "mean_force", "max_force"]])
#
#             # Ensure the fields for plotting are not null
#             load_cell_data = load_cell_data.dropna(subset=["mean_force", "max_force"])
#             if not load_cell_data.empty:
#                 # Extract mean and max forces
#                 mean_force = load_cell_data["mean_force"].astype(float)
#                 max_force = load_cell_data["max_force"].astype(float)
#
#                 # Plot mean force
#                 axs[row_idx].plot(load_cell_data["timestamp"], mean_force, color=color_brown_light, linestyle='-',
#                                   alpha=line_alpha, label=f"Load Cell Mean ({node_id})")
#                 axs[row_idx].scatter(load_cell_data["timestamp"], mean_force, color=color_brown_light,
#                                      s=marker_size ** 2, alpha=scatter_alpha)
#
#                 # Plot max force
#                 axs[row_idx].plot(load_cell_data["timestamp"], max_force, color=color_red_dark, linestyle='-',
#                                   alpha=line_alpha, label=f"Load Cell Max ({node_id})")
#                 axs[row_idx].scatter(load_cell_data["timestamp"], max_force, color=color_red_dark, s=marker_size ** 2,
#                                      alpha=scatter_alpha)
#
#                 # Left Y-axis for Force in Newtons
#                 axs[row_idx].set_ylabel("Force (N)")
#
#                 # Right Y-axis for Force in Pounds-Force
#                 ax_force_lbf = axs[row_idx].twinx()
#                 ax_force_lbf.set_ylabel("Force (lbf)")
#                 ax_force_lbf.set_ylim(axs[row_idx].get_ylim()[0] * newton_to_lbf,
#                                       axs[row_idx].get_ylim()[1] * newton_to_lbf)
#                 ax_force_lbf.tick_params(axis='y', labelcolor='black')
#
#                 axs[row_idx].legend(loc="upper left")
#                 row_idx += 1
#
#     axs[row_idx - 1].set_xlabel("Time (UTC)")
#     plt.tight_layout()
#     plt.show()

def plot_data(grouped_data, unique_node_ids, wave_data, spotter_id):
    """
    Generate detailed plots for wave height, managed sensor data, and unmanaged sensor data.

    Args:
        grouped_data (dict): Grouped sensor data by Node ID or position.
        unique_node_ids (set): Unique Node IDs for unmanaged data.
        wave_data (dict): Parsed wave data.
        spotter_id (str): ID of the Spotter buoy.
    """
    import matplotlib.pyplot as plt

    # Setup plot with subplots
    fig, axs = plt.subplots(4, 1, figsize=(12, 16), sharex=True)
    fig.suptitle(f"Time Series Data for Spotter ID: {spotter_id}", fontsize=16)

    # Plot 1: Significant Wave Height
    wave_df = pd.DataFrame(wave_data.get("waves", []))
    wave_df["timestamp"] = pd.to_datetime(wave_df["timestamp"])
    axs[0].plot(wave_df["timestamp"], wave_df["significantWaveHeight"], label="Wave Height (m)", color="blue")
    axs[0].set_ylabel("Wave Height (m)")
    axs[0].legend(loc="upper left")

    # Managed sensor data
    for group_key, df in grouped_data.items():
        if "unit_type" in df.columns:
            for unit_type in df["unit_type"].unique():
                data = df[df["unit_type"] == unit_type]
                if unit_type == "pressure_mean":
                    axs[1].plot(data["timestamp"], data["value"], label=f"{group_key} Pressure Mean", color="green")
                elif unit_type == "speed":
                    axs[2].plot(data["timestamp"], data["value"], label=f"{group_key} Speed (m/s)", color="orange")

    # Unmanaged sensor data (e.g., Load Cell)
    for node_id in unique_node_ids:
        if node_id in grouped_data:
            df = grouped_data[node_id]
            axs[3].plot(df["timestamp"], df["mean_force"], label=f"{node_id} Mean Force", color="red")

    # Finalize the plots
    axs[3].set_xlabel("Time (UTC)")
    for ax in axs:
        ax.legend()
    plt.tight_layout()
    plt.show()
