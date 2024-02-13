import neurol2
from neurol2 import streams

def getEEGValues():
    streams1 = resolve_stream("name='Unicorn'")
    inlet = StreamInlet(streams1[0])
    stream = streams.lsl_stream(inlet,buffer_length=1024)

    if not stream:
        print("There is no values being read through the EEG Stream!")
        return -1

    return (sum(stream) / len(stream))

def EEGThreshold(threshold):
    EEG_val = getEEGValues()
    if (EEG_val > threshold):
        #print("Greater than the threshold!")
        return 1
    else:
        #print("Less than the threshold!")
        return 0

