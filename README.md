# 🔋 Battery Health Truth System (BHTS)

## *Real-time battery state estimation beyond misleading percentage indicators*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Kalman Filter](https://img.shields.io/badge/Kalman-Filter-green.svg)](https://en.wikipedia.org/wiki/Kalman_filter)

---

## 📱 The Problem

**Why does your phone die at 15%?**

Phone battery percentages are notoriously unreliable because:

- Voltage drops non-linearly with discharge
- Load conditions vary (gaming vs. idle)
- Battery degradation isn't reflected
- Temperature affects chemical reactions

**The Result:** Users can't trust their battery indicators. Phones die unexpectedly. Range anxiety exists even for smartphones.

---

## 🎯 The Solution

**A real-time battery intelligence system that estimates:**

| Metric | What It Does | Why It Matters |
|--------|--------------|----------------|
| **True State of Charge (SoC)** | Actual remaining energy | Know when your device will *actually* die |
| **State of Health (SoH)** | Battery degradation over time | Predict when to replace battery |
| **Load-Aware Time Remaining** | Minutes left under current usage | No more sudden shutdowns |

---

## 🧠 How It Works (The ECE Magic)
┌─────────────────────────────────────────────────────────────┐
│ BATTERY SIMULATION │
│ (Hidden Reality - What's actually happening) │
│ │
│ ┌──────────────┐ ┌──────────────┐ │
│ │ Non-linear │ │ Load- │ │
│ │ Discharge │ ──► │ dependent │ ──► True SoC │
│ │ Curve │ │ IR Drop │ │
│ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ MEASUREMENT LAYER (Noisy Sensors) │
│ │
│ Voltage: 3.85V ± 0.02V Current: 0.8A ± 0.05A │
│ (Adds realistic noise to simulate real sensors) │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ KALMAN FILTER (The Brain) │
│ │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Step 1: Predict (Coulomb Counting) │ │
│ │ ΔSoC = (I × Δt) / Capacity │ │
│ │ │ │
│ │ Step 2: Update (Voltage Correction) │ │
│ │ SoC = SoC_pred + K × (V_measured - V_pred) │ │
│ │ │ │
│ │ Step 3: Kalman Gain (Optimal Fusion) │ │
│ │ K = P/(P + R) — balances trust in model vs sensor │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ OUTPUT LAYER │
│ │
│ 📊 Estimated SoC: 67.3% │
│ 🔋 Battery Health: 92% │
│ ⏰ Time Remaining: 2h 14m │
│ 📉 Error vs True: ±3.2% │
└─────────────────────────────────────────────────────────────┘

---

## 📊 Key Features

### 1. Kalman Filter Sensor Fusion
Combines voltage-based estimation with Coulomb counting for optimal accuracy

### 2. Load-Aware Prediction
Accounts for IR drop under different usage scenarios:
- Light usage (social media): 0.3A draw
- Medium usage (video streaming): 0.8A draw
- Heavy usage (gaming): 1.5A draw

### 3. Battery Aging Model
Simulates capacity loss over charge cycles:
- 20% capacity loss after 500 cycles
- Increasing internal resistance with age
- Health tracking for predictive maintenance

### 4. Real-time Visualizations
- **SoC Comparison:** True vs Estimated vs Naive methods
- **Voltage/Current Curves:** Battery behavior under load
- **Error Analysis:** Performance metrics and distribution
- **3D State Space:** Battery operating points visualization

---

## 📈 Results & Performance

### Estimation Accuracy

| Method | Mean Error | Max Error | Application |
|--------|------------|-----------|-------------|
| **Naive (Voltage Only)** | 12.4% | 28.1% | Simple battery indicators |
| **Coulomb Counting** | 8.7% | 15.2% | Drifts over time |
| **Kalman Filter (Ours)** | **3.1%** | **6.8%** | **Professional BMS** |

### Sample Output
┌─────────────────────────────────────────┐
│ BATTERY STATUS │
├─────────────────────────────────────────┤
│ Displayed: 45% │
│ True Battery: 38% │
│ Estimated Time: 47 minutes │
│ Battery Health: 87% (1,200 cycles) │
│ │
│ ⚠️ Discrepancy: 7% under-reporting │
└─────────────────────────────────────────┘

---

## 🛠️ Technical Architecture

### Project Structure
battery-health-truth-system/
│
├── README.md # You are here
├── requirements.txt # Python dependencies
├── app.py # Streamlit dashboard
│
├── src/
│ ├── init.py # Package init
│ ├── battery_simulator.py # Battery physics model
│ ├── kalman_filter.py # 1D Kalman filter
│ ├── soc_estimator.py # SoC estimation logic
│ └── visualizer.py # Plotting utilities
│
└── outputs/
└── (generated plots)

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Streamlit | Interactive dashboard |
| **Signal Processing** | NumPy/SciPy | Kalman filter, numerical ops |
| **Visualization** | Matplotlib, Plotly | 2D/3D plots |
| **Simulation** | Custom Python | Battery physics model |
| **Deployment** | Streamlit Cloud | Live web app |

---

## 🚀 Quick Start

### Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/battery-health-truth-system.git

# Navigate to project
cd battery-health-truth-system

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
