# if we just start to detect voice with default value of thresholds when we except bad result
# we need to correct thresholds to get good looked view
# look at speech descriptors graphs and change thresholds value (sometimes it can be negative)
# the black line guides you

from voice_detection.vad import VAD

if __name__ == '__main__':
    # bar = VAD('../audio/count colors.wav', visualise=True, save_path='../results',
    #           rolloff_threshold=0.94,
    #           zerocrossing_threshold=1.05,
    #           flatness_threshold=2.2)
    baz = VAD('../audio/boosted count to ten.wav', visualise=True, save_path='../results',
              energy_threshold=-3*10**-1,
              flatness_threshold=0.03)
