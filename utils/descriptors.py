"""This module provides some basic speech descriptors that help to detect speech activity in voice signal"""

import librosa
import numpy as np
import scipy
import scipy.stats


def short_term_frame(frame):
    """Calculate short term energy of frame"""
    return sum([abs(x) ** 2 for x in frame]) / len(frame)


def short_term_energy(frames):
    """Calculate short term energy of each frame from array of frames"""
    return [short_term_frame(frame) for frame in frames]


def additional_short_term_energy(framed_signal):
    """Another way to calculate short term energy using librosa library"""
    return [librosa.feature.rms(frame) for frame in framed_signal]


def zero_crossing_frame(frame):
    """Calculate zero crossing rate of frame"""
    signs = np.sign(frame)
    signs[signs == 0] = -1
    return len(np.where(np.diff(signs))[0]) / len(frame)


def zero_crossing_rate(frames):
    """Calculate zero crossing rate of each frame from array of frames"""
    norm = [frame * np.hanning(len(frame)) for frame in frames]
    return [zero_crossing_frame(frame) for frame in norm]


def additional_zero_crossing_rate(framed_signal):
    """Another way to calculate short term energy using librosa library"""
    return [librosa.feature.zero_crossing_rate(frame, )[0][0] for frame in framed_signal]


def spectral_flatness_frame(frame):
    """Calculate spectral flatness of frame"""
    geometric_mean = scipy.stats.mstats.gmean(abs(frame))
    arithmetic_mean = np.mean(frame)
    return 10 * np.log10(geometric_mean / arithmetic_mean)


def spectral_flatness(pow_frames):
    """Calculate spectral flatness of each frame from array of frames"""
    return [spectral_flatness_frame(frame) for frame in pow_frames]


def additional_spectral_flatness(framed_signal, nfft=4096):
    """Another way to calculate spectral flatness using librosa library"""
    return [librosa.feature.spectral_flatness(frame, n_fft=nfft)[0][0] for frame in framed_signal]


def spectral_rolloff(framed_signal, nfft=4096):
    """Calculate spectral_rolloff of each frame"""
    return [librosa.feature.spectral_rolloff(frame, roll_percent=0.97, n_fft=nfft)[0][0] for frame in
            framed_signal]


def spectral_bandwidth(framed_signal, nfft=4096):
    """Calculate spectral_bandwidth of each frame"""
    return [librosa.feature.spectral_bandwidth(frame, n_fft=nfft)[0][0] for frame in
            framed_signal]
