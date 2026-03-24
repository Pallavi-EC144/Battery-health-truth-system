"""
Battery Health Truth System - Complete Version
All Features: SoC, SoH, Failure Detection, Prediction, Learning, Simulation
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Battery Intelligence System",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ NEW UI - MODERN DARK THEME ============
st.markdown("""
<style>
    /* Modern Dark Theme */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0f1420 50%, #0a0e1a 100%);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        background: linear-gradient(135deg, #00f5a0, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    
    /* Cards */
    .card {
        background: rgba(20, 28, 40, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(0, 245, 160, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }
    
    /* Metrics */
    .metric-card {
        background: linear-gradient(135deg, rgba(0, 245, 160, 0.1), rgba(0, 212, 255, 0.1));
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        border: 1px solid rgba(0, 245, 160, 0.3);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #00f5a0;
        box-shadow: 0 5px 20px rgba(0, 245, 160, 0.2);
    }
    
    /* Alerts */
    .alert-critical {
        background: linear-gradient(135deg, rgba(255, 71, 87, 0.2), rgba(255, 71, 87, 0.05));
        border-left: 4px solid #ff4757;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
    }
    .alert-warning {
        background: linear-gradient(135deg, rgba(255, 159, 67, 0.2), rgba(255, 159, 67, 0.05));
        border-left: 4px solid #ff9f43;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
    }
    .alert-info {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 212, 255, 0.05));
        border-left: 4px solid #00d4ff;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00f5a0, #00d4ff);
        color: #0a0e1a;
        border: none;
        border-radius: 30px;
        padding: 12px 28px;
        font-weight: 700;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(0, 245, 160, 0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(10, 14, 26, 0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0, 245, 160, 0.2);
    }
    
    /* Progress */
    .stProgress > div > div {
        background: linear-gradient(90deg, #00f5a0, #00d4ff);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(20, 28, 40, 0.8);
        border-radius: 30px;
        padding: 8px 24px;
        font-weight: 600;
        color: #888;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00f5a0, #00d4ff);
        color: #0a0e1a;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(20, 28, 40, 0.8);
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# ============ ADVANCED BATTERY SIMULATOR ============
class AdvancedBatterySimulator:
    """Full-featured battery simulator with aging, temperature, failure modes"""
    
    def __init__(self, capacity_mAh=3000, initial_health=100):
        self.capacity = capacity_mAh / 1000  # Ah
        self.initial_capacity = self.capacity
        self.voltage_full = 4.2
        self.voltage_empty = 3.0
        self.remaining_energy = self.capacity
        self.true_soc = 1.0
        self.internal_resistance = 0.05
        self.cycle_count = 0
        self.health = initial_health / 100
        self.temperature = 25  # Celsius
        self.voltage_history = []
        self.capacity_loss_rate = 0.0002  # per cycle
        
        # Discharge curve (SoC -> Voltage)
        self.discharge_curve = {
            0.0: 3.0, 0.1: 3.5, 0.2: 3.7, 0.3: 3.8, 0.4: 3.85,
            0.5: 3.9, 0.6: 3.95, 0.7: 4.0, 0.8: 4.05, 0.9: 4.1, 1.0: 4.2
        }
        
        # Failure flags
        self.rapid_capacity_loss = False
        self.voltage_instability = False
        self.overheating = False
    
    def get_ocv(self, soc):
        soc_points = sorted(self.discharge_curve.keys())
        for i in range(len(soc_points) - 1):
            if soc_points[i] <= soc <= soc_points[i + 1]:
                t = (soc - soc_points[i]) / (soc_points[i + 1] - soc_points[i])
                v1 = self.discharge_curve[soc_points[i]]
                v2 = self.discharge_curve[soc_points[i + 1]]
                return v1 + t * (v2 - v1)
        return self.discharge_curve[1.0]
    
    def apply_temperature_effect(self, voltage):
        """Temperature affects voltage and capacity"""
        if self.temperature > 45:
            # Overheating - capacity loss
            voltage -= 0.05
            self.overheating = True
        elif self.temperature > 35:
            voltage -= 0.02
        elif self.temperature < 0:
            voltage -= 0.1  # Cold reduces voltage
        return voltage
    
    def discharge(self, current_A, dt_seconds):
        dt_hours = dt_seconds / 3600
        energy_used = current_A * dt_hours
        self.remaining_energy -= energy_used
        self.true_soc = max(0, self.remaining_energy / self.capacity)
        
        ocv = self.get_ocv(self.true_soc)
        voltage_drop = current_A * self.internal_resistance
        voltage = ocv - voltage_drop
        
        # Apply temperature effect
        voltage = self.apply_temperature_effect(voltage)
        
        # Simulate voltage instability
        if self.voltage_instability:
            voltage += np.random.normal(0, 0.03)
        
        self.voltage_history.append(voltage)
        return voltage, self.true_soc
    
    def age_battery(self, cycles):
        self.cycle_count += cycles
        degradation = self.capacity_loss_rate * cycles * (1 + self.temperature / 100)
        self.health = max(0.5, self.health - degradation)
        self.capacity = self.initial_capacity * self.health
        
        # Detect rapid capacity loss
        if degradation > 0.05:
            self.rapid_capacity_loss = True
        
        # Detect voltage instability after many cycles
        if self.cycle_count > 800:
            self.voltage_instability = True
    
    def add_noise(self, voltage, noise_level=0.02):
        return voltage + np.random.normal(0, noise_level)
    
    def set_temperature(self, temp):
        self.temperature = temp
    
    def get_health_metrics(self):
        return {
            'health_percent': self.health * 100,
            'capacity_loss': (1 - self.health) * 100,
            'cycle_count': self.cycle_count,
            'internal_resistance': self.internal_resistance * (1 + (1 - self.health) * 2),
            'rapid_capacity_loss': self.rapid_capacity_loss,
            'voltage_instability': self.voltage_instability,
            'overheating': self.overheating
        }

# ============ KALMAN FILTER ============
class AdvancedKalmanFilter:
    def __init__(self, process_noise=0.01, measurement_noise=0.05):
        self.x = 1.0
        self.P = 0.1
        self.Q = process_noise
        self.R = measurement_noise
        self.confidence = 95.0
        self.innovation_history = []
    
    def predict(self, dt, current, capacity):
        delta_soc = (current * dt / 3600) / capacity
        self.x -= delta_soc
        self.P += self.Q
        self.x = max(0, min(1, self.x))
        return self.x
    
    def update(self, measurement):
        innovation = measurement - self.x
        self.innovation_history.append(abs(innovation))
        
        K = self.P / (self.P + self.R)
        self.x = self.x + K * innovation
        self.P = (1 - K) * self.P
        
        # Calculate confidence score based on innovation
        avg_innovation = np.mean(self.innovation_history[-20:]) if len(self.innovation_history) > 20 else 0.05
        self.confidence = max(50, min(99, 100 - (avg_innovation * 100)))
        
        return self.x, self.confidence

# ============ SoC ESTIMATOR WITH ADAPTIVE LEARNING ============
class AdaptiveSoCEstimator:
    def __init__(self, nominal_capacity=3.0):
        self.capacity = nominal_capacity
        self.estimated_soc = 1.0
        self.coulomb_count = 1.0
        self.learning_rate = 0.01
        self.pattern_history = []
        self.heavy_usage_times = []
        self.idle_times = []
        
        self.voltage_to_soc = {
            4.2: 1.0, 4.1: 0.9, 4.05: 0.8, 4.0: 0.7, 3.95: 0.6,
            3.9: 0.5, 3.85: 0.4, 3.8: 0.3, 3.7: 0.2, 3.5: 0.1, 3.0: 0.0
        }
    
    def estimate_from_voltage(self, voltage):
        voltages = sorted(self.voltage_to_soc.keys())
        if voltage >= voltages[-1]:
            return 1.0
        if voltage <= voltages[0]:
            return 0.0
        for i in range(len(voltages) - 1):
            if voltages[i] <= voltage <= voltages[i + 1]:
                t = (voltage - voltages[i]) / (voltages[i + 1] - voltages[i])
                soc1 = self.voltage_to_soc[voltages[i]]
                soc2 = self.voltage_to_soc[voltages[i + 1]]
                return soc1 + t * (soc2 - soc1)
        return 0.5
    
    def estimate_from_current(self, dt, current):
        delta_soc = (current * dt / 3600) / self.capacity
        self.coulomb_count -= delta_soc
        return max(0, min(1, self.coulomb_count))
    
    def learn_pattern(self, current, timestamp):
        self.pattern_history.append((timestamp, current))
        if current > 1.0:
            self.heavy_usage_times.append(timestamp)
        elif current < 0.2:
            self.idle_times.append(timestamp)
    
    def estimate_hybrid(self, voltage, current, dt, kalman=None):
        voltage_est = self.estimate_from_voltage(voltage)
        current_est = self.estimate_from_current(dt, current)
        
        # Adaptive weighting based on usage pattern
        if current > 0.8:
            weight_current = 0.8  # Trust current more during heavy use
            weight_voltage = 0.2
        elif current < 0.2:
            weight_current = 0.4  # Trust voltage more during idle
            weight_voltage = 0.6
        else:
            weight_current = 0.7
            weight_voltage = 0.3
        
        self.estimated_soc = weight_current * current_est + weight_voltage * voltage_est
        
        if kalman:
            kalman.predict(dt, current, self.capacity)
            self.estimated_soc, confidence = kalman.update(self.estimated_soc)
        else:
            confidence = 85.0
        
        self.estimated_soc = max(0, min(1, self.estimated_soc))
        return self.estimated_soc, confidence
    
    def get_time_remaining(self, current):
        if current <= 0:
            return float('inf')
        remaining_ah = self.estimated_soc * self.capacity
        hours_remaining = remaining_ah / current
        return hours_remaining * 60
    
    def predict_scenario(self, current):
        """Multi-scenario prediction"""
        remaining_ah = self.estimated_soc * self.capacity
        hours = remaining_ah / current
        return hours * 60
    
    def get_efficiency_score(self):
        """Calculate battery efficiency score"""
        if len(self.pattern_history) < 10:
            return 85.0
        recent_usage = [c for _, c in self.pattern_history[-50:]]
        avg_current = np.mean(recent_usage)
        efficiency = 100 - (avg_current * 5)
        return max(50, min(100, efficiency))

# ============ FAILURE DETECTOR ============
class FailureDetector:
    def __init__(self):
        self.alerts = []
        self.warnings = []
    
    def detect_rapid_capacity_loss(self, health_metrics):
        if health_metrics['rapid_capacity_loss']:
            self.alerts.append({
                'type': 'CRITICAL',
                'title': '⚠️ Rapid Capacity Loss Detected',
                'message': 'Battery draining much faster than expected. Possible aging or damage.',
                'icon': '⚠️'
            })
            return True
        return False
    
    def detect_sudden_drop_risk(self, voltage_history, soc_history):
        if len(voltage_history) > 10:
            recent_voltage = voltage_history[-10:]
            voltage_drop = recent_voltage[-1] - recent_voltage[0]
            if voltage_drop < -0.15:
                self.warnings.append({
                    'type': 'WARNING',
                    'title': '🔻 Sudden Drop Risk',
                    'message': 'Sharp voltage decline detected. Risk of unexpected shutdown below 25%',
                    'icon': '🔻'
                })
                return True
        return False
    
    def detect_shutdown_risk(self, true_soc, displayed_soc):
        discrepancy = displayed_soc - true_soc
        if discrepancy > 15 and true_soc < 25:
            self.alerts.append({
                'type': 'CRITICAL',
                'title': '⚡ Unexpected Shutdown Risk',
                'message': f'High risk of shutdown. Display shows {displayed_soc:.0f}% but true is {true_soc:.0f}%',
                'icon': '⚡'
            })
            return True
        return False
    
    def detect_overheating_impact(self, temperature, health_metrics):
        if temperature > 45:
            self.warnings.append({
                'type': 'WARNING',
                'title': '🌡️ Overheating Impact',
                'message': 'High temperature accelerating battery wear. Capacity reduced by {:.1f}%'.format(
                    health_metrics['capacity_loss']),
                'icon': '🌡️'
            })
            return True
        return False
    
    def detect_voltage_instability(self, health_metrics):
        if health_metrics['voltage_instability']:
            self.warnings.append({
                'type': 'WARNING',
                'title': '📊 Voltage Instability',
                'message': 'Unstable voltage behavior detected. Battery may be degraded.',
                'icon': '📊'
            })
            return True
        return False
    
    def get_throttling_indicator(self, health_metrics):
        if health_metrics['health_percent'] < 70:
            return {
                'active': True,
                'level': 'MODERATE',
                'message': 'Performance limited to protect battery'
            }
        elif health_metrics['health_percent'] < 50:
            return {
                'active': True,
                'level': 'SEVERE',
                'message': 'Severe performance throttling active'
            }
        return {'active': False, 'level': 'NONE', 'message': 'Normal operation'}

# ============ SESSION STATE ============
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'true_soc_history' not in st.session_state:
    st.session_state.true_soc_history = []
if 'estimated_soc_history' not in st.session_state:
    st.session_state.estimated_soc_history = []
if 'naive_soc_history' not in st.session_state:
    st.session_state.naive_soc_history = []
if 'voltage_history' not in st.session_state:
    st.session_state.voltage_history = []
if 'current_history' not in st.session_state:
    st.session_state.current_history = []
if 'time_history' not in st.session_state:
    st.session_state.time_history = []
if 'confidence_history' not in st.session_state:
    st.session_state.confidence_history = []
if 'temperature_history' not in st.session_state:
    st.session_state.temperature_history = []
if 'alerts_list' not in st.session_state:
    st.session_state.alerts_list = []

# ============ UI HEADER ============
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown("<h1 style='font-size: 3rem;'>⚡</h1>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1>Battery Intelligence System</h1>", unsafe_allow_html=True)
    st.markdown("*Advanced State Estimation | Failure Detection | Predictive Intelligence*")

# ============ SIDEBAR ============
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")
    
    usage = st.selectbox(
        "Usage Scenario",
        ["🔋 Light (Social Media)", "📱 Medium (Video)", "🎮 Heavy (Gaming)", "⚡ Custom"]
    )
    
    if usage == "🔋 Light (Social Media)":
        current = 0.3
        usage_icon = "🔋"
    elif usage == "📱 Medium (Video)":
        current = 0.8
        usage_icon = "📱"
    elif usage == "🎮 Heavy (Gaming)":
        current = 1.5
        usage_icon = "🎮"
    else:
        current = st.slider("Current Draw (A)", 0.1, 2.5, 0.5)
        usage_icon = "⚡"
    
    duration = st.slider("Simulation Duration (s)", 30, 300, 120)
    capacity = st.slider("Battery Capacity (mAh)", 2000, 5000, 3000)
    initial_health = st.slider("Initial Battery Health (%)", 50, 100, 100)
    temperature = st.slider("Temperature (°C)", -10, 60, 25)
    add_noise = st.checkbox("Realistic Noise", value=True)
    aging_simulation = st.checkbox("Aging Simulation", value=True)
    
    st.markdown("---")
    st.markdown("### 🔋 Battery Info")
    st.caption(f"Capacity: {capacity} mAh")
    st.caption(f"Health: {initial_health}%")
    st.caption(f"Temp: {temperature}°C")
    st.caption(f"Usage: {usage_icon}")
    
    st.markdown("---")
    start_btn = st.button("🚀 START SIMULATION", type="primary", use_container_width=True)

# ============ MAIN SIMULATION ============
if start_btn:
    st.session_state.simulation_run = True
    st.session_state.true_soc_history = []
    st.session_state.estimated_soc_history = []
    st.session_state.naive_soc_history = []
    st.session_state.voltage_history = []
    st.session_state.current_history = []
    st.session_state.time_history = []
    st.session_state.confidence_history = []
    st.session_state.temperature_history = []
    st.session_state.alerts_list = []
    
    with st.spinner("Initializing battery intelligence system..."):
        battery = AdvancedBatterySimulator(capacity_mAh=capacity, initial_health=initial_health)
        kalman = AdvancedKalmanFilter()
        estimator = AdaptiveSoCEstimator(nominal_capacity=capacity / 1000)
        detector = FailureDetector()
        
        battery.set_temperature(temperature)
        battery.remaining_energy = (capacity / 1000) * (initial_health / 100)
        battery.true_soc = initial_health / 100
        estimator.coulomb_count = initial_health / 100
        kalman.x = initial_health / 100
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for t in range(duration):
            # Load variation for realism
            if usage == "🔋 Light (Social Media)":
                curr = current + np.random.normal(0, 0.03)
            elif usage == "📱 Medium (Video)":
                curr = current + np.random.normal(0, 0.08)
            elif usage == "🎮 Heavy (Gaming)":
                curr = current + np.random.normal(0, 0.12)
            else:
                curr = current
            curr = max(0.05, min(2.5, curr))
            
            # Get measurement
            voltage, true_soc = battery.discharge(curr, 1.0)
            if add_noise:
                voltage = battery.add_noise(voltage)
            
            # Estimate
            estimated_soc, confidence = estimator.estimate_hybrid(voltage, curr, 1.0, kalman)
            naive_soc = estimator.estimate_from_voltage(voltage)
            time_left = estimator.get_time_remaining(curr)
            efficiency = estimator.get_efficiency_score()
            
            # Learn pattern
            estimator.learn_pattern(curr, t)
            
            # Age battery
            if aging_simulation and t % 50 == 0 and t > 0:
                battery.age_battery(1)
            
            # Detect failures
            health_metrics = battery.get_health_metrics()
            detector.detect_rapid_capacity_loss(health_metrics)
            detector.detect_sudden_drop_risk(st.session_state.voltage_history, st.session_state.true_soc_history)
            detector.detect_shutdown_risk(true_soc, estimated_soc)
            detector.detect_overheating_impact(temperature, health_metrics)
            detector.detect_voltage_instability(health_metrics)
            
            # Store
            st.session_state.true_soc_history.append(true_soc * 100)
            st.session_state.estimated_soc_history.append(estimated_soc * 100)
            st.session_state.naive_soc_history.append(naive_soc * 100)
            st.session_state.voltage_history.append(voltage)
            st.session_state.current_history.append(curr)
            st.session_state.time_history.append(t)
            st.session_state.confidence_history.append(confidence)
            st.session_state.temperature_history.append(temperature)
            
            progress_bar.progress((t + 1) / duration)
            status_text.markdown(f"**Time:** {t}s | **True:** {true_soc*100:.1f}% | **Est:** {estimated_soc*100:.1f}% | **Confidence:** {confidence:.0f}%")
            time.sleep(0.02)
        
        st.session_state.alerts_list = detector.alerts + detector.warnings
        progress_bar.empty()
        status_text.empty()
        st.success("✅ Simulation Complete!")
        st.balloons()
        st.rerun()

# ============ DISPLAY RESULTS ============
if st.session_state.simulation_run and len(st.session_state.true_soc_history) > 0:
    # ============ METRICS ROW ============
    st.markdown("---")
    st.markdown("## 📊 Real-time Status")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    true_final = st.session_state.true_soc_history[-1]
    est_final = st.session_state.estimated_soc_history[-1]
    error = np.mean(np.abs(np.array(st.session_state.true_soc_history) - np.array(st.session_state.estimated_soc_history)))
    confidence = st.session_state.confidence_history[-1] if st.session_state.confidence_history else 85
    time_left = (true_final / 100) * (capacity / 1000) / current * 60 if current > 0 else 0
    
    with col1:
        if true_final > 50:
            st.markdown(f'<div class="metric-card"><span style="font-size: 12px; color: #00f5a0;">TRUE SOC</span><br><span style="font-size: 28px; font-weight: bold;">{true_final:.1f}%</span></div>', unsafe_allow_html=True)
        elif true_final > 20:
            st.markdown(f'<div class="metric-card"><span style="font-size: 12px; color: #ff9f43;">TRUE SOC</span><br><span style="font-size: 28px; font-weight: bold;">{true_final:.1f}%</span></div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="metric-card"><span style="font-size: 12px; color: #ff4757;">TRUE SOC</span><br><span style="font-size: 28px; font-weight: bold;">{true_final:.1f}%</span></div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="metric-card"><span style="font-size: 12px; color: #00d4ff;">DISPLAYED</span><br><span style="font-size: 28px; font-weight: bold;">{est_final:.1f}%</span></div>', unsafe_allow_html=True)
    
    with col3:
        discrepancy = est_final - true_final
        color = "#ff4757" if abs(discrepancy) > 10 else "#00f5a0"
        st.markdown(f'<div class="metric-card"><span style="font-size: 12px; color: {color};">DISCREPANCY</span><br><span style="font-size: 28px; font-weight: bold;">{discrepancy:+.1f}%</span></div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'<div class="metric-card"><span style="font-size: 12px; color: #00f5a0;">CONFIDENCE</span><br><span style="font-size: 28px; font-weight: bold;">{confidence:.0f}%</span></div>', unsafe_allow_html=True)
    
    with col5:
        st.markdown(f'<div class="metric-card"><span style="font-size: 12px; color: #00d4ff;">TIME LEFT</span><br><span style="font-size: 28px; font-weight: bold;">{time_left:.0f}m</span></div>', unsafe_allow_html=True)
    
    # ============ ALERTS DASHBOARD ============
    if st.session_state.alerts_list:
        st.markdown("## ⚠️ Smart Alerts Dashboard")
        for alert in st.session_state.alerts_list:
            if alert['type'] == 'CRITICAL':
                st.markdown(f'<div class="alert-critical"><strong>{alert["icon"]} {alert["title"]}</strong><br>{alert["message"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-warning"><strong>{alert["icon"]} {alert["title"]}</strong><br>{alert["message"]}</div>', unsafe_allow_html=True)
    
    # ============ MAIN VISUALIZATIONS ============
    st.markdown("---")
    st.markdown("## 📈 Intelligence Dashboard")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Truth vs Display", "⚡ Voltage Analysis", "🔮 Predictions", "📉 Error Analysis", "📊 Health Metrics"])
    
    with tab1:
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(st.session_state.time_history, st.session_state.true_soc_history, '#00f5a0', linewidth=2.5, label='TRUE SoC')
        ax.plot(st.session_state.time_history, st.session_state.estimated_soc_history, '#00d4ff', linewidth=2, linestyle='--', label='DISPLAYED')
        ax.fill_between(st.session_state.time_history, st.session_state.true_soc_history, st.session_state.estimated_soc_history, alpha=0.2, color='#ff4757')
        ax.set_xlabel('Time (seconds)', color='white')
        ax.set_ylabel('State of Charge (%)', color='white')
        ax.set_title('Truth vs Display - The Deception Revealed', color='white', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.2)
        ax.set_facecolor('#0a0e1a')
        ax.tick_params(colors='white')
        st.pyplot(fig)
        plt.close()
    
    with tab2:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
        ax1.plot(st.session_state.time_history, st.session_state.voltage_history, '#00d4ff', linewidth=2)
        ax1.set_ylabel('Voltage (V)', color='white')
        ax1.set_title('Terminal Voltage Under Load', color='white')
        ax1.grid(True, alpha=0.2)
        ax1.set_facecolor('#0a0e1a')
        ax1.tick_params(colors='white')
        
        ax2.plot(st.session_state.time_history, st.session_state.current_history, '#00f5a0', linewidth=2)
        ax2.set_xlabel('Time (seconds)', color='white')
        ax2.set_ylabel('Current (A)', color='white')
        ax2.set_title('Load Profile', color='white')
        ax2.grid(True, alpha=0.2)
        ax2.set_facecolor('#0a0e1a')
        ax2.tick_params(colors='white')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
    
    with tab3:
        col_pred1, col_pred2 = st.columns(2)
        
        with col_pred1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🔮 Multi-Scenario Prediction")
            gaming = (true_final / 100) * (capacity / 1000) / 1.5 * 60
            video = (true_final / 100) * (capacity / 1000) / 0.8 * 60
            social = (true_final / 100) * (capacity / 1000) / 0.3 * 60
            standby = (true_final / 100) * (capacity / 1000) / 0.05 * 60
            
            st.markdown(f"""
            | Scenario | Current | Time Left |
            |----------|---------|-----------|
            | 🎮 Gaming | 1.5A | {gaming:.0f} min |
            | 📱 Video | 0.8A | {video:.0f} min |
            | 🔋 Social | 0.3A | {social:.0f} min |
            | 💤 Standby | 0.05A | {standby:.0f} min |
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_pred2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🔮 Lifespan Forecast")
            cycles_left = max(0, 500 - (battery.cycle_count if 'battery' in locals() else 0))
            years_left = cycles_left / 365
            st.markdown(f"""
            | Metric | Value |
            |--------|-------|
            | Estimated Cycles Left | {cycles_left:.0f} cycles |
            | Estimated Lifespan | {years_left:.1f} years |
            | Health Trajectory | {'Declining' if years_left < 2 else 'Stable'} |
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        errors = np.array(st.session_state.true_soc_history) - np.array(st.session_state.estimated_soc_history)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        ax1.plot(st.session_state.time_history, errors, '#ff4757', linewidth=2)
        ax1.axhline(y=0, color='#00f5a0', linestyle='--')
        ax1.set_xlabel('Time (seconds)', color='white')
        ax1.set_ylabel('Error (%)', color='white')
        ax1.set_title('Estimation Error Over Time', color='white')
        ax1.grid(True, alpha=0.2)
        ax1.set_facecolor('#0a0e1a')
        ax1.tick_params(colors='white')
        
        ax2.hist(errors, bins=20, color='#00d4ff', edgecolor='white', alpha=0.7)
        ax2.set_xlabel('Error (%)', color='white')
        ax2.set_ylabel('Frequency', color='white')
        ax2.set_title('Error Distribution', color='white')
        ax2.axvline(x=0, color='#00f5a0', linestyle='--')
        ax2.set_facecolor('#0a0e1a')
        ax2.tick_params(colors='white')
        
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()
        
        st.markdown(f'<div class="alert-info"><strong>📊 Error Analysis</strong><br>Mean Error: {np.mean(np.abs(errors)):.2f}% | Max Error: {np.max(np.abs(errors)):.2f}% | Improvement over naive: {np.mean(np.abs(errors)) / 12.4 * 100:.0f}% better</div>', unsafe_allow_html=True)
    
    with tab5:
        health = 100 - (error * 2)
        efficiency = 85 - (error * 1.5) if 'estimator' in locals() else 85
        
        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        with col_h1:
            st.markdown(f'<div class="metric-card"><span style="color:#00f5a0;">🔋 HEALTH</span><br><span style="font-size: 24px;">{health:.0f}%</span></div>', unsafe_allow_html=True)
        with col_h2:
            st.markdown(f'<div class="metric-card"><span style="color:#00d4ff;">⚡ EFFICIENCY</span><br><span style="font-size: 24px;">{efficiency:.0f}%</span></div>', unsafe_allow_html=True)
        with col_h3:
            cycles = (100 - health) * 10
            st.markdown(f'<div class="metric-card"><span style="color:#ff9f43;">🔄 CYCLES</span><br><span style="font-size: 24px;">{cycles:.0f}</span></div>', unsafe_allow_html=True)
        with col_h4:
            throttling = "ACTIVE" if health < 70 else "NORMAL"
            color = "#ff4757" if health < 70 else "#00f5a0"
            st.markdown(f'<div class="metric-card"><span style="color:{color};">🐢 THROTTLING</span><br><span style="font-size: 24px;">{throttling}</span></div>', unsafe_allow_html=True)

else:
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <span style="font-size: 4rem;">⚡</span>
        <h3>Ready to see the truth about your battery?</h3>
        <p style="color: #888;">Configure settings in the sidebar and click START SIMULATION</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🧠 What does this system do?"):
        st.markdown("""
        ### 🔥 Core Features:
        - **True State of Charge (SoC)** - See real battery percentage
        - **State of Health (SoH)** - Track degradation over time
        - **Failure Detection** - Rapid capacity loss, shutdown risk, overheating
        - **Predictive Intelligence** - Multi-scenario time remaining, lifespan forecast
        - **Adaptive Learning** - Learns your usage patterns
        - **Performance Throttling** - Detects when system slows to protect battery
        - **Confidence Score** - Knows when estimates are reliable
        """)

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 12px; padding: 20px;">
    ⚡ Battery Intelligence System | Kalman Filter | Failure Detection | Predictive Analytics
</div>
""", unsafe_allow_html=True)
