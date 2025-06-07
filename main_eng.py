# Software Name: Triple Multiple Wave Generator
# Author: Bocaletto Luca
# License: GPLv3

import sys
import numpy as np
import pyaudio
import wave
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QPushButton, QVBoxLayout, QWidget, QLabel, QComboBox
from PyQt5.QtCore import Qt

# Class for generating audio
class AudioGenerator:
    def __init__(self, generator_id, frequency=440.0, volume=0.5, waveform='Sine'):
        # Initialize object parameters
        self.generator_id = generator_id      # Generator identifier
        self.frequency = frequency            # Frequency of the audio wave (default: 440 Hz)
        self.volume = volume                  # Volume of the audio wave (default: 0.5)
        self.waveform = waveform              # Waveform type (default: 'Sine')
        self.audio_stream = None              # Audio stream object for playback
        self.playing = False                  # Indicates whether audio is playing

    # Generate audio data for a given duration (in seconds)
    def generate_audio(self, duration):
        sample_rate = 44100
        num_samples = int(sample_rate * duration)
        if self.waveform == 'Sine':
            wave_data = np.sin(2 * np.pi * np.arange(num_samples) * self.frequency / sample_rate)
        elif self.waveform == 'Square':
            wave_data = np.sign(np.sin(2 * np.pi * np.arange(num_samples) * self.frequency / sample_rate))
        elif self.waveform == 'Triangle':
            wave_data = np.abs(2 * (np.arange(num_samples) * self.frequency / sample_rate - 
                                    np.floor(0.5 + np.arange(num_samples) * self.frequency / sample_rate)))
        elif self.waveform == 'Sawtooth':
            wave_data = 2 * (np.arange(num_samples) * self.frequency / sample_rate - 
                             np.floor(0.5 + np.arange(num_samples) * self.frequency / sample_rate))
        else:
            wave_data = np.random.uniform(-1, 1, num_samples)
        
        data = (self.volume * wave_data).astype(np.float32).tobytes()
        return data

    # Start audio playback
    def start(self):
        p = pyaudio.PyAudio()
        self.audio_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100,
                                   output=True, stream_callback=self.callback)
        self.playing = True

    # Stop audio playback
    def stop(self):
        if self.audio_stream is not None:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.playing = False

    # Callback for generating audio data based on the selected waveform
    def callback(self, in_data, frame_count, time_info, status):
        sample_rate = 44100
        if self.waveform == 'Sine':
            wave_data = np.sin(2 * np.pi * np.arange(frame_count) * self.frequency / sample_rate)
        elif self.waveform == 'Square':
            wave_data = np.sign(np.sin(2 * np.pi * np.arange(frame_count) * self.frequency / sample_rate))
        elif self.waveform == 'Triangle':
            wave_data = np.abs(2 * (np.arange(frame_count) * self.frequency / sample_rate - 
                                    np.floor(0.5 + np.arange(frame_count) * self.frequency / sample_rate)))
        elif self.waveform == 'Sawtooth':
            wave_data = 2 * (np.arange(frame_count) * self.frequency / sample_rate - 
                             np.floor(0.5 + np.arange(frame_count) * self.frequency / sample_rate))
        else:
            wave_data = np.random.uniform(-1, 1, frame_count)
        
        data = (self.volume * wave_data).astype(np.float32).tobytes()
        return (data, pyaudio.paContinue)

# Main application class
class AudioGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.generators = []  # List to store audio generators
        self.init_ui()
        self.setWindowTitle("Triple Multiple Wave Generator")

    # Initialize the user interface
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Add the title at the top with white text and indigo background
        title_label = QLabel("Triple Multiple Wave Generator")
        title_label.setStyleSheet("font-size: 20px; color: white; padding: 10px; background-color: indigo;")
        layout.addWidget(title_label)

        for i in range(3):
            generator = AudioGenerator(i)
            self.generators.append(generator)

            status_label = QLabel(f"Generator {i + 1}: STOP")
            layout.addWidget(status_label)
            generator.status_label = status_label

            # Frequency slider
            frequency_slider = QSlider(Qt.Horizontal)
            frequency_slider.setMinimum(20)
            frequency_slider.setMaximum(2000)
            frequency_slider.valueChanged.connect(lambda val, idx=i: self.update_frequency(idx, val))
            layout.addWidget(frequency_slider)

            # Volume slider
            volume_slider = QSlider(Qt.Horizontal)
            volume_slider.setMinimum(0)
            volume_slider.setMaximum(10)
            volume_slider.valueChanged.connect(lambda val, idx=i: self.update_volume(idx, val))
            layout.addWidget(volume_slider)

            # ComboBox to select the waveform
            waveform_combo = QComboBox()
            waveform_combo.addItems(['Sine', 'Square', 'Triangle', 'Sawtooth', 'Random'])
            waveform_combo.currentIndexChanged.connect(lambda combo_idx, idx=i: self.change_waveform(idx, combo_idx))
            layout.addWidget(waveform_combo)

            # Start button
            start_button = QPushButton("Start")
            start_button.clicked.connect(lambda state, idx=i: self.start_audio_generation(idx))
            layout.addWidget(start_button)

            # Stop button
            stop_button = QPushButton("Stop")
            stop_button.clicked.connect(lambda state, idx=i: self.stop_audio_generation(idx))
            layout.addWidget(stop_button)

            # Reset button to restore default settings
            reset_button = QPushButton("Reset")
            reset_button.clicked.connect(lambda state, idx=i: self.reset_settings(idx))
            layout.addWidget(reset_button)

            # Save button to save the generated audio
            save_button = QPushButton("Save")
            save_button.clicked.connect(lambda state, idx=i: self.save_audio(idx))
            layout.addWidget(save_button)

        self.show()

    # Start audio generation for a specific generator
    def start_audio_generation(self, idx):
        generator = self.generators[idx]
        generator.start()
        generator.status_label.setText(f"Generator {idx + 1}: IS STARTING")

    # Stop audio generation for a specific generator
    def stop_audio_generation(self, idx):
        generator = self.generators[idx]
        generator.stop()
        generator.status_label.setText(f"Generator {idx + 1}: STOP")

    # Reset the settings to default for a specific generator
    def reset_settings(self, idx):
        generator = self.generators[idx]
        generator.frequency = 440.0
        generator.volume = 0.5
        generator.waveform = 'Sine'
        generator.status_label.setText(f"Generator {idx + 1}: STOP")

    # Save the generated audio to a WAV file for a specific generator
    def save_audio(self, idx):
        generator = self.generators[idx]
        wf = wave.open(f"audio_{idx}.wav", "wb")
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        data = generator.generate_audio(3)
        wf.writeframes(data)
        wf.close()

    # Update the frequency for a specific generator
    def update_frequency(self, idx, value):
        generator = self.generators[idx]
        generator.frequency = value

    # Update the volume for a specific generator
    def update_volume(self, idx, value):
        generator = self.generators[idx]
        generator.volume = value / 10

    # Change the waveform for a specific generator
    def change_waveform(self, idx, combo_idx):
        generator = self.generators[idx]
        if combo_idx == 0:
            generator.waveform = 'Sine'
        elif combo_idx == 1:
            generator.waveform = 'Square'
        elif combo_idx == 2:
            generator.waveform = 'Triangle'
        elif combo_idx == 3:
            generator.waveform = 'Sawtooth'
        else:
            generator.waveform = 'Random'

# Main function to run the application
def main():
    app = QApplication(sys.argv)
    main_window = AudioGeneratorApp()
    sys.exit(app.exec_())

# Entry point of the application
if __name__ == '__main__':
    main()
