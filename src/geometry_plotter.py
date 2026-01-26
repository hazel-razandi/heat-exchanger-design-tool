"""
Tube Bundle Layout Visualizer
Author: KAKAROTONCLOUD
Version: 3.1.0 Enterprise
"""
import matplotlib.pyplot as plt
import io

def plot_tube_layout(n_tubes, shell_id, tube_od, pitch_ratio=1.25):
    """
    Generates a mechanical cross-section of the tube bundle using Matplotlib.
    Returns a BytesIO image buffer for Streamlit.
    """
    # Create figure without GUI backend
    plt.ioff() 
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # 1. Draw Shell (Outer Circle)
    # Light gray background for shell
    shell = plt.Circle((0, 0), shell_id/2, color='#f0f2f6', fill=True)
    ax.add_patch(shell)
    # Black outline
    shell_outline = plt.Circle((0, 0), shell_id/2, color='black', fill=False, linewidth=2.0)
    ax.add_patch(shell_outline)

    # 2. Calculate Tube Positions (Triangular Pitch - 30 degrees)
    pitch = tube_od * pitch_ratio
    
    # Clearance from shell wall (typically shell_id/20)
    clearance = shell_id * 0.05
    r_max = (shell_id/2) - (tube_od/2) - clearance
    
    tubes_drawn = 0
    # Simple hex packing scan
    # Limit scan range to avoid infinite loops
    limit = int(shell_id / pitch) + 2
    
    for y_idx in range(-limit, limit + 1):
        # Vertical spacing for triangular pitch is pitch * sin(60)
        y = y_idx * pitch * 0.866
        
        # Offset every other row
        offset = (pitch / 2) if (y_idx % 2) != 0 else 0
        
        for x_idx in range(-limit, limit + 1):
            x = x_idx * pitch + offset
            
            # Check if tube fits inside shell boundaries
            dist = (x**2 + y**2)**0.5
            if dist <= r_max:
                if tubes_drawn < n_tubes:
                    # Draw Tube
                    tube = plt.Circle((x, y), tube_od/2, color='#0068C9', fill=True, alpha=0.8)
                    tube_edge = plt.Circle((x, y), tube_od/2, color='white', fill=False, linewidth=0.5)
                    ax.add_patch(tube)
                    ax.add_patch(tube_edge)
                    tubes_drawn += 1

    # 3. Formatting
    limit_view = shell_id * 0.6
    ax.set_xlim(-limit_view, limit_view)
    ax.set_ylim(-limit_view, limit_view)
    ax.set_aspect('equal')
    ax.axis('off') # Hide axes for CAD look
    
    # Add Title inside plot
    plt.text(0, -limit_view*0.9, f"TEMA Bundle: {tubes_drawn} Tubes", 
             ha='center', fontsize=10, fontweight='bold', color='#555')

    # Convert to image for Streamlit
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf

