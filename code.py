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


# Configuration for the Trigno EMG device
host = 'localhost'  # Replace with your host IP
dev = pytrigno.TrignoEMG(channel_range=(0, 15), data_port=50043, samples_per_read=850, host=host, units='normalized')
print("Print Dev ", dev, "\n")

# Start the device
dev.start()

# Calibration settings
rest_calibration_time = 5  # Calibration time at rest in seconds
mvc_calibration_time = 2    # Calibration time during MVC in seconds
pause_time = 2               # Pause time in seconds
noise_levels = None  # To be set after calibration
max_contraction_value = None   # Max contraction value for thresholds
calibration_complete = False


# Function to show calibration messages
def show_message(message):
    print("Calibration Instruction", message)

# Calibration procedure
def calibrate():
    """Calibrate EMG thresholds with rest and max voluntary contraction phases."""
    global noise_levels, max_contraction_value, calibration_complete
    # Show pop-up message for relaxation phase
    show_message("Calibration started. Please relax your leg for 5 seconds...")
    # Phase 1: Collect samples at rest
    rest_samples = [[] for _ in range(4)]
    start_time = time.time()
    while time.time() - start_time < rest_calibration_time:
        data = dev.read() * 1e6  # Convert volts to microvolts
        data[2] = data[4]  # swapping to emg 5 because emg 3 doesn't seem to work well
        for i in range(4):
            rest_samples[i].append(np.mean(np.abs(data[i])))

    rest_means = [np.mean(samples) for samples in rest_samples]
    print(f"Rest calibration complete. Resting means: {rest_means}")

    # Set noise thresholds dynamically based on resting means
    noise_levels = [max(mean * 1.1, 0.05) for mean in rest_means]
    print(f"Dynamic noise thresholds set: {noise_levels}")

    # Phase 2: Calibration for MVC (Max Voluntary Contraction)
    max_contraction_value = None
    mvc_samples = []
    print("Starting MVC calibration...")
    
    show_message("Prepare for Maximum Contraction!")
    time.sleep(pause_time)  # Pause for a brief time
    mvc_samples = []
    start_time = time.time()
    while time.time() - start_time < mvc_calibration_time:
        data = dev.read() * 1e6  # Read data and convert to microvolts
        data[2] = data[4]
        if data.shape[0] > 0:
            mvc_samples.append(np.mean(np.abs(data[3])))
    max_contraction_value = np.mean(mvc_samples)
    print(f"Max MVC for sensor 4: {max_contraction_value}")

    calibration_complete = True

# Function to detect flexion based on threshold
def detect_flexion(emg_data):
    """Classify leg state based on EMG threshold."""
    if np.mean(emg_data) > max_contraction_value:
        return "flexed"
    else:
        return "not flexed"

# Function to read EMG data and classify it as flexed or not flexed
def read_emg():
    data = dev.read() * 1e6  # Read in latest data and Convert raw data from V to µV  
    data[2] = data[4]  # swapping to emg 5 because emg 3 doesn't seem to work well
    if data.shape[1] > 0:
        sensor_data = [np.mean(np.abs(data[3]))]  # Get mean for sensor 4
        print(f"EMG Data: {sensor_data}")
        
        # Classify flexion state
        flexion_state = detect_flexion(sensor_data)
        print(f"Flexion State: {flexion_state}")
        
        
# Start the calibration
calibrate()

# Continuously read EMG data and classify it
while True: 
    read_emg()
    time.sleep(0.001) # adjust this delay as needed 