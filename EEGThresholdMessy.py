from neurol import streams
from pylsl import StreamInlet, resolve_stream
import numpy as np
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
    stream = streams.lsl_stream(inlet, buffer_length=1)

    if not stream:
        print("There are no values being read through the EEG Stream!")
        return -1
        
    # This sample[0] means that we are pulling only the data from the first node
    raw_data = []
    for _ in range(20):
        sample, timestamp = inlet.pull_sample()
        ext_sample = sample[0]
        print(timestamp, sample)
        raw_data.append(sample[0])

    filtered_data = highpass_filter(raw_data, cutoff=60, fs=250)
    return raw_data, filtered_data




def getEEGValuesInCSV(num_data_points):
    streams1 = resolve_stream("name='Unicorn'")
    inlet = StreamInlet(streams1[0])
    stream = streams.lsl_stream(inlet, buffer_length=1)

    if not stream:
        print("There are no values being read through the EEG Stream!")
        return -1
        
    # This sample[0] means that we are pulling only the data from the first node
    raw_data = []
    

    sample_number = 20
    averaged_data_list = []
    averaged_filtered_data_list = []

    for k in range(num_data_points):
        data_totals = []
        filtered_data_totals = []
        for i in range (17):
            data_totals.append(0)
            filtered_data_totals.append(0)

        for _ in range(sample_number):
            sample, timestamp = inlet.pull_sample()
            #print(timestamp, sample)
            #filtered_sample = highpass_filter(sample, cutoff=60, fs=250)
            filtered_sample = sample
            #print(sample)
            #print("Filtered sample: ")
            #print(filtered_sample)
            for i in range (len(sample)):
                data_totals[i] += sample[i]
                filtered_data_totals[i] += filtered_sample[i]
        
        #print(averaged_filtered_data_list)
        # Average the totals
        average_data = [x / sample_number for x in data_totals]
        filtered_average_data = [x / sample_number for x in filtered_data_totals]
        averaged_data_list.append(average_data)
        averaged_filtered_data_list.append(filtered_average_data)
    
        

    with open('averaged_eeg_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header row
        writer.writerow(['EEG1', 'EEG2', 'EEG3', 'EEG4', 'EEG5', 'EEG6', 'EEG7', 'EEG8',
                         'Accel X', 'Accel Y', 'Accel Z', 'Gyro X', 'Gyro Y',
                         'Battery %', 'Counter', 'Indicator'])

        # Record start time
        for i in range(num_data_points):
            writer.writerow(averaged_filtered_data_list[i])


def EEGThreshold(threshold):
    raw_data, filtered_data = getEEGValues()
    print("Raw EEG Data:", filtered_data)
    print("Filtered EEG Data:", filtered_data)
   # return (sum(filtered_data) / len(filtered_data))

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

        while time.time() - start_time < 5:
            # Get EEG data
            unfiltered_eeg_data, eeg_data = getEEGValues()
            #eeg_data = eeg_data.tolist()

            # print("EEG_DATA", eeg_data)

            # Separate data into EEG and sensor data
            eeg_values = eeg_data[:8]
            sensor_data = eeg_data[8:11]
            gyro_data = eeg_data[11:13]
            battery_percentage = eeg_data[13]
            counter = eeg_data[14]
            indicator = eeg_data[15]

            #print("Indicator is: " + str(eeg_data))

            # print("Indicator", eeg_data[15])
            chunk_size = 16
            length = len(eeg_data)
            start_index = 0
            end_index = min(chunk_size, length)
            while start_index < length:
                chunk = eeg_data[start_index:end_index]
                if (len(chunk) != 0):
                    print("Chunk", chunk)

                start_index = end_index
                end_index = min(start_index + chunk_size, length)

                writer.writerow(chunk)

            # Average sensor data
            #averaged_eeg_values = [sum(eeg_values) / len(eeg_values) for _ in range(len(eeg_values))]
            #averaged_sensor_data = [sum(sensor_data) / len(sensor_data) for _ in range(len(sensor_data))]
            #averaged_gyro_data = [sum(gyro_data) / len(gyro_data) for _ in range(len(gyro_data))]

            # Write averaged data to CSV file
            # writer.writerow(eeg_data)
            #for i in range(len(eeg_data)):
            #    writer.writerow(eeg_values[i] + sensor_data[i] + gyro_data[i] + [battery_percentage, counter, indicator])

            # Wait for a short time before next iteration
            time.sleep(0.1)  # Adjust as needed
    print("Indicator is: " + str(unfiltered_eeg_data))

print("In main")
#EEGThreshold(0.1)
#average_and_output_csv()
start_time = time.time()
print("Starting time = " + str(start_time))
getEEGValuesInCSV(735)
end_time = time.time()
print("Ending time = " + str(end_time))
print("total elapsed time = " + str(end_time - start_time))
