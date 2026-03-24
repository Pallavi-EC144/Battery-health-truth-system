"""
State of Charge Estimator
Combines voltage-based and coulomb-counting methods
"""

import numpy as np

class SoCEstimator:
    """
    Hybrid SoC Estimator using:
    - Voltage-based estimation (OCV curve)
    - Coulomb counting (current integration)
    - Kalman filter fusion
    """
    
    def __init__(self, nominal_capacity=3.0):
        """
        Args:
            nominal_capacity: Battery capacity in Ah
        """
        self.capacity = nominal_capacity
        self.estimated_soc = 1.0
        self.last_current = 0
        self.last_voltage = 4.2
        self.coulomb_count = 0
        
        # Discharge curve (inverse of battery model)
        self.voltage_to_soc = {
            4.2: 1.0,
            4.1: 0.9,
            4.05: 0.8,
            4.0: 0.7,
            3.95: 0.6,
            3.9: 0.5,
            3.85: 0.4,
            3.8: 0.3,
            3.7: 0.2,
            3.5: 0.1,
            3.0: 0.0
        }
        
        # Tracking
        self.history = []
        
    def estimate_from_voltage(self, voltage, current=0):
        """
        Estimate SoC from voltage with IR compensation
        """
        # Compensate for voltage sag
        ir_compensation = current * 0.05  # Assume 0.05 ohm IR
        voltage_compensated = voltage + ir_compensation
        
        # Find SoC from voltage curve
        voltages = sorted(self.voltage_to_soc.keys())
        
        if voltage_compensated >= voltages[-1]:
            return 1.0
        if voltage_compensated <= voltages[0]:
            return 0.0
        
        # Interpolate
        for i in range(len(voltages) - 1):
            if voltages[i] <= voltage_compensated <= voltages[i + 1]:
                t = (voltage_compensated - voltages[i]) / (voltages[i + 1] - voltages[i])
                soc1 = self.voltage_to_soc[voltages[i]]
                soc2 = self.voltage_to_soc[voltages[i + 1]]
                return soc1 + t * (soc2 - soc1)
        
        return 0.5
    
    def estimate_from_current(self, dt, current):
        """
        Coulomb counting estimation
        """
        delta_soc = (current * dt / 3600) / self.capacity
        self.coulomb_count -= delta_soc
        return max(0, min(1, self.coulomb_count))
    
    def estimate_hybrid(self, voltage, current, dt, kalman_filter=None):
        """
        Combine voltage and current estimates
        """
        # Get estimates
        voltage_est = self.estimate_from_voltage(voltage, current)
        current_est = self.estimate_from_current(dt, current)
        
        # Weighted average (trust current more during discharge, voltage at rest)
        current_weight = 0.7
        voltage_weight = 0.3
        
        self.estimated_soc = current_weight * current_est + voltage_weight * voltage_est
        
        # Apply Kalman filter if provided
        if kalman_filter:
            kalman_filter.predict(dt, current, self.capacity)
            self.estimated_soc = kalman_filter.update(self.estimated_soc)
        else:
            self.estimated_soc = max(0, min(1, self.estimated_soc))
        
        # Store history
        self.history.append({
            'time': len(self.history),
            'voltage_est': voltage_est,
            'current_est': current_est,
            'hybrid_est': self.estimated_soc
        })
        
        return self.estimated_soc
    
    def get_time_remaining(self, current):
        """
        Estimate remaining time at current drain
        """
        if current <= 0:
            return float('inf')
        
        remaining_ah = self.estimated_soc * self.capacity
        hours_remaining = remaining_ah / current
        minutes_remaining = hours_remaining * 60
        
        return minutes_remaining
