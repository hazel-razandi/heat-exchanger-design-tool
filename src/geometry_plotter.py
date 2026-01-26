"""
Visualizer
"""
import matplotlib.pyplot as plt
import io

def plot_tube_layout(n_tubes, shell_id):
    plt.ioff()
    fig, ax = plt.subplots(figsize=(4,4))
    shell = plt.Circle((0,0), shell_id/2, color='#eee', fill=True)
    ax.add_patch(shell)
    ax.add_patch(plt.Circle((0,0), shell_id/2, fill=False, lw=2))
    
    # Rough approximation of filled area for visual
    r_fill = (n_tubes**0.5) * 0.02 * 1.3 
    ax.add_patch(plt.Circle((0,0), r_fill, color='#0068c9', alpha=0.5, label='Tube Bundle'))
    
    ax.set_xlim(-shell_id*0.6, shell_id*0.6)
    ax.set_ylim(-shell_id*0.6, shell_id*0.6)
    ax.axis('off')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    return buf
