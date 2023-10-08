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
from PyQt5.QtGui import QPalette, QColor

# Classe per generare l'audio
class AudioGenerator:
    def __init__(self, generator_id, frequency=440.0, volume=0.5, waveform='Sine'):
        # Inizializza i parametri dell'oggetto
        self.generator_id = generator_id  # Identificatore del generatore
        self.frequency = frequency  # Frequenza dell'onda sonora (default: 440 Hz)
        self.volume = volume  # Volume dell'onda sonora (default: 0.5)
        self.waveform = waveform  # Tipo di forma d'onda (default: 'Sine')
        self.audio_stream = None  # Oggetto per la riproduzione dell'audio
        self.playing = False  # Indica se l'audio è in riproduzione o no

    # Avvia la riproduzione dell'audio
    def start(self):
        p = pyaudio.PyAudio()
        self.audio_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=int(self.frequency * 10), output=True,
                                   stream_callback=self.callback)
        self.playing = True

    # Ferma la riproduzione dell'audio
    def stop(self):
        if self.audio_stream is not None:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.playing = False

    # Callback per generare i dati dell'audio in base alla forma d'onda selezionata
    def callback(self, in_data, frame_count, time_info, status):
        if self.waveform == 'Sine':
            waveform = np.sin(2 * np.pi * np.arange(frame_count) * self.frequency / 44100.0)
        elif self.waveform == 'Square':
            waveform = np.sign(np.sin(2 * np.pi * np.arange(frame_count) * self.frequency / 44100.0))
        elif self.waveform == 'Triangle':
            waveform = np.abs(2 * (np.arange(frame_count) * self.frequency / 44100.0 - np.floor(0.5 + np.arange(frame_count) * self.frequency / 44100.0)))
        elif self.waveform == 'Sawtooth':
            waveform = 2 * (np.arange(frame_count) * self.frequency / 44100.0 - np.floor(0.5 + np.arange(frame_count) * self.frequency / 44100.0))
        else:
            waveform = np.random.uniform(-1, 1, frame_count)

        data = (self.volume * waveform).astype(np.float32).tobytes()
        return (data, pyaudio.paContinue)

# Classe principale dell'app
class AudioGeneratorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.generators = []  # Lista dei generatori audio
        self.init_ui()
        self.setWindowTitle("Triple Multiple Wave Generator")  # Imposta il titolo della finestra

    # Inizializza l'interfaccia utente
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Aggiungi il titolo nella parte superiore con il colore del testo bianco
        title_label = QLabel("Triple Multiple Wave Generator")
        title_label.setStyleSheet("font-size: 20px; color: white; padding: 10px; background-color: indigo;")  # Imposta il colore del testo e il padding
        layout.addWidget(title_label)

        for i in range(3):
            generator = AudioGenerator(i)  # Crea un nuovo generatore audio
            self.generators.append(generator)  # Aggiunge il generatore alla lista

            label = QLabel(f'Generatore {i + 1}: STOP')  # Etichetta per lo stato del generatore
            layout.addWidget(label)
            generator.status_label = label

            frequency_slider = QSlider(Qt.Horizontal)  # Slider per la frequenza
            frequency_slider.setMinimum(20)
            frequency_slider.setMaximum(2000)
            frequency_slider.valueChanged.connect(lambda val, idx=i: self.update_frequency(idx, val))
            layout.addWidget(frequency_slider)

            volume_slider = QSlider(Qt.Horizontal)  # Slider per il volume
            volume_slider.setMinimum(0)
            volume_slider.setMaximum(10)
            volume_slider.valueChanged.connect(lambda val, idx=i: self.update_volume(idx, val))
            layout.addWidget(volume_slider)

            waveform_combo = QComboBox()  # ComboBox per selezionare la forma d'onda
            waveform_combo.addItems(['Sine', 'Square', 'Triangle', 'Sawtooth', 'Random'])
            waveform_combo.currentIndexChanged.connect(lambda combo_idx, idx=i: self.change_waveform(idx, combo_idx))
            layout.addWidget(waveform_combo)

            start_button = QPushButton('Start')  # Pulsante per avviare la riproduzione
            start_button.clicked.connect(lambda state, idx=i: self.start_audio_generation(idx))
            layout.addWidget(start_button)

            stop_button = QPushButton('Stop')  # Pulsante per fermare la riproduzione
            stop_button.clicked.connect(lambda state, idx=i: self.stop_audio_generation(idx))
            layout.addWidget(stop_button)

            reset_button = QPushButton('Reset')  # Pulsante per ripristinare le impostazioni predefinite
            reset_button.clicked.connect(lambda state, idx=i: self.reset_settings(idx))
            layout.addWidget(reset_button)

            save_button = QPushButton('Save')  # Pulsante per salvare l'audio generato
            save_button.clicked.connect(lambda state, idx=i: self.save_audio(idx))
            layout.addWidget(save_button)

        self.show()

    # Avvia la riproduzione dell'audio per un generatore specifico
    def start_audio_generation(self, idx):
        generator = self.generators[idx]
        generator.start()
        generator.status_label.setText(f'Generatore {idx + 1}: IS START')

    # Ferma la riproduzione dell'audio per un generatore specifico
    def stop_audio_generation(self, idx):
        generator = self.generators[idx]
        generator.stop()
        generator.status_label.setText(f'Generatore {idx + 1}: STOP')

    # Ripristina le impostazioni predefinite per un generatore specifico
    def reset_settings(self, idx):
        generator = self.generators[idx]
        generator.frequency = 440.0
        generator.volume = 0.5
        generator.waveform = 'Sine'
        generator.status_label.setText(f'Generatore {idx + 1}: STOP')

    # Salva l'audio generato in un file WAV per un generatore specifico
    def save_audio(self, idx):
        generator = self.generators[idx]
        wf = wave.open(f'audio_{idx}.wav', 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        wf.writeframes(generator.generate_audio(3))
        wf.close()

    # Aggiorna la frequenza per un generatore specifico
    def update_frequency(self, idx, value):
        generator = self.generators[idx]
        generator.frequency = value

    # Aggiorna il volume per un generatore specifico
    def update_volume(self, idx, value):
        generator = self.generators[idx]
        generator.volume = value / 10

    # Cambia la forma d'onda per un generatore specifico
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

# Funzione principale per avviare l'applicazione
def main():
    app = QApplication(sys.argv)
    main_win = AudioGeneratorApp()
    sys.exit(app.exec_())

# Punto di ingresso dell'app
if __name__ == '__main__':
    main()
