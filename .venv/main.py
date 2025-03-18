import azure.cognitiveservices.speech as speechsdk
import os
import io
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play
import pygame

# Ruta del audio
video = 'C:/Users/david/Downloads/audioejemplo.wav'
print("Reproduciendo audio original...")

pygame.mixer.init()

# Cargar el archivo de audio
pygame.mixer.music.load(video)

# Reproducir
pygame.mixer.music.play()

# Mantener el programa corriendo mientras se reproduce el audio
while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)

# Claves y endpoint de Azure
API_KEY = '6JtsnBbBD1vt3NGn1enHJUumR3LmW8suTsQZASQnXtph8tb9hoJCJQQJ99BCACYeBjFXJ3w3AAAYACOGRqV0'
endpoint = 'https://eastus.api.cognitive.microsoft.com/'

# Configuración de traducción de voz
translation_config = speechsdk.translation.SpeechTranslationConfig(
    subscription=API_KEY, region="eastus")

translation_config.speech_recognition_language = 'es-MX'
translation_config.add_target_language('en')
speech_config = speechsdk.SpeechConfig(subscription=API_KEY, region='eastus')

# Configuración de audio
audio_config = speechsdk.audio.AudioConfig(filename=video)
synth_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

# Configuración de voz
translation_config.speech_synthesis_voice_name = 'en-US-AvaMultilingualNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=synth_output_config)

# Reproducir el audio original antes de la transcripción
print("Realizando la traducción")

# Inicialización del reconocedor de traducción
recognizer = speechsdk.translation.TranslationRecognizer(
    translation_config=translation_config, audio_config=audio_config)

# Reconocimiento de audio y traducción
result = recognizer.recognize_once()

# Manejo de errores y resultados
if result.reason == speechsdk.ResultReason.TranslatedSpeech:
    source_language_text = result.text
    print(f"Texto en español: {source_language_text}")
    print(f"Traducción al inglés: {result.translations['en']}")

    # Síntesis de voz del texto traducido
    speech_synthesis_result = speech_synthesizer.speak_text_async(result.translations['en']).get()

elif result.reason == speechsdk.ResultReason.NoMatch:
    print("No se reconoció ningún discurso.")
elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print(f"Traducción cancelada: {cancellation_details.reason}")
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        print(f"Error: {cancellation_details.error_details}")
