import tkinter as tk
from tkinter import messagebox, scrolledtext
import googlemaps
import re
import gmplot
import webbrowser

API_KEY = "KEY"  # Put your key here
gmaps = googlemaps.Client(key=API_KEY)

root = tk.Tk()
root.title("Public Transport Trip Planner")
root.geometry("700x700")

tk.Label(root, text="Start Location:").pack(pady=5)
start_entry = tk.Entry(root, width=60)
start_entry.pack()

tk.Label(root, text="Destination:").pack(pady=5)
end_entry = tk.Entry(root, width=60)
end_entry.pack()

use_waypoints_var = tk.BooleanVar()
tk.Checkbutton(root, text="Add intermediate stops", variable=use_waypoints_var, command=lambda: toggle_waypoints()).pack(pady=5)

waypoints_frame = tk.Frame(root)
waypoints_frame.pack(pady=5)
waypoint_entries = []
waypoint_names = [entry[0].get().strip() for entry in waypoint_entries if entry[0].get().strip()]


MAX_WAYPOINTS = 2


output_text = scrolledtext.ScrolledText(root, width=80, height=25, wrap=tk.WORD)
output_text.pack(pady=10)

mode_colors = {
    'WALKING': '#2E86C1',
    'TRANSIT': '#27AE60',
    'BUS': '#D68910',
    'RAIL': '#AF7AC5',
    'SUBWAY': '#C0392B',
    'FERRY': '#17A589',
    'DEFAULT': '#000000'
}

mode_emojis = {
    'WALKING': '🚶‍♂️',
    'TRANSIT': '🚍',
    'BUS': '🚌',
    'RAIL': '🚆',
    'SUBWAY': '🚇',
    'FERRY': '⛴️',
}

def get_mode_icon_and_color(step):
    travel_mode = step.get('travel_mode', 'DEFAULT')
    icon = mode_emojis.get(travel_mode, '🚍')
    color = mode_colors.get(travel_mode, mode_colors['DEFAULT'])

    if travel_mode == 'TRANSIT':
        line = step.get('transit_details', {}).get('line', {})
        vehicle_type = line.get('vehicle', {}).get('type', '').upper()
        if vehicle_type in mode_emojis:
            icon = mode_emojis[vehicle_type]
        if vehicle_type in mode_colors:
            color = mode_colors[vehicle_type]
    return icon, color

def generate_map(start_coords, end_coords, path_coords, route_steps_html):
    try:
        # Step 1: Generate map using gmplot and save to 'map_only.html'
        lats, lngs = zip(*[(float(p['lat']), float(p['lng'])) for p in path_coords])
        gmap = gmplot.GoogleMapPlotter(start_coords[0], start_coords[1], 13, apikey=API_KEY)
        gmap.plot(lats, lngs, 'blue', edge_width=4)
        gmap.marker(start_coords[0], start_coords[1], color='green', title="Start")
        gmap.marker(end_coords[0], end_coords[1], color='red', title="End")
        gmap.draw("map_only.html")  # this file will be loaded in iframe

        # Step 2: Create main HTML with sidebar and iframe for map
        with open("route_map.html", "w", encoding="utf-8") as f:
            f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Route Map</title>
    <style>
        body {{
            margin: 0;
            font-family: Arial, sans-serif;
        }}
        #container {{
            display: flex;
            height: 100vh;
        }}
        #sidebar {{
            width: 35%;
            padding: 20px;
            overflow-y: auto;
            background-color: #f4f4f4;
            border-right: 1px solid #ccc;
        }}
        #map {{
            flex-grow: 1;
        }}
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        .step {{
            margin-bottom: 15px;
            padding: 10px;
            background: white;
            border-left: 5px solid #3498db;
            box-shadow: 0 0 5px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div id="container">
        <div id="sidebar">
            <h2>Route Details</h2>
            {route_steps_html}
        </div>
        <div id="map">
            <iframe src="map_only.html"></iframe>
        </div>
    </div>
</body>
</html>
""")
        # Step 3: Open final HTML page
        webbrowser.open("route_map.html")

    except Exception as e:
        messagebox.showerror("Map Error", f"Error generating map:\n{e}")


def plan_trip():
    start = start_entry.get().strip()
    end = end_entry.get().strip()

    # Validate start and end early
    if not start or not end:
        messagebox.showwarning("Missing Info", "Please enter both start and destination locations.")
        return

    # Collect and validate waypoints (if checkbox is active)
    waypoints = []
    stay_durations = []

    if use_waypoints_var.get():
        for stop_entry, stay_entry in waypoint_entries:
            location = stop_entry.get().strip()
            stay = stay_entry.get().strip()
            if not location or not stay:
                messagebox.showwarning("Missing Info", "Each intermediate stop and stay duration must be filled.")
                return
            try:
                stay_minutes = int(stay)
            except ValueError:
                messagebox.showwarning("Invalid Time", "Stay duration must be an integer (in minutes).")
                return
            waypoints.append(location)
            stay_durations.append(stay_minutes)

    # Build full list of route points: start → [waypoints...] → end
    route_points = [start] + waypoints + [end]
    total_stay_time = sum(stay_durations)

    all_steps = []
    total_duration_minutes = 0
    all_path_coords = []
    route_steps_html = ""

    output_text.delete('1.0', tk.END)
    waypoint_names = [entry[0].get().strip() for entry in waypoint_entries if entry[0].get().strip()]
    if waypoint_names:
        route_str = f"Route: {start} → " + " → ".join(waypoint_names) + f" → {end}\n"
    else:
        route_str = f"Route: {start} → {end}\n"

    output_text.insert(tk.END, route_str)

    try:
        for i in range(len(route_points) - 1):
            origin = route_points[i]
            destination = route_points[i + 1]

            directions = gmaps.directions(origin, destination, mode="transit", departure_time="now")

            if not directions:
                messagebox.showerror("No Route", f"No transit route found from {origin} to {destination}.")
                return

            leg = directions[0]['legs'][0]
            steps = leg['steps']
            duration_minutes = leg['duration']['value'] // 60
            total_duration_minutes += duration_minutes

            output_text.insert(tk.END, f"\nLeg {i + 1}: {origin} → {destination} ({duration_minutes} min)\n")

            for j, step in enumerate(steps, start=1):
                icon, color = get_mode_icon_and_color(step)
                travel_mode = step['travel_mode']
                instruction = re.sub('<.*?>', '', step['html_instructions'])
                step_duration = step['duration']['text']

                # Extra transit details
                extra_info_gui = ""
                extra_info_html = ""

                if travel_mode == 'TRANSIT':
                    transit = step.get('transit_details', {})
                    line = transit.get('line', {})
                    vehicle = line.get('vehicle', {})
                    line_name = line.get('short_name') or line.get('name') or ""
                    vehicle_type = vehicle.get('type', '')
                    departure_stop = transit.get('departure_stop', {}).get('name', '')
                    arrival_stop = transit.get('arrival_stop', {}).get('name', '')
                    num_stops = transit.get('num_stops', 0)

                    extra_info_gui = (
                        f"\n    Line: {line_name} ({vehicle_type})"
                        f"\n    From: {departure_stop} → To: {arrival_stop}"
                        f"\n    Stops: {num_stops}"
                    )
                    extra_info_html = (
                        f"<br><strong>Line:</strong> {line_name} ({vehicle_type})"
                        f"<br><strong>From:</strong> {departure_stop} → <strong>To:</strong> {arrival_stop}"
                        f"<br><strong>Stops:</strong> {num_stops}"
                    )

                step_text = f"{j}. {icon} [{travel_mode}] {instruction} ({step_duration}){extra_info_gui}\n\n"
                start_idx = output_text.index(tk.END)
                output_text.insert(tk.END, step_text)
                end_idx = output_text.index(tk.END)
                output_text.tag_add(f"color{i}_{j}", start_idx, end_idx)
                output_text.tag_config(f"color{i}_{j}", foreground=color)

                route_steps_html += f"""
                <div class='step' style="border-color: {color};">
                    <strong>{j}. {icon} [{travel_mode}]</strong><br>
                    {instruction} ({step_duration}){extra_info_html}
                </div>
                """

            # Append decoded polyline for this segment
            polyline = directions[0]['overview_polyline']['points']
            all_path_coords.extend(googlemaps.convert.decode_polyline(polyline))

        # Total time: transit duration + stop durations
        full_trip_time = total_duration_minutes + total_stay_time

        if total_stay_time > 0:
            output_text.insert(tk.END, f"\nStay Time at Stops: {total_stay_time} minutes\n")

        output_text.insert(tk.END, f"\n⏱️ Total Trip Time: {full_trip_time} minutes\n")

        # Get start and end coords for map markers
        start_geocode = gmaps.geocode(start)[0]['geometry']['location']
        end_geocode = gmaps.geocode(end)[0]['geometry']['location']
        start_coords = (start_geocode['lat'], start_geocode['lng'])
        end_coords = (end_geocode['lat'], end_geocode['lng'])

        generate_map(start_coords, end_coords, all_path_coords, route_steps_html)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while planning your trip:\n{e}")


def add_waypoint():
    if len(waypoint_entries) >= MAX_WAYPOINTS:
        messagebox.showinfo("Limit Reached", f"Transit mode only supports {MAX_WAYPOINTS} intermediate stops.")
        return

    row = tk.Frame(waypoints_frame)
    tk.Label(row, text="Stop:", width=6).pack(side=tk.LEFT)
    stop_entry = tk.Entry(row, width=30)
    stop_entry.pack(side=tk.LEFT, padx=2)
    tk.Label(row, text="Stay (min):", width=10).pack(side=tk.LEFT)
    stay_entry = tk.Entry(row, width=6)
    stay_entry.pack(side=tk.LEFT)

    # Optional: Add remove button
    def remove():
        waypoint_entries.remove((stop_entry, stay_entry))
        row.destroy()
        # Re-enable the add button if needed
        if len(waypoint_entries) < MAX_WAYPOINTS:
            add_waypoint_btn.config(state=tk.NORMAL)

    tk.Button(row, text="✕", command=remove, fg="red").pack(side=tk.LEFT, padx=5)

    row.pack(pady=2)
    waypoint_entries.append((stop_entry, stay_entry))

    if len(waypoint_entries) >= MAX_WAYPOINTS:
        add_waypoint_btn.config(state=tk.DISABLED)


def toggle_waypoints():
    if use_waypoints_var.get():
        add_waypoint_btn.pack(pady=3)
        add_waypoint()
    else:
        for widget in waypoints_frame.winfo_children():
            widget.destroy()
        waypoint_entries.clear()
        add_waypoint_btn.pack_forget()
        add_waypoint_btn.config(state=tk.NORMAL)

add_waypoint_btn = tk.Button(root, text="Add another stop", command=add_waypoint)

tk.Button(root, text="Plan Route", command=plan_trip).pack(pady=10)

root.mainloop()