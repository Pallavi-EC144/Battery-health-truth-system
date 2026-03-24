"""
Battery Simulator - Models real battery behavior
Generates voltage, current, and capacity data
"""

import numpy as np

class BatterySimulator:
    """
    Simulates a real battery with:
    - Non-linear discharge curve
    - Load-dependent voltage sag
    - Battery degradation over cycles
    - Measurement noise
    """
    
    def __init__(self, capacity_mAh=3000, nominal_voltage=3.7):
        """
        Args:
            capacity_mAh: Battery capacity in milliamp-hours
            nominal_voltage: Nominal voltage in volts
        """
        self.capacity = capacity_mAh / 1000  # Convert to Ah
        self.nominal_voltage = nominal_voltage
        self.voltage_full = 4.2
        self.voltage_empty = 3.0
        
        # True state of charge (hidden from estimator)
        self.true_soc = 1.0  # 100% charged
        self.remaining_energy = self.capacity  # Ah
        
        # Battery health
        self.cycle_count = 0
        self.state_of_health = 1.0  # 100% health
        self.internal_resistance = 0.05  # Ohms
        
        # Discharge curve (SoC -> Open Circuit Voltage)
        self.discharge_curve = {
            0.0: 3.0,   # 0% - Empty
            0.1: 3.5,
            0.2: 3.7,
            0.3: 3.8,
            0.4: 3.85,
            0.5: 3.9,
            0.6: 3.95,
            0.7: 4.0,
            0.8: 4.05,
            0.9: 4.1,
            1.0: 4.2    # 100% - Full
        }
        
    def get_ocv(self, soc):
        """
        Get Open Circuit Voltage from State of Charge
        Uses non-linear discharge curve
        """
        soc_points = sorted(self.discharge_curve.keys())
        
        # Find nearest points
        for i in range(len(soc_points) - 1):
            if soc_points[i] <= soc <= soc_points[i + 1]:
                t = (soc - soc_points[i]) / (soc_points[i + 1] - soc_points[i])
                v1 = self.discharge_curve[soc_points[i]]
                v2 = self.discharge_curve[soc_points[i + 1]]
                return v1 + t * (v2 - v1)
        
        return self.discharge_curve[soc_points[-1]] if soc > 0.5 else self.discharge_curve[soc_points[0]]
    
    def discharge(self, current_A, dt_seconds):
        """
        Discharge battery for time dt at current current_A
        
        Returns:
            voltage: Terminal voltage (with IR drop)
            soc: New state of charge
        """
        # Convert to hours
        dt_hours = dt_seconds / 3600
        
        # Energy consumed
        energy_used = current_A * dt_hours
        
        # Update remaining energy
        self.remaining_energy -= energy_used
        self.true_soc = max(0, self.remaining_energy / self.capacity)
        
        # Get open circuit voltage
        ocv = self.get_ocv(self.true_soc)
        
        # Voltage sag due to internal resistance (IR drop)
        voltage_drop = current_A * self.internal_resistance
        
        # Terminal voltage
        voltage = ocv - voltage_drop
        
        return voltage, self.true_soc
    
    def add_noise(self, voltage, noise_level=0.02):
        """
        Add realistic measurement noise
        """
        noise = np.random.normal(0, noise_level)
        return voltage + noise
    
    def add_voltage_sag(self, voltage, current):
        """
        Add extra voltage sag for high current loads
        """
        sag = current * 0.02  # Extra sag coefficient
        return voltage - sag
    
    def age_battery(self, cycles):
        """
        Simulate battery aging
        """
        self.cycle_count += cycles
        # 20% capacity loss after 500 cycles
        degradation = min(0.2, self.cycle_count / 2500)
        self.state_of_health = 1 - degradation
        self.capacity = self.capacity * (1 - degradation)
        self.internal_resistance = 0.05 * (1 + degradation * 3)
    
    def get_measurement(self, dt=1.0, current=0.5, add_noise=True):
        """
        Get a single battery measurement
        """
        voltage, soc = self.discharge(current, dt)
        
        if add_noise:
            voltage = self.add_noise(voltage)
            
            # Add sudden drops for realism
            if np.random.random() < 0.01:  # 1% chance
                voltage -= np.random.uniform(0.05, 0.15)
        
        return {
            'voltage': voltage,
            'current': current,
            'true_soc': soc,
            'timestamp': dt,
            'health': self.state_of_health
        }
