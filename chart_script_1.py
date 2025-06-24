import plotly.graph_objects as go
import plotly.io as pio

# Data for the flowchart with improved layout
workflow_data = {
  "workflow_steps": [
    {"id": 1, "type": "start", "text": "Launch App", "x": 5, "y": 1},
    {"id": 2, "type": "process", "text": "Select Role", "x": 5, "y": 2},
    {"id": 3, "type": "process", "text": "Voice Training", "x": 5, "y": 3},
    {"id": 4, "type": "process", "text": "Load Route", "x": 5, "y": 4},
    {"id": 5, "type": "process", "text": "Equipment Check", "x": 5, "y": 5},
    {"id": 6, "type": "process", "text": "Start Route", "x": 5, "y": 6},
    {"id": 7, "type": "process", "text": "Navigate Stop", "x": 5, "y": 7},
    {"id": 8, "type": "process", "text": "Scan Package", "x": 5, "y": 8},
    {"id": 9, "type": "decision", "text": "Customer Here?", "x": 5, "y": 9},
    {"id": 10, "type": "process", "text": "Deliver Pkg", "x": 2, "y": 10},
    {"id": 11, "type": "process", "text": "Leave Notice", "x": 8, "y": 10},
    {"id": 12, "type": "process", "text": "Capture Proof", "x": 2, "y": 11},
    {"id": 13, "type": "process", "text": "Voice: Delivered", "x": 2, "y": 12},
    {"id": 14, "type": "process", "text": "Voice: Attempted", "x": 8, "y": 11},
    {"id": 15, "type": "decision", "text": "More Stops?", "x": 5, "y": 13},
    {"id": 16, "type": "process", "text": "Complete Route", "x": 5, "y": 14},
    {"id": 17, "type": "process", "text": "Sync Data", "x": 5, "y": 15},
    {"id": 18, "type": "end", "text": "Generate Report", "x": 5, "y": 16}
  ],
  "connections": [
    {"from": 1, "to": 2},
    {"from": 2, "to": 3},
    {"from": 3, "to": 4},
    {"from": 4, "to": 5},
    {"from": 5, "to": 6},
    {"from": 6, "to": 7},
    {"from": 7, "to": 8},
    {"from": 8, "to": 9},
    {"from": 9, "to": 10, "label": "Yes"},
    {"from": 9, "to": 11, "label": "No"},
    {"from": 10, "to": 12},
    {"from": 12, "to": 13},
    {"from": 11, "to": 14},
    {"from": 13, "to": 15},
    {"from": 14, "to": 15},
    {"from": 15, "to": 7, "label": "Yes"},
    {"from": 15, "to": 16, "label": "No"},
    {"from": 16, "to": 17},
    {"from": 17, "to": 18}
  ]
}

# Brand colors
colors = ['#1FB8CD', '#FFC185', '#ECEBD5', '#5D878F', '#D2BA4C']

# Create figure
fig = go.Figure()

# Add connection lines and arrows
for conn in workflow_data['connections']:
    from_step = next(s for s in workflow_data['workflow_steps'] if s['id'] == conn['from'])
    to_step = next(s for s in workflow_data['workflow_steps'] if s['id'] == conn['to'])
    
    x0, y0 = from_step['x'], from_step['y']
    x1, y1 = to_step['x'], to_step['y']
    
    # Special handling for loop back connection
    if conn['from'] == 15 and conn['to'] == 7:  # More Stops? -> Navigate Stop
        # Create curved path for loop back
        fig.add_shape(
            type="path",
            path=f"M {x0+0.7},{y0} Q {x0+2},{y0-3} {x1+0.7},{y1}",
            line=dict(color='#13343B', width=2)
        )
        # Add arrow at end
        fig.add_annotation(
            x=x1+0.7, y=y1-0.1,
            ax=x1+0.9, ay=y1-0.3,
            arrowhead=2, arrowsize=1, arrowwidth=2,
            arrowcolor='#13343B',
            showarrow=True,
            text=""
        )
    else:
        # Regular straight line
        fig.add_shape(
            type="line",
            x0=x0, y0=y0, x1=x1, y1=y1,
            line=dict(color='#13343B', width=2)
        )
        # Add arrow head
        if abs(x1-x0) > 0.1 or abs(y1-y0) > 0.1:
            fig.add_annotation(
                x=x1, y=y1,
                ax=x0, ay=y0,
                arrowhead=2, arrowsize=1, arrowwidth=2,
                arrowcolor='#13343B',
                showarrow=True,
                text=""
            )

# Add shapes for each workflow step
for i, step in enumerate(workflow_data['workflow_steps']):
    x, y = step['x'], step['y']
    step_type = step['type']
    text = step['text']
    
    # Choose color
    color = colors[i % len(colors)]
    
    if step_type == 'start' or step_type == 'end':
        # Oval shape
        fig.add_shape(
            type="circle",
            x0=x-0.8, y0=y-0.3, x1=x+0.8, y1=y+0.3,
            fillcolor=color,
            line=dict(color='#13343B', width=2)
        )
        # Add icon for start/end
        icon = "🚀" if step_type == 'start' else "📊"
        fig.add_annotation(
            x=x, y=y+0.1,
            text=f"{icon}<br>{text}",
            showarrow=False,
            font=dict(size=11, color='black'),
            bgcolor="rgba(255,255,255,0.8)"
        )
    
    elif step_type == 'decision':
        # Diamond shape
        fig.add_shape(
            type="path",
            path=f"M {x},{y-0.4} L {x+0.8},{y} L {x},{y+0.4} L {x-0.8},{y} Z",
            fillcolor=color,
            line=dict(color='#13343B', width=2)
        )
        # Add icon for decision
        fig.add_annotation(
            x=x, y=y,
            text=f"❓<br>{text}",
            showarrow=False,
            font=dict(size=10, color='black'),
            bgcolor="rgba(255,255,255,0.8)"
        )
    
    else:  # process
        # Rectangle shape
        fig.add_shape(
            type="rect",
            x0=x-0.8, y0=y-0.3, x1=x+0.8, y1=y+0.3,
            fillcolor=color,
            line=dict(color='#13343B', width=2)
        )
        # Add appropriate icon based on text content
        if "scan" in text.lower():
            icon = "📱"
        elif "voice" in text.lower():
            icon = "🎤"
        elif "navigate" in text.lower():
            icon = "🧭"
        elif "deliver" in text.lower():
            icon = "📦"
        elif "capture" in text.lower():
            icon = "📸"
        elif "sync" in text.lower():
            icon = "☁️"
        elif "equipment" in text.lower():
            icon = "⚙️"
        elif "route" in text.lower():
            icon = "🗺️"
        else:
            icon = "📋"
            
        fig.add_annotation(
            x=x, y=y,
            text=f"{icon}<br>{text}",
            showarrow=False,
            font=dict(size=10, color='black'),
            bgcolor="rgba(255,255,255,0.8)"
        )

# Add connection labels
for conn in workflow_data['connections']:
    if 'label' in conn:
        from_step = next(s for s in workflow_data['workflow_steps'] if s['id'] == conn['from'])
        to_step = next(s for s in workflow_data['workflow_steps'] if s['id'] == conn['to'])
        
        # Position label appropriately
        if conn['from'] == 15 and conn['to'] == 7:  # Loop back
            fig.add_annotation(
                x=7, y=10,
                text=conn['label'],
                showarrow=False,
                font=dict(size=12, color='#13343B'),
                bgcolor="white",
                bordercolor="#13343B",
                borderwidth=1
            )
        else:
            mid_x = (from_step['x'] + to_step['x']) / 2
            mid_y = (from_step['y'] + to_step['y']) / 2
            
            # Offset label slightly to avoid overlap with line
            if from_step['x'] != to_step['x']:
                mid_y += 0.2
            else:
                mid_x += 0.3
                
            fig.add_annotation(
                x=mid_x, y=mid_y,
                text=conn['label'],
                showarrow=False,
                font=dict(size=12, color='#13343B'),
                bgcolor="white",
                bordercolor="#13343B",
                borderwidth=1
            )

# Update layout
fig.update_layout(
    title="PONYXPRESS Delivery Workflow",
    showlegend=False
)

# Update axes
fig.update_xaxes(
    range=[0, 10],
    showgrid=False,
    showticklabels=False,
    zeroline=False
)

fig.update_yaxes(
    range=[0, 17],
    showgrid=False,
    showticklabels=False,
    zeroline=False,
    autorange='reversed'
)

# Save the chart
fig.write_image("ponyxpress_workflow.png")
fig.show()