import speech_recognition as sr
import pyaudio

init_rec = sr.Recognizer()

with sr.Microphone() as source:
    while True:
        try:
            # wait for a second to let the recognizer
            # adjust the energy threshold based on
            # the surrounding noise level
            init_rec.adjust_for_ambient_noise(source, duration=0.2)
            
            audio_data = init_rec.record(source, duration=2)
            text = init_rec.recognize_google(audio_data)
            if "restart" in text:
                print("restart")

        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
         
        except sr.UnknownValueError:
            print("unknown error occurred")