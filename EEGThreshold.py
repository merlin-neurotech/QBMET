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




def getEEGValuesInCSV(num_data_rows, num_samples):
    # Initialize the unicorn headset to read data
    data_stream = resolve_stream("name='Unicorn'")
    inlet = StreamInlet(data_stream[0])
    stream = streams.lsl_stream(inlet, buffer_length=1)

    # Check to make sure that values are being read
    if not stream:
        print("There are no values being read through the EEG Stream!")
        return -1
        
    
    # Initialize the lists
    raw_data = []
    averaged_data_list = []
    averaged_filtered_data_list = []

    # Collect the averaged data rows and store them in the above lists
    for k in range(num_data_rows):
        data_totals = []
        filtered_data_totals = []

        # Clear the list and fill it with zeros to write to it
        for i in range (17):
            data_totals.append(0)
            filtered_data_totals.append(0)

        # Get the data for a set number of samples and add them to a total amount
        # Currently the filtering doesn't work so the filtered data is just the unfiltered sample
        for _ in range(num_samples):
            sample, timestamp = inlet.pull_sample()
            #filtered_sample = highpass_filter(sample, cutoff=60, fs=250)
            filtered_sample = sample
            #print(timestamp, sample)

            # Add the values in sample to their respective column
            for i in range (len(sample)):
                data_totals[i] += sample[i]
                filtered_data_totals[i] += filtered_sample[i]
        

        # Average the totalled values by dividing the number of samples, and then append that to the list
        average_data = [x / num_samples for x in data_totals]
        filtered_average_data = [x / num_samples for x in filtered_data_totals]
        averaged_data_list.append(average_data)
        averaged_filtered_data_list.append(filtered_average_data)
    
        

    # Once we've collected our data, write it to the csv file
    with open('averaged_eeg_data.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header row
        writer.writerow(['EEG1', 'EEG2', 'EEG3', 'EEG4', 'EEG5', 'EEG6', 'EEG7', 'EEG8',
                         'Accel X', 'Accel Y', 'Accel Z', 'Gyro X', 'Gyro Y',
                         'Battery %', 'Counter', 'Indicator'])

        # Write data rows
        for i in range(num_data_rows):
            writer.writerow(averaged_filtered_data_list[i])




print("In main")
#EEGThreshold(0.1)
#average_and_output_csv()
start_time = time.time()
print("Starting time = " + str(start_time))
# Through trial and error, this number of samples will run for approximately 1 minute
getEEGValuesInCSV(num_data_rows=735, num_samples=20)
end_time = time.time()
print("Ending time = " + str(end_time))
print("total elapsed time = " + str(end_time - start_time))
