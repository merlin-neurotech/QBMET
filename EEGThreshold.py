import neurol
from neurol import streams
from pylsl import StreamInlet, resolve_stream
import numpy as np
from pylsl import StreamInlet, resolve_stream
from scipy.signal import butter, filtfilt


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
        
    #This sample[0] means that we are pulling only the data fromt he first node
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



print("In main")
EEGThreshold(0.1)