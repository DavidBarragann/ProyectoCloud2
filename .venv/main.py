import azure.cognitiveservices.speech as speechsdk
import os
from dotenv import load_dotenv
from azure.ai.translation.text import TextTranslationClient
from azure.core.credentials import AzureKeyCredential

def create_text_translation_client():
    apikey = '7mKLeLUJ9BJTqOzUxyqwckNy4QvAzILgFLV8gNjhx5jKDtAi09RRJQQJ99BCACYeBjFXJ3w3AAAbACOGBJcA'
    region = 'eastus'
    # [START create_text_translation_client_with_credential]
    credential = AzureKeyCredential(apikey)
    text_translator = TextTranslationClient(credential=credential, region=region)
    # [END create_text_translation_client_with_credential]
    return text_translator

def speak_to_microphone(API_KEY, region):
    speech_config = speechsdk.SpeechConfig(subscription=API_KEY, region=region)
    speech_config.speech_synthesis_language = "es-ES"
    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # Configurar timeout
    speech_recognizer.properties.set_property(speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs,
                                              "60000")  # 60 segundos
    speech_recognizer.properties.set_property(speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs,
                                              "20000")  # 20 segundos

    print("Habla al micrófono para iniciar la traducción, di 'End session' para terminar")

    texto_acumulado = ""  # Variable para acumular el texto reconocido

    while True:
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Se reconoció: {}".format(speech_recognition_result.text))
            texto_acumulado += speech_recognition_result.text + " "  # Acumular el texto

            if "End session" in speech_recognition_result.text:
                print("Sesión finalizada por el usuario, iniciando traducción")
                texto_acumulado = texto_acumulado.replace("End session", "").strip()  # Remover 'End session'
                return texto_acumulado

        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            print("No se reconoció ningún discurso para traducir")
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            print("Reconocimiento de voz cancelado: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Detalles del error: {}".format(cancellation_details.error_details))
                print("Revisa tus credenciales.")


def traducir_texto(text_translator, texto, API_KEY):
    # Configurar el servicio de voz
    speech_config = speechsdk.SpeechConfig(subscription=API_KEY, region='eastus')
    # Establecer la voz de AvaMultilingual
    speech_config.speech_synthesis_voice_name = 'en-US-AvaMultilingualNeural'

    # Configurar la salida de audio
    synth_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

    # Crear el sintetizador de voz
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=synth_output_config)

    print(f"Traduciendo el texto: {texto}")

    try:
        # Realizar la traducción a inglés y alemán
        response = text_translator.translate(
            body=[texto],
            to_language=["en", "de"],  # Traducción a inglés y alemán
            from_language="es"  # Idioma del texto original
        )

        # Procesar la respuesta de traducción
        for translation in response:
            detected_language = translation.detected_language
            if detected_language:
                print(
                    f"El idioma detectado es: {detected_language.language} con un puntaje de confianza de: {detected_language.score}.")

            for translated_text in translation.translations:
                print(f"Texto traducido a {translated_text.to}: '{translated_text.text}'.")

                # Sintetizar el texto traducido
                speech_synthesis_result = speech_synthesizer.speak_text_async(translated_text.text).get()

                # Verificar si la síntesis de voz fue exitosa
                if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    print(f"Se ha completado la síntesis de voz para el texto: '{translated_text.text}'.")
                else:
                    print(f"Error en la síntesis de voz: {speech_synthesis_result.reason}")
    except Exception as e:
        print(f"Error durante la traducción: {str(e)}")
# Cargar las claves de entorno
load_dotenv()

# Claves y endpoint de Azure
API_KEY = '6JtsnBbBD1vt3NGn1enHJUumR3LmW8suTsQZASQnXtph8tb9hoJCJQQJ99BCACYeBjFXJ3w3AAAYACOGRqV0'
region = 'eastus'

# Crear el cliente de traducción de texto
text_translator = create_text_translation_client()

# Reconocer el texto hablado
texto_reconocido = speak_to_microphone(API_KEY, region)

# Realizar la traducción
if texto_reconocido:
    traducir_texto(text_translator, texto_reconocido,API_KEY)
