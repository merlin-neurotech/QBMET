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
    stream = inlet

    if not stream:
        print("There is no values being read through the EEG Stream!")
        return -1

    data = []
    for _ in range(1):
        sample, timestamp = inlet.pull_sample()
        data.append(sample[0])

    filtered_data = highpass_filter(data, cutoff=60, fs=250)  # fs is the sampling rate
    print(filtered_data)


def EEGThreshold(threshold):
    getEEGValues()
    EEG_val = 1  # This should be replaced with actual processed data
    if EEG_val > threshold:
        print("Greater than the threshold!")
        return 1
    else:
        print("Less than the threshold!")
        return 0


print("In main")
EEGThreshold(0.1)
