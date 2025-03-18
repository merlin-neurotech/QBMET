"""
This code is part of a Merlin and QBMET collaboration for the Robotic Exoskeleton Leg. 
It takes in EMG data from the delsys trigno system, calibrates it to an individual resting and max strength,
then consistently updates the stream based on the if the person's leg is flexed is not flexed. 

Developed by Merlin Neurotech Club. 
We acknowldge that the base code was written by the DISC598/599 2024/25 research team consisting of: 
Shayne, Kristen, Prisha, and Riya. 
"""
import pytrigno
import numpy as np
import time

class EMGProcessor: 
    def __init__(self, host='localhost', channel_range=(0, 15), samples_per_read=850):
        self.device = pytrigno.TrignoEMG(channel_range=channel_range, data_port=50043, 
                                       samples_per_read=samples_per_read, host=host, units='normalized')
        self.noise_levels = None
        self.max_contraction_value = None
        self.device.start()
        
    def calibrate(self, rest_time=5, mvc_time=2, pause_time=2): 
        """Calibrate EMG thresholds with rest and max voluntary contraction phases."""
        print("Calibration started. Please relax your leg for 5 seconds...")
        rest_samples = self._collect_samples(rest_time)
        rest_means = np.mean(np.abs(rest_samples), axis=1)
        self.noise_levels = np.maximum(rest_means * 1.1, 0.05)
        
        print("Prepare for Maximum Contraction!")
        time.sleep(pause_time)
        mvc_samples = self._collect_samples(mvc_time)
        self.max_contraction_value = np.mean(np.abs(mvc_samples[3]))  # Sensor 4
        print(f"Calibration complete. Noise: {self.noise_levels}, MVC: {self.max_contraction_value}")
    
    def _collect_samples(self, duration):
        """Collect EMG data for a given duration in seconds."""
        samples = []
        start_time = time.time()
        while time.time() - start_time < duration:
            data = self.device.read() * 1e6  # Convert to microvolts
            data[2] = data[4]  # Swap EMG 3 with 5
            samples.append(data)
        return np.array(samples)
    
    def detect_flexion(self, emg_data): 
        """Classify leg state based on EMG threshold."""
        return "flexed" if np.mean(emg_data) > self.max_contraction_value else "not flexed"

    def run(self):
        """Continuously read and classify EMG data."""
        while True:
            data = self.device.read() * 1e6
            data[2] = data[4]
            sensor_data = np.mean(np.abs(data[3]))  # Sensor 4
            state = self.detect_flexion(sensor_data)
            print(f"EMG: {sensor_data:.2f}, State: {state}")
            time.sleep(0.01)  # Adjust based on sampling rate
            
if __name__ == "__main__":
    processor = EMGProcessor()
    processor.calibrate()
    processor.run()
 