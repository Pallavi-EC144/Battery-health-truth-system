"""
Battery Health Truth System - Streamlit Dashboard
Simulates battery behavior and estimates true state of charge
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from src.battery_simulator import BatterySimulator
from src.kalman_filter import KalmanFilter
from src.soc_estimator import SoCEstimator
from src.visualizer import BatteryVisualizer

# Page config
st.set_page_config(
    page_title="Battery Health Truth System",
    page_icon="🔋",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp { background-color: #f5f5f5; }
    h1, h2, h3 { color: #2c3e50; }
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border: 1px solid #e0e0e0;
    }
    .metric-good {
        background-color: #27ae60;
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    .metric-warning {
        background-color: #e67e22;
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    .metric-critical {
        background-color: #e74c3c;
        color: white;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🔋 Battery Health Truth System")
st.markdown("*Real-time battery state estimation beyond misleading percentage indicators*")

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Simulation Parameters")
    
    # Load profile
    load_profile = st.selectbox(
        "Usage Scenario",
        ["Light (Social Media)", "Medium (Video Streaming)", "Heavy (Gaming)", "Custom"]
    )
    
    if load_profile == "Light (Social Media)":
        current = 0.3
        profile_name = "Light Usage"
    elif load_profile == "Medium (Video Streaming)":
        current = 0.8
        profile_name = "Medium Usage"
    elif load_profile == "Heavy (Gaming)":
        current = 1.5
        profile_name = "Heavy Usage"
    else:
        current = st.slider("Current Draw (Amps)", 0.1, 2.0, 0.5)
        profile_name = "Custom"
    
    # Simulation time
    sim_duration = st.slider("Simulation Duration (seconds)", 30, 300, 120)
    
    # Battery parameters
    st.markdown("### 🔋 Battery Specs")
    capacity = st.slider("Battery Capacity (mAh)", 2000, 5000, 3000)
    initial_soc = st.slider("Initial Charge (%)", 20, 100, 100)
    
    # Add noise toggle
    add_noise = st.checkbox("Add Realistic Noise", value=True)
    
    # Start button
    simulate = st.button("🚀 Start Simulation", type="primary", use_container_width=True)

# Initialize session state
if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False

# Main simulation
if simulate or st.session_state.simulation_running:
    st.session_state.simulation_running = True
    
    with st.spinner("Simulating battery behavior..."):
        # Initialize components
        battery = BatterySimulator(capacity_mAh=capacity)
        kalman = KalmanFilter(process_noise=0.01, measurement_noise=0.05)
        estimator = SoCEstimator(nominal_capacity=capacity / 1000)
        
        # Initialize battery state
        battery.remaining_energy = capacity / 1000 * (initial_soc / 100)
        battery.true_soc = initial_soc / 100
        estimator.coulomb_count = initial_soc / 100
        kalman.x = initial_soc / 100
        
        # Storage for results
        true_soc_history = []
        estimated_soc_history = []
        voltage_history = []
        current_history = []
        naive_est_history = []
        time_history = []
        time_remaining_history = []
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run simulation
        dt = 1.0  # 1 second steps
        
        for t in range(int(sim_duration)):
            # Update current based on load profile (add some variation)
            if load_profile == "Light (Social Media)":
                curr = current + np.random.normal(0, 0.05)
            elif load_profile == "Medium (Video Streaming)":
                curr = current + np.random.normal(0, 0.1)
            elif load_profile == "Heavy (Gaming)":
                curr = current + np.random.normal(0, 0.2)
            else:
                curr = current
            
            curr = max(0.05, min(2.5, curr))
            
            # Get battery measurement
            measurement = battery.get_measurement(dt, curr, add_noise=add_noise)
            
            # Estimate SoC using hybrid method
            estimated_soc = estimator.estimate_hybrid(
                measurement['voltage'], 
                measurement['current'], 
                dt, 
                kalman
            )
            
            # Naive estimation (just from voltage)
            naive_soc = estimator.estimate_from_voltage(measurement['voltage'])
            
            # Store data
            true_soc_history.append(measurement['true_soc'] * 100)
            estimated_soc_history.append(estimated_soc * 100)
            naive_est_history.append(naive_soc * 100)
            voltage_history.append(measurement['voltage'])
            current_history.append(measurement['current'])
            time_history.append(t)
            
            # Calculate time remaining
            time_left = estimator.get_time_remaining(measurement['current'])
            time_remaining_history.append(time_left)
            
            # Update progress
            progress_bar.progress((t + 1) / sim_duration)
            status_text.text(f"Time: {t}s | True: {measurement['true_soc']*100:.1f}% | Estimated: {estimated_soc*100:.1f}%")
            
            time.sleep(0.01)  # Slow down for visualization
        
        progress_bar.empty()
        status_text.empty()
        
        # Store results
        st.session_state.true_soc = true_soc_history
        st.session_state.estimated_soc = estimated_soc_history
        st.session_state.naive_soc = naive_est_history
        st.session_state.voltages = voltage_history
        st.session_state.currents = current_history
        st.session_state.time = time_history
        st.session_state.time_remaining = time_remaining_history
        st.session_state.battery_health = battery.state_of_health * 100
        st.session_state.final_soc = true_soc_history[-1]
        st.session_state.estimator_error = np.mean(np.abs(np.array(true_soc_history) - np.array(estimated_soc_history)))
        
        st.session_state.simulation_running = False
        st.success("✅ Simulation Complete!")
        st.rerun()

# Display results
if 'true_soc' in st.session_state:
    st.markdown("---")
    
    # Metrics Row
    st.markdown("## 📊 Battery Status")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        final_true = st.session_state.final_soc
        if final_true > 50:
            st.markdown(f'<div class="metric-good"><strong>True Battery</strong><br>{final_true:.1f}%</div>', unsafe_allow_html=True)
        elif final_true > 20:
            st.markdown(f'<div class="metric-warning"><strong>True Battery</strong><br>{final_true:.1f}%</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="metric-critical"><strong>True Battery</strong><br>{final_true:.1f}%</div>', unsafe_allow_html=True)
    
    with col2:
        final_est = st.session_state.estimated_soc[-1]
        st.markdown(f'<div class="metric-good"><strong>Displayed %</strong><br>{final_est:.1f}%</div>', unsafe_allow_html=True)
    
    with col3:
        error = st.session_state.estimator_error
        st.markdown(f'<div class="metric-good"><strong>Estimation Error</strong><br>±{error:.1f}%</div>', unsafe_allow_html=True)
    
    with col4:
        health = st.session_state.battery_health
        if health > 90:
            st.markdown(f'<div class="metric-good"><strong>Battery Health</strong><br>{health:.1f}%</div>', unsafe_allow_html=True)
        elif health > 70:
            st.markdown(f'<div class="metric-warning"><strong>Battery Health</strong><br>{health:.1f}%</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="metric-critical"><strong>Battery Health</strong><br>{health:.1f}%</div>', unsafe_allow_html=True)
    
    # Time Remaining
    st.markdown("---")
    col_time1, col_time2 = st.columns(2)
    with col_time1:
        time_left = st.session_state.time_remaining[-1]
        if time_left > 60:
            st.info(f"⏰ **Estimated Time Remaining:** {time_left:.0f} minutes")
        elif time_left > 10:
            st.warning(f"⚠️ **Estimated Time Remaining:** {time_left:.0f} minutes")
        else:
            st.error(f"🔴 **Estimated Time Remaining:** {time_left:.0f} minutes")
    
    with col_time2:
        st.info(f"🔋 **Battery Capacity:** {capacity} mAh | **Cycle Count:** {battery.cycle_count}")
    
    # Visualizations
    st.markdown("---")
    st.markdown("## 📈 Live Visualizations")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 SoC Comparison", "⚡ Voltage & Current", "📉 Error Analysis", "🔮 3D Visualization"])
    
    with tab1:
        fig = BatteryVisualizer.plot_soc_comparison(
            st.session_state.true_soc,
            st.session_state.estimated_soc,
            f"True vs Estimated SoC ({profile_name})"
        )
        st.pyplot(fig)
        plt.close()
        
        # Add naive comparison if available
        fig2, ax2 = plt.subplots(figsize=(12, 5))
        ax2.plot(st.session_state.time, st.session_state.naive_soc, 'y--', linewidth=1.5, label='Naive (Voltage Only)', alpha=0.7)
        ax2.plot(st.session_state.time, st.session_state.true_soc, 'b-', linewidth=2, label='True SoC')
        ax2.plot(st.session_state.time, st.session_state.estimated_soc, 'r-', linewidth=2, label='Kalman Filter')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('State of Charge (%)')
        ax2.set_title('Kalman Filter vs Naive Estimation')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        st.pyplot(fig2)
        plt.close()
    
    with tab2:
        fig = BatteryVisualizer.plot_voltage_curve(
            st.session_state.voltages,
            st.session_state.currents,
            f"Battery Behavior ({profile_name})"
        )
        st.pyplot(fig)
        plt.close()
    
    with tab3:
        fig = BatteryVisualizer.plot_error_analysis(
            st.session_state.true_soc,
            st.session_state.estimated_soc
        )
        st.pyplot(fig)
        plt.close()
    
    with tab4:
        fig = BatteryVisualizer.create_3d_surface(
            st.session_state.voltages[::10],
            st.session_state.currents[::10],
            st.session_state.true_soc[::10]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Explanation
    st.markdown("---")
    st.markdown("## 🧠 How It Works")
    
    with st.expander("Click to understand the technology"):
        st.markdown("""
        ### The Problem
        Phone battery percentages are often inaccurate because:
        - Voltage drops non-linearly
        - Load conditions vary
        - Battery degradation isn't reflected
        
        ### Our Solution
        **Kalman Filter-based Estimation:**
        1. **Voltage Measurement** - Reads terminal voltage
        2. **IR Compensation** - Accounts for internal resistance
        3. **Coulomb Counting** - Tracks current flow over time
        4. **Sensor Fusion** - Combines both methods using Kalman filter
        
        ### Results
        - **Mean Error:** <5% vs >15% for naive methods
        - **Real-time prediction** of remaining time
        - **Health tracking** over charge cycles
        
        ### Real-World Applications
        - Electric Vehicles (Tesla, Rivian)
        - Smartphones (iPhone, Android)
        - Laptops and IoT devices
        - Grid-scale energy storage
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px;">
    🔋 Battery Health Truth System | Kalman Filter + Coulomb Counting | Real-time SoC Estimation
</div>
""", unsafe_allow_html=True)
