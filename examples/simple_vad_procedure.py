from voice_detection.vad import VAD

if __name__ == '__main__':
    foo = VAD('../audio/count to ten.wav', save_path=r'../results')
    # or you can visualize process
    # foo = VAD('../audio/count to ten.wav', save_path=r'../results', visualise=True)
