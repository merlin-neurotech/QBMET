import neurol
from neurol import streams
from pylsl import StreamInlet, resolve_stream
import numpy as np
from pylsl import StreamInlet, resolve_stream
from scipy.signal import butter, filtfilt

import csv
import time

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="high", analog=False)
    return b, a

def highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def getEEGValues():
    streams1 = resolve_stream("name='Unicorn'")
    inlet = StreamInlet(streams1[0])
    stream = streams.lsl_stream(inlet,buffer_length=1024)

    if not stream:
        print("There is no values being read through the EEG Stream!")
        return -1

    # Data is returned in the format:
    # [EEG1, EEG2, ..., EEG8, Accel X, Accel Y, Accel Z, Gyro X, Gyro Y, Battery %, Counter, Indicator (On/Off, always 1)
    #This sample[0] means that we are pulling only the data from the first node
    data = []
    for _ in range(20):
        sample, timestamp = inlet.pull_sample()
        ext_sample = sample[0]
        #print(timestamp, sample)
        data.append(sample[0])

    #print(data)
    filtered_data = highpass_filter(data, cutoff=60, fs=250)
    #print(filtered_data)
    return (sum(filtered_data) / len(filtered_data))

def EEGThreshold(threshold):
    EEG_val = getEEGValues()
    print(EEG_val)
    if (EEG_val > threshold):
        print("Greater than the threshold!")
        return 1
    else:
        print("Less than the threshold!")
        return 0
#change


def average_and_output_csv():
    # Open CSV file for writing
    with open('averaged_eeg_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header row
        writer.writerow(['EEG1', 'EEG2', 'EEG3', 'EEG4', 'EEG5', 'EEG6', 'EEG7', 'EEG8',
                         'Accel X', 'Accel Y', 'Accel Z', 'Gyro X', 'Gyro Y',
                         'Battery %', 'Counter', 'Indicator'])

        # Record start time
        start_time = time.time()

        while time.time() - start_time < 10:
            # Get EEG data
            eeg_data = getEEGValues()

            # Separate data into EEG and sensor data
            eeg_values = eeg_data[:8]
            sensor_data = eeg_data[8:11]
            gyro_data = eeg_data[11:13]
            battery_percentage = eeg_data[13]
            counter = eeg_data[14]
            indicator = eeg_data[15]

            # Average sensor data
            averaged_sensor_data = [sum(sensor_data) / len(sensor_data) for _ in range(len(sensor_data))]

            # Write averaged data to CSV file
            writer.writerow(eeg_values + averaged_sensor_data + gyro_data + [battery_percentage, counter, indicator])

            # Wait for a short time before next iteration
            time.sleep(0.1)  # Adjust as needed


print("In main")
EEGThreshold(0.1)
