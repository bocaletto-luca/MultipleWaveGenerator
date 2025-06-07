# Software Name: Generatore Triplo di Onde Multiple
# Autore: Bocaletto Luca
# Licenza: GPLv3

import sys
import numpy as np
import pyaudio
import wave
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QPushButton, QVBoxLayout, QWidget, QLabel, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor

# Classe per generare l'audio
class GeneratoreAudio:
    def __init__(self, id_generatore, frequenza=440.0, volume=0.5, forma_onda='Seno'):
        # Inizializza i parametri dell'oggetto
        self.id_generatore = id_generatore          # Identificatore del generatore
        self.frequenza = frequenza                  # Frequenza dell'onda sonora (default: 440 Hz)
        self.volume = volume                        # Volume dell'onda sonora (default: 0.5)
        self.forma_onda = forma_onda                # Tipo di forma d'onda (default: 'Seno')
        self.audio_stream = None                    # Oggetto per la riproduzione dell'audio
        self.playing = False                        # Indica se l'audio è in riproduzione o meno

    # Metodo per generare l'audio per una durata specificata (in secondi)
    def genera_audio(self, durata):
        sr = 44100
        num_samples = int(sr * durata)
        if self.forma_onda == 'Seno':
            onda = np.sin(2 * np.pi * np.arange(num_samples) * self.frequenza / sr)
        elif self.forma_onda == 'Quadrata':
            onda = np.sign(np.sin(2 * np.pi * np.arange(num_samples) * self.frequenza / sr))
        elif self.forma_onda == 'Triangolare':
            onda = np.abs(2 * (np.arange(num_samples) * self.frequenza / sr - 
                               np.floor(0.5 + np.arange(num_samples) * self.frequenza / sr)))
        elif self.forma_onda == 'Dente di sega':
            onda = 2 * (np.arange(num_samples) * self.frequenza / sr - 
                        np.floor(0.5 + np.arange(num_samples) * self.frequenza / sr))
        else:
            onda = np.random.uniform(-1, 1, num_samples)

        dati = (self.volume * onda).astype(np.float32).tobytes()
        return dati

    # Avvia la riproduzione dell'audio
    def avvia(self):
        p = pyaudio.PyAudio()
        # Utilizziamo un sample rate fisso a 44100 per lo stream
        self.audio_stream = p.open(format=pyaudio.paFloat32, channels=1, rate=44100,
                                   output=True, stream_callback=self.callback)
        self.playing = True

    # Ferma la riproduzione dell'audio
    def ferma(self):
        if self.audio_stream is not None:
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.playing = False

    # Callback per generare i dati audio in base alla forma d'onda selezionata
    def callback(self, in_data, frame_count, time_info, status):
        sr = 44100
        if self.forma_onda == 'Seno':
            onda = np.sin(2 * np.pi * np.arange(frame_count) * self.frequenza / sr)
        elif self.forma_onda == 'Quadrata':
            onda = np.sign(np.sin(2 * np.pi * np.arange(frame_count) * self.frequenza / sr))
        elif self.forma_onda == 'Triangolare':
            onda = np.abs(2 * (np.arange(frame_count) * self.frequenza / sr - 
                               np.floor(0.5 + np.arange(frame_count) * self.frequenza / sr)))
        elif self.forma_onda == 'Dente di sega':
            onda = 2 * (np.arange(frame_count) * self.frequenza / sr - 
                        np.floor(0.5 + np.arange(frame_count) * self.frequenza / sr))
        else:
            onda = np.random.uniform(-1, 1, frame_count)

        dati = (self.volume * onda).astype(np.float32).tobytes()
        return (dati, pyaudio.paContinue)

# Classe principale dell'applicazione
class AppGeneratoreAudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.generatori = []  # Lista dei generatori audio
        self.inizializza_ui()
        self.setWindowTitle("Generatore Triplo di Onde Multiple")

    # Inizializza l'interfaccia utente
    def inizializza_ui(self):
        widget_centrale = QWidget()
        self.setCentralWidget(widget_centrale)

        layout = QVBoxLayout()
        widget_centrale.setLayout(layout)

        # Aggiungi il titolo nella parte superiore con testo bianco e sfondo indaco
        etichetta_titolo = QLabel("Generatore Triplo di Onde Multiple")
        etichetta_titolo.setStyleSheet("font-size: 20px; color: white; padding: 10px; background-color: indigo;")
        layout.addWidget(etichetta_titolo)

        for i in range(3):
            generatore = GeneratoreAudio(i)
            self.generatori.append(generatore)

            etichetta_stato = QLabel(f"Generatore {i+1}: FERMO")
            layout.addWidget(etichetta_stato)
            generatore.status_label = etichetta_stato

            # Slider per la frequenza
            slider_frequenza = QSlider(Qt.Horizontal)
            slider_frequenza.setMinimum(20)
            slider_frequenza.setMaximum(2000)
            slider_frequenza.valueChanged.connect(lambda val, idx=i: self.aggiorna_frequenza(idx, val))
            layout.addWidget(slider_frequenza)

            # Slider per il volume
            slider_volume = QSlider(Qt.Horizontal)
            slider_volume.setMinimum(0)
            slider_volume.setMaximum(10)
            slider_volume.valueChanged.connect(lambda val, idx=i: self.aggiorna_volume(idx, val))
            layout.addWidget(slider_volume)

            # ComboBox per selezionare la forma d'onda
            combo_forma = QComboBox()
            combo_forma.addItems(['Seno', 'Quadrata', 'Triangolare', 'Dente di sega', 'Casuale'])
            combo_forma.currentIndexChanged.connect(lambda indice, idx=i: self.cambia_forma_onda(idx, indice))
            layout.addWidget(combo_forma)

            pulsante_avvia = QPushButton("Avvia")
            pulsante_avvia.clicked.connect(lambda stato, idx=i: self.avvia_generazione_audio(idx))
            layout.addWidget(pulsante_avvia)

            pulsante_ferma = QPushButton("Ferma")
            pulsante_ferma.clicked.connect(lambda stato, idx=i: self.ferma_generazione_audio(idx))
            layout.addWidget(pulsante_ferma)

            pulsante_ripristina = QPushButton("Ripristina")
            pulsante_ripristina.clicked.connect(lambda stato, idx=i: self.ripristina_impostazioni(idx))
            layout.addWidget(pulsante_ripristina)

            pulsante_salva = QPushButton("Salva")
            pulsante_salva.clicked.connect(lambda stato, idx=i: self.salva_audio(idx))
            layout.addWidget(pulsante_salva)

        self.show()

    # Avvia la riproduzione dell'audio per un generatore specifico
    def avvia_generazione_audio(self, idx):
        generatore = self.generatori[idx]
        generatore.avvia()
        generatore.status_label.setText(f"Generatore {idx+1}: AVVIATO")

    # Ferma la riproduzione dell'audio per un generatore specifico
    def ferma_generazione_audio(self, idx):
        generatore = self.generatori[idx]
        generatore.ferma()
        generatore.status_label.setText(f"Generatore {idx+1}: FERMO")

    # Ripristina le impostazioni predefinite per un generatore specifico
    def ripristina_impostazioni(self, idx):
        generatore = self.generatori[idx]
        generatore.frequenza = 440.0
        generatore.volume = 0.5
        generatore.forma_onda = 'Seno'
        generatore.status_label.setText(f"Generatore {idx+1}: FERMO")

    # Salva l'audio generato in un file WAV per un generatore specifico
    def salva_audio(self, idx):
        generatore = self.generatori[idx]
        wf = wave.open(f"audio_{idx}.wav", "wb")
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(44100)
        dati_audio = generatore.genera_audio(3)
        wf.writeframes(dati_audio)
        wf.close()

    # Aggiorna la frequenza per un generatore specifico
    def aggiorna_frequenza(self, idx, valore):
        generatore = self.generatori[idx]
        generatore.frequenza = valore

    # Aggiorna il volume per un generatore specifico
    def aggiorna_volume(self, idx, valore):
        generatore = self.generatori[idx]
        generatore.volume = valore / 10

    # Cambia la forma d'onda per un generatore specifico
    def cambia_forma_onda(self, idx, indice):
        generatore = self.generatori[idx]
        if indice == 0:
            generatore.forma_onda = 'Seno'
        elif indice == 1:
            generatore.forma_onda = 'Quadrata'
        elif indice == 2:
            generatore.forma_onda = 'Triangolare'
        elif indice == 3:
            generatore.forma_onda = 'Dente di sega'
        else:
            generatore.forma_onda = 'Casuale'

# Funzione principale per avviare l'applicazione
def main():
    app = QApplication(sys.argv)
    finestra = AppGeneratoreAudio()
    sys.exit(app.exec_())

# Punto d'ingresso dell'applicazione
if __name__ == '__main__':
    main()
