"""This module provides simple visualization of voice activity detection process using matplotlib"""

import librosa
import matplotlib.pyplot as plt
import numpy as np

from utils.audio_operations import normalize

COLORS = ['#42f5cb',
          '#51c9fc',
          '#bd7aff',
          '#F7728A',
          '#59ff6a']

LABELS = ['audio signal and detected regions',
          'short term energy',
          'zero crossing rate',
          'spectral flatness',
          'spectral rolloff'
          ]

LINES = ["-", "--", "-.", "-."]


def plotting_descriptors(signal, *args, **kwargs):
    """Visualize audio signal and main speech descriptors

    :param signal: audio signal librosa.load() object;
    :param args: speech descriptions, not all of them can be used. (default: all of them);
    :param kwargs: help to plot detected regions
    """
    detect = kwargs.get('detection_region')
    frame_length = kwargs.get('frame_length')
    sample_rate = kwargs.get('sample_rate')

    # short_term_energy_impact = kwargs.get('short_term_energy_impact')
    # spectral_flatness_impact = kwargs.get('spectral_flatness_impact')
    # spectral_rolloff_impact = kwargs.get('spectral_rolloff_impact')
    # zero_crossing_rate_impact = kwargs.get('zero_crossing_rate_impact')
    impacts = list(kwargs.values())[3:]
    duration = librosa.get_duration(signal)

    plt.rcParams.update({'font.size': 14})
    fig = plt.figure(figsize=(16, 14))
    fig_grid = plt.GridSpec(ncols=1, nrows=len(args) + 1, figure=fig)
    plt.subplot(fig_grid[0, 0])
    plt.title(LABELS[0])

    for i in range(len(detect)):
        color = '#C3C5C7' if detect[i] else 'white'

        plt.axvspan((i * frame_length * 0.5),
                    ((i * frame_length * sample_rate / 2) + frame_length * sample_rate / 2) / sample_rate,
                    color=color, lw=0, alpha=0.2)
    #
    # plt.plot(np.linspace(0, duration, len(zero_crossing_rate_impact)), zero_crossing_rate_impact, color=COLORS[2],
    #          ls='-.')
    #
    # plt.plot(np.linspace(0, duration, len(spectral_flatness_impact)), spectral_flatness_impact, color=COLORS[3],
    #          ls='dotted')
    #
    # plt.plot(np.linspace(0, duration, len(spectral_rolloff_impact)), spectral_rolloff_impact, color=COLORS[4],
    #          ls='dashed')
    #
    plt.plot(np.linspace(0, duration, len(signal)), normalize(signal), color=COLORS[0], label=LABELS[0])
    # '-', '--', '-.', ':', 'None', ' ', '', 'solid', 'dashed', 'dashdot', 'dotted'
    if args:
        for i in range(len(args)):
            plt.subplot(fig_grid[i + 1, 0])
            plt.title(LABELS[i + 1])
            plt.plot(np.linspace(0, duration, len(impacts[i])), impacts[i], color='black', ls=LINES[i], alpha=0.4)
            plt.plot(np.linspace(0, duration, len(args[i])), args[i], color=COLORS[i + 1])
            plt.fill_between(np.linspace(0, duration, len(args[i])), args[i], 0, color=COLORS[i + 1], alpha=0.3)
            plt.grid(alpha=0.4)

    plt.xlabel('Time, seconds')
    plt.subplots_adjust(hspace=0.7)
    plt.show()


def plot_signals_comparison(signal, cut_signal, sample_rate):
    """Plot comparison graph

    :param signal: original audio signal;
    :param cut_signal: signal after voice activity detection procedure;
    :param sample_rate: sample rate of both signals.
    """
    signal_duration = librosa.get_duration(signal)
    plt.rcParams.update({'font.size': 14})
    fig = plt.figure(figsize=(12, 8))

    plt.subplot(2, 1, 1)
    plt.title('Original audio signal')
    plt.plot(np.linspace(0, signal_duration, len(signal)), signal, color=COLORS[0])
    plt.grid(alpha=0.5)

    plt.subplot(2, 1, 2)
    plt.title('Voice activity')
    plt.plot(np.linspace(0, int(len(cut_signal) / sample_rate), len(cut_signal)), cut_signal, color=COLORS[1])
    plt.grid(alpha=0.5)
    plt.xlabel('Time, seconds')
    plt.show()


def plotting_descriptors_verbose(signal, *args, **kwargs):
    """Visualize audio signal and main speech descriptors

        :param signal: audio signal librosa.load() object;
        :param args: speech descriptions, not all of them can be used. (default: all of them);
        :param kwargs: help to plot detected regions
        """
    duration = librosa.get_duration(signal)
    plt.rcParams.update({'font.size': 14})
    fig = plt.figure(figsize=(16, 14))
    fig_grid = plt.GridSpec(ncols=1, nrows=len(args) + 1, figure=fig)
    plt.subplot(fig_grid[0, 0])
    plt.title(LABELS[0])
    detect = kwargs.get('detection_region')
    frame_length = kwargs.get('frame_length')
    sample_rate = kwargs.get('sample_rate')

    for i in range(len(detect)):
        color = '#C3C5C7' if detect[i] else 'white'

        plt.axvspan((i * frame_length * 0.5),
                    ((i * frame_length * sample_rate / 2) + frame_length * sample_rate / 2) / sample_rate,
                    color=color, lw=0, alpha=0.2)

    plt.plot(np.linspace(0, duration, len(signal)), signal, color=COLORS[0], label=LABELS[0])

    if args:
        for i in range(len(args)):
            plt.subplot(fig_grid[i + 1, 0])
            plt.title(LABELS[i + 1])
            plt.plot(np.linspace(0, duration, len(args[i])), args[i], color=COLORS[i + 1])
            plt.fill_between(np.linspace(0, duration, len(args[i])), args[i], 0, color=COLORS[i + 1], alpha=0.3)
            plt.grid(alpha=0.4)

    plt.xlabel('Time, seconds')
    plt.subplots_adjust(hspace=0.7)
    plt.show()
