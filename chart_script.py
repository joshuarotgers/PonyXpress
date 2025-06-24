import plotly.graph_objects as go
import plotly.express as px
import json

# Define the data with shortened names to meet 15-char limit
data = {
  "components": [
    {"name": "PONYXPRESS Core", "type": "core", "x": 5, "y": 5},
    {"name": "AI Assistant", "type": "feature", "x": 3, "y": 3},
    {"name": "Maps & GPS", "type": "feature", "x": 7, "y": 3},
    {"name": "Barcode Scanner", "type": "feature", "x": 3, "y": 7},
    {"name": "Camera & Sig", "type": "feature", "x": 7, "y": 7},
    {"name": "Local Storage", "type": "data", "x": 5, "y": 8},
    {"name": "Cloud Sync", "type": "data", "x": 5, "y": 2},
    {"name": "Admin Dashboard", "type": "interface", "x": 9, "y": 5}
  ],
  "platforms": [
    {"name": "Web/PWA", "x": 1, "y": 1},
    {"name": "Android", "x": 1, "y": 3},
    {"name": "iOS", "x": 1, "y": 5},
    {"name": "Windows", "x": 1, "y": 7},
    {"name": "macOS", "x": 1, "y": 9},
    {"name": "Linux", "x": 1, "y": 11}
  ],
  "roles": [
    {"name": "Carrier", "x": 12, "y": 2},
    {"name": "Substitute", "x": 12, "y": 4},
    {"name": "Supervisor", "x": 12, "y": 6},
    {"name": "Admin", "x": 12, "y": 8}
  ],
  "features": [
    {"name": "Route Optimize", "x": 9, "y": 1},
    {"name": "Voice Commands", "x": 9, "y": 2},
    {"name": "Package Scan", "x": 9, "y": 3},
    {"name": "Proof Delivery", "x": 9, "y": 7},
    {"name": "Time Tracking", "x": 9, "y": 8},
    {"name": "Offline Ops", "x": 9, "y": 9}
  ]
}

# Color mapping for different types
colors = {
    "core": "#1FB8CD",
    "feature": "#FFC185", 
    "data": "#5D878F",
    "interface": "#ECEBD5",
    "platforms": "#D2BA4C",
    "roles": "#B4413C",
    "features": "#964325"
}

# Create figure
fig = go.Figure()

# Add all components as scatter points (invisible) and shapes (visible rectangles)
all_items = []

# Add main components
for comp in data["components"]:
    all_items.append({
        "x": comp["x"], "y": comp["y"], "name": comp["name"], 
        "color": colors[comp["type"]], "category": "Components"
    })

# Add platforms
for platform in data["platforms"]:
    all_items.append({
        "x": platform["x"], "y": platform["y"], "name": platform["name"],
        "color": colors["platforms"], "category": "Platforms"
    })

# Add roles  
for role in data["roles"]:
    all_items.append({
        "x": role["x"], "y": role["y"], "name": role["name"],
        "color": colors["roles"], "category": "Roles"
    })

# Add features
for feature in data["features"]:
    all_items.append({
        "x": feature["x"], "y": feature["y"], "name": feature["name"],
        "color": colors["features"], "category": "Features"
    })

# Add invisible scatter points for positioning
fig.add_trace(go.Scatter(
    x=[item["x"] for item in all_items],
    y=[item["y"] for item in all_items],
    mode='markers',
    marker=dict(size=1, opacity=0),
    showlegend=False,
    hoverinfo='none'
))

# Add rectangles and text for each item
for item in all_items:
    # Add rectangle
    fig.add_shape(
        type="rect",
        x0=item["x"]-0.8, y0=item["y"]-0.3,
        x1=item["x"]+0.8, y1=item["y"]+0.3,
        line=dict(color="white", width=2),
        fillcolor=item["color"],
        opacity=0.8
    )
    
    # Add text
    fig.add_annotation(
        x=item["x"], y=item["y"],
        text=item["name"],
        showarrow=False,
        font=dict(color="white", size=10, family="Arial"),
        bgcolor="rgba(0,0,0,0)"
    )

# Add connecting lines from core to main components
core_x, core_y = 5, 5
connections = [
    (3, 3), (7, 3), (3, 7), (7, 7),  # Feature components
    (5, 8), (5, 2),  # Data components
    (9, 5)  # Admin dashboard
]

for conn_x, conn_y in connections:
    fig.add_shape(
        type="line",
        x0=core_x, y0=core_y,
        x1=conn_x, y1=conn_y,
        line=dict(color="#13343B", width=2, dash="dot"),
        opacity=0.6
    )

# Add connecting lines from platforms to core
for platform in data["platforms"]:
    fig.add_shape(
        type="line",
        x0=platform["x"], y0=platform["y"],
        x1=core_x, y1=core_y,
        line=dict(color="#13343B", width=1, dash="dash"),
        opacity=0.4
    )

# Update layout and axes
fig.update_layout(
    title="PONYXPRESS System Architecture",
    showlegend=False,
    plot_bgcolor='white'
)

fig.update_xaxes(
    range=[-0.5, 13.5],
    showgrid=False,
    showticklabels=False,
    zeroline=False
)

fig.update_yaxes(
    range=[0, 12],
    showgrid=False,
    showticklabels=False,
    zeroline=False
)

# Save the chart
fig.write_image("ponyxpress_architecture.png", width=1200, height=800)