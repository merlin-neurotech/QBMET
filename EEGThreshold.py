import neurol
from neurol import BCI_tools as bci
from neurol import streams
from pylsl import StreamInlet, resolve_stream
import numpy as np

def getEEGValues():
    streams1 = resolve_stream("name='Unicorn'")
    inlet = StreamInlet(streams1[0])
    #inlet2 = bci.filter_signal(signal=np.asarray(inlet), sampling_rate=250)
    stream = streams.lsl_stream(inlet,buffer_length=1024)

    if not stream:
        print("There is no values being read through the EEG Stream!")
        return -1
        

    data = []
    for _ in range(1):
        sample, timestamp = inlet.pull_sample()
        ext_sample = sample[0]
        #print(timestamp, sample)
        data.append(sample[0])
    print(data)
    #return (sum(data) / len(data))

def EEGThreshold(threshold):
    #EEG_val = getEEGValues()
    getEEGValues()
    EEG_val = 1
    if (EEG_val > threshold):
        print("Greater than the threshold!")
        return 1
    else:
        print("Less than the threshold!")
        return 0
#change



print("In main")
EEGThreshold(0.1)