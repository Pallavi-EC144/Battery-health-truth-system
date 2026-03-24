"""
Visualization for Battery Health System
"""

import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class BatteryVisualizer:
    """Creates professional visualizations"""
    
    @staticmethod
    def plot_soc_comparison(true_soc, estimated_soc, title="State of Charge Comparison"):
        """Compare true vs estimated SoC"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        time = range(len(true_soc))
        
        ax.plot(time, np.array(true_soc) * 100, 'b-', linewidth=2, label='True SoC')
        ax.plot(time, np.array(estimated_soc) * 100, 'r--', linewidth=2, label='Estimated SoC')
        ax.fill_between(time, np.array(true_soc) * 100, np.array(estimated_soc) * 100, alpha=0.3, color='gray')
        
        ax.set_xlabel('Time (seconds)', fontsize=12)
        ax.set_ylabel('State of Charge (%)', fontsize=12)
        ax.set_title(title, fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 105)
        
        # Calculate error
        error = np.mean(np.abs(np.array(true_soc) - np.array(estimated_soc))) * 100
        ax.text(0.02, 0.98, f'Mean Error: {error:.2f}%', transform=ax.transAxes, 
                fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        return fig
    
    @staticmethod
    def plot_voltage_curve(voltages, currents, title="Battery Voltage Under Load"):
        """Plot voltage and current over time"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        time = range(len(voltages))
        
        ax1.plot(time, voltages, 'g-', linewidth=2)
        ax1.set_ylabel('Voltage (V)', fontsize=12)
        ax1.set_title(title, fontsize=14)
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(2.8, 4.3)
        
        ax2.plot(time, currents, 'r-', linewidth=2)
        ax2.set_xlabel('Time (seconds)', fontsize=12)
        ax2.set_ylabel('Current (A)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def plot_error_analysis(true_soc, estimated_soc):
        """Plot error distribution"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        errors = np.array(true_soc) - np.array(estimated_soc)
        
        # Error over time
        ax1.plot(range(len(errors)), errors * 100, 'b-', linewidth=2)
        ax1.axhline(y=0, color='r', linestyle='--')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Error (%)')
        ax1.set_title('Estimation Error Over Time')
        ax1.grid(True, alpha=0.3)
        
        # Error histogram
        ax2.hist(errors * 100, bins=20, color='skyblue', edgecolor='black')
        ax2.set_xlabel('Error (%)')
        ax2.set_ylabel('Frequency')
        ax2.set_title('Error Distribution')
        ax2.axvline(x=0, color='r', linestyle='--')
        
        plt.tight_layout()
        return fig
    
    @staticmethod
    def create_3d_surface(voltages, currents, soc):
        """Create 3D visualization of battery behavior"""
        fig = go.Figure(data=[go.Scatter3d(
            x=voltages,
            y=currents,
            z=soc,
            mode='markers',
            marker=dict(
                size=4,
                color=soc,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="SoC")
            )
        )])
        
        fig.update_layout(
            title="Battery State Space",
            scene=dict(
                xaxis_title="Voltage (V)",
                yaxis_title="Current (A)",
                zaxis_title="State of Charge (%)"
            ),
            height=500
        )
        
        return fig
