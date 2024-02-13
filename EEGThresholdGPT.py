import numpy as np
from pylsl import StreamInlet, resolve_stream
from scipy.signal import butter, lfilter, lfilter_zi


def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="high", analog=False)
    return b, a


def live_highpass_filter(data, b, a, zi):
    y, zo = lfilter(b, a, data, zi=zi)
    return y, zo


def getEEGValues():
    streams1 = resolve_stream("name='Unicorn'")
    inlet = StreamInlet(streams1[0])

    b, a = butter_highpass(cutoff=60, fs=250)  # fs is the sampling rate
    zi = lfilter_zi(b, a)

    while True:
        sample, timestamp = inlet.pull_sample()
        if sample:
            filtered_sample, zi = live_highpass_filter(
                [sample], b, a, zi
            )  # Ensure sample is in list format
            print("Timestamp:", timestamp, "Filtered Sample:", filtered_sample)


def EEGThreshold(threshold):
    getEEGValues()
    # Implement your threshold logic here


print("In main")
EEGThreshold(0.1)
