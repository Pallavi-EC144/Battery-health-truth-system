"""
Kalman Filter for Smooth State of Charge Estimation
Reduces noise and provides accurate predictions
"""

import numpy as np

class KalmanFilter:
    """
    1D Kalman Filter for SoC estimation
    """
    
    def __init__(self, process_noise=0.01, measurement_noise=0.05):
        """
        Args:
            process_noise: Model uncertainty (Q)
            measurement_noise: Sensor noise (R)
        """
        # State estimate
        self.x = 1.0  # Initial SoC = 100%
        
        # Error covariance
        self.P = 0.1
        
        # Process noise
        self.Q = process_noise
        
        # Measurement noise
        self.R = measurement_noise
        
    def predict(self, dt, current, capacity):
        """
        Predict next state based on Coulomb counting
        
        Args:
            dt: Time step (seconds)
            current: Current draw (Amps)
            capacity: Battery capacity (Ah)
        """
        # Coulomb counting prediction
        delta_soc = (current * dt / 3600) / capacity
        self.x -= delta_soc
        
        # Update error covariance
        self.P += self.Q
        
        # Limit SoC to [0, 1]
        self.x = max(0, min(1, self.x))
        
        return self.x
    
    def update(self, measurement):
        """
        Update estimate with new measurement
        """
        # Kalman gain
        K = self.P / (self.P + self.R)
        
        # Update estimate
        self.x = self.x + K * (measurement - self.x)
        
        # Update error covariance
        self.P = (1 - K) * self.P
        
        return self.x
    
    def get_state(self):
        """Return current SoC estimate"""
        return self.x
