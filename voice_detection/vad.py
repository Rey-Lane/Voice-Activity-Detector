"""This module provides voice activity detector that works on calculated speech descriptors"""
import pathlib
import warnings

import librosa
import noisereduce as nr
import numpy as np
import soundfile as sf
from loguru import logger

import utils.audio_operations as audio_operations
import utils.descriptors as speech_descriptors
import utils.visualize as verbose

warnings.filterwarnings("ignore")


class VAD:

    def __init__(self, file, save_path=None, frame_length=0.03, frame_overlap=0.015, energy_threshold=5 * 10 ** -6,
                 flatness_threshold=0.12, zerocrossing_threshold=0.9, rolloff_threshold=0.7, visualise=False,
                 N_frames=31):
        """Initialize main params

        :param file: name of audio file with path;
        :param save_path: path to save cut audio file (default: current dir);
        :param frame_length: length of each frame (default = 0.03);
        :param frame_overlap: duration of frames overlap (default = 0.015);
        :param energy_threshold: threshold of short term energy (default: 5 * 10 ** -6);
        :param flatness_threshold: threshold of spectral flatness (default: 0.12);
        :param zerocrossing_threshold: threshold of zero crossing rate (default: 0.9);
        :param rolloff_threshold: threshold of spectral rolloff (default: 0.7);
        :param visualise: if True show descriptor graphs that can help to configure thresholds;
        :param N_frames: number of first silent frames.
        """
        self.file = file
        self.file_name = "".join(self.file.split(".")[:-1])
        self.file_format = self.file.split(".")[-1]

        self.save_path = save_path
        self.frame_length = frame_length
        self.frame_overlap = frame_overlap
        self.energy_threshold = energy_threshold
        self.flatness_threshold = flatness_threshold
        self.zerocrossing_threshold = zerocrossing_threshold
        self.rolloff_threshold = rolloff_threshold
        self.visualise = visualise
        self.n_frames = N_frames

        self.__speech_descriptors()
        self.__mean_values()
        self.__voice_indexes()
        self.__separate_speech_information()
        self.__save_signal()

    def __speech_descriptors(self):
        """Calculate main speech descriptors"""
        logger.info("Calculate speech descriptors")
        self.signal, self.sample_rate = librosa.load(self.file, mono=True)
        self.signal = nr.reduce_noise(self.signal, self.signal[:-1])
        # self.signal = audio_operations.normalize(self.signal)
        self.framed_signal = audio_operations.framing_signal(self.signal, self.sample_rate, frame_length=0.03,
                                                             frame_overlap=0.015)
        self.preemphasis_signal = librosa.effects.preemphasis(self.signal)
        self.preemphasis_framed_signal = audio_operations.framing_signal(self.signal, self.sample_rate,
                                                                         frame_length=0.03,
                                                                         frame_overlap=0.015)

        self.short_term_energy = speech_descriptors.short_term_energy(self.framed_signal) / np.linalg.norm(
            speech_descriptors.short_term_energy(self.framed_signal))
        self.short_term_energy = audio_operations.normalize(self.short_term_energy)

        self.zero_crossing_rate = speech_descriptors.additional_zero_crossing_rate(self.framed_signal)
        self.zero_crossing_rate = audio_operations.normalize(self.zero_crossing_rate)

        self.spectral_flatness = speech_descriptors.additional_spectral_flatness(self.preemphasis_framed_signal)
        self.spectral_flatness = audio_operations.normalize(self.spectral_flatness)

        self.spectral_rolloff = speech_descriptors.spectral_rolloff(self.preemphasis_framed_signal)
        self.spectral_rolloff = audio_operations.normalize(self.spectral_rolloff)

    def __mean_values(self):
        """Calculate mean value of each first 30 frames of speech descriptor"""
        logger.info("Get mean values")
        self.mean_energy = np.mean(self.short_term_energy[:self.n_frames])
        self.mean_flatness = np.mean(self.spectral_flatness[:self.n_frames])
        self.mean_zerocross = np.mean(self.zero_crossing_rate[:self.n_frames])
        self.mean_rolloff = np.mean(self.spectral_rolloff[:self.n_frames])

    def __apply_descriptors(self):
        pass

    def __voice_indexes(self):
        """Calculate indexes where speech activity is appeared

        :return numpy array of speech activity indexes.
        """
        logger.info("Extract speech indexes")
        speech_detection = np.zeros(len(self.framed_signal), dtype='bool')
        speech_counter = 0
        silence_detection = 0
        self.spectral_flatness_impact = np.zeros(len(self.framed_signal), dtype='int')
        self.short_term_energy_impact = np.zeros(len(self.framed_signal), dtype='int')
        self.zero_crossing_rate_impact = np.zeros(len(self.framed_signal), dtype='int')
        self.spectral_rolloff_impact = np.zeros(len(self.framed_signal), dtype='int')

        for i in range(len(self.framed_signal)):

            if self.zero_crossing_rate[i] - self.mean_zerocross < self.zerocrossing_threshold:
                self.zero_crossing_rate_impact[i] = 1
            else:
                self.zero_crossing_rate_impact[i] = 0

            if self.spectral_flatness[i] - self.mean_flatness <= self.flatness_threshold:
                self.spectral_flatness_impact[i] = 1
            else:
                self.spectral_flatness_impact[i] = 0

            if self.short_term_energy[i] - self.mean_energy >= self.energy_threshold:
                self.short_term_energy_impact[i] = 1
            else:
                self.short_term_energy_impact[i] = 0

            if self.spectral_rolloff[i] - self.mean_rolloff <= self.rolloff_threshold:
                self.spectral_rolloff_impact[i] = 1
            else:
                self.spectral_rolloff_impact[i] = 0

            if self.spectral_flatness[i] - self.mean_flatness <= self.flatness_threshold and \
                    self.short_term_energy[i] - self.mean_energy >= self.energy_threshold and \
                    self.spectral_rolloff[i] - self.mean_rolloff <= self.rolloff_threshold and \
                    self.zero_crossing_rate[i] - self.mean_zerocross <= self.zerocrossing_threshold:

                speech_counter += 1
                if speech_counter >= 7:
                    speech_detection[i - 7:i] = True

            else:
                silence_detection += 1
                if silence_detection >= 7:
                    speech_detection[i - 7:i] = False
                speech_counter = 0
                silence_detection = 0

        self.indexes = np.where(speech_detection[:-1] != speech_detection[1:])[0]

        if self.visualise:
            logger.info("Plotting graphs")
            self.__print_current_threshold_values()
            verbose.plotting_descriptors(self.signal,
                                         self.short_term_energy,
                                         self.zero_crossing_rate,
                                         self.spectral_flatness,
                                         self.spectral_rolloff,
                                         detection_region=speech_detection,
                                         frame_length=self.frame_length,
                                         sample_rate=self.sample_rate,
                                         short_term_energy_impact=self.short_term_energy_impact,
                                         zero_crossing_rate_impact=self.zero_crossing_rate_impact,
                                         spectral_flatness_impact=self.spectral_flatness_impact,
                                         spectral_rolloff_impact=self.spectral_rolloff_impact)

    def __separate_speech_information(self):
        """Separate speech and noises"""
        logger.info("Separate speech and noises")
        coefficient = self.frame_length * self.sample_rate / 2
        self.cutted_signal = []
        i = 0

        logger.info("Join speech chunks")
        while i < len(self.indexes):
            chunk = self.signal[int(self.indexes[i] * coefficient):int(self.indexes[i + 1] * coefficient)]
            self.cutted_signal.extend(chunk)
            i += 2
        if self.visualise:
            verbose.plot_signals_comparison(self.signal, self.cutted_signal, self.sample_rate)

    def __save_signal(self):
        """Save signal to WAV format"""

        if not self.save_path:
            fn = pathlib.Path(self.file_name).name
            logger.info(f"Save result signal in {self.file_name}_vad.wav")
            sf.write(f'{fn}_vad.wav', self.cutted_signal, self.sample_rate)

        else:
            try:
                fn = pathlib.Path(self.file_name).name
                fp = pathlib.Path(self.save_path)
                logger.info(f"Save result signal in {fp}\\{fn}_vad.wav")
                sf.write(f'{fp}\\{fn}_vad.wav', self.cutted_signal, self.sample_rate)
            except RuntimeError:
                logger.error('Please check save path, the folder must exist')

    def __print_current_threshold_values(self):
        logger.info(f"Short term energy threshold: {self.energy_threshold}\n"
                    f"Zero crossing rate threshold: {self.zerocrossing_threshold}\n"
                    f"Spectral flatness threshold: {self.flatness_threshold}\n"
                    f"Spectral rolloff threshold: {self.rolloff_threshold}\n")
