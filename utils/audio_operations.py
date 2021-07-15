"""This module provides some basic operations that help to manipulate audio signal"""

import decimal

import numpy as np
import sklearn


def round_half_up(number):
    """Round half up a number

    :param number: the number to be rounded;
    :return: rounded value.
    """
    rounded_value = int(decimal.Decimal(number).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return rounded_value


def framing_signal(audio_signal, sample_rate, frame_length=0.03, frame_overlap=0.015, ):
    """Separate audio signal into frames

    :param audio_signal: librosa.open() object;
    :param frame_length: length of each frame (default = 0.03);
    :param frame_overlap: duration of frames overlap (default = 0.015);
    :param sample_rate: sample rate of audio signal (librosa open() object)
    :return numpy array of frames.
    """
    frame_length, frame_step = frame_length * sample_rate, frame_overlap * sample_rate
    signal_length = len(audio_signal)
    frame_length = int(round(frame_length))
    frame_step = int(round(frame_step))
    num_frames = int(np.ceil(float(np.abs(signal_length - frame_length)) / frame_step))

    pad_signal_length = num_frames * frame_step + frame_length
    z = np.zeros((pad_signal_length - signal_length))
    pad_signal = np.append(audio_signal, z)

    indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + np.tile(
        np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
    frames = pad_signal[indices.astype(np.int32, copy=False)]
    frames *= np.blackman(frame_length)
    return frames


def deframing_signal(array_of_frames, signal_length, frame_length, frame_overlap,
                     window_function=lambda x: np.ones((x,))):
    """Concatenate framing signal into normal signal

    :param array_of_frames: numpy array of audio signal frames;
    :param signal_length: audio signal length using len() function;
    :param frame_length: length of each frame (default = 0.03);
    :param frame_overlap: duration of frames overlap (default = 0.015);
    :param window_function: window function;
    :return array of audio signal.
    """
    frame_length = round_half_up(frame_length)
    frame_overlap = round_half_up(frame_overlap)
    number_of_frames = np.shape(array_of_frames)[0]
    assert np.shape(array_of_frames)[
               1] == number_of_frames, '"frames" matrix is wrong size, 2nd dim is not equal to frame_len'

    indices = np.tile(np.arange(0, frame_length), (number_of_frames, 1)) + np.tile(
        np.arange(0, number_of_frames * frame_overlap, frame_overlap), (frame_length, 1)).T
    indices = np.array(indices, dtype=np.int32)
    padlen = (number_of_frames - 1) * frame_overlap + frame_length

    if signal_length <= 0:
        siglen = padlen

    rec_signal = np.zeros((padlen,))
    window_correction = np.zeros((padlen,))
    win = window_function(frame_length)

    for i in range(0, number_of_frames):
        window_correction[indices[i, :]] = window_correction[
                                               indices[i, :]] + win + 1e-15  # add a little bit so it is never zero
        rec_signal[indices[i, :]] = rec_signal[indices[i, :]] + array_of_frames[i, :]

    rec_signal = rec_signal / window_correction
    return rec_signal[0:siglen]


def normalize(x, axis=0):
    """Normalize any array of values"""
    return sklearn.preprocessing.minmax_scale(x, axis=axis)
