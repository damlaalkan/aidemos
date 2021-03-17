import glob
import azure.cognitiveservices.speech as speechsdk
import time
import json
import pandas as pd

# Create a config file with your own configuration
# config_file_dev.json has my dev config
config_file_name = "config_file_dev.json"

with open(config_file_name, 'r') as json_data_file:
    configuration = json.load(json_data_file)

# Speech SDK and File Location, entered in json file
speech_key = configuration["speech_api"]["speech_key"]
service_region = configuration["speech_api"]["service_region"]
location = configuration["location"]["full_file_path"]
print("service_region: " + service_region)
speech_key, service_region = speech_key, service_region
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

print ("PROGRAM START")
tic = time.perf_counter()
print ("####################################################################################")

def speech_recognize_continuous_from_file(file):
    """performs continuous speech recognition with input from an audio file"""
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    audio_config = speechsdk.audio.AudioConfig(filename=file)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
    done = False
    def stop_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True
    all_results = []
    def handle_final_result(evt):
        all_results.append(evt.result.text)
    speech_recognizer.recognized.connect(handle_final_result)
    # Connect callbacks to the events fired by the speech recognizer
    #speech_recognizer.recognizing.connect(lambda evt: print('RECOGNIZING: {}'.format(evt)))
    speech_recognizer.recognized.connect(lambda evt: print('RECOGNIZED: {}'.format(evt)))
    speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)
    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.5)
    print("Printing all results:")
    print(all_results)
    df = pd.DataFrame(all_results)
    df
    file_name = file + r"-speech-to-text-csv-output.csv"
    df.to_csv(file_name)
    print ("Audio File: "+file+" converted successfully")

# Defines the files locations and list audio files (*.wav)
location = location
fileset = [file for file in glob.glob(location + "**/*.wav", recursive=True)]

# Loop to call function to convert audio files to text
for file in fileset:
    #run_speech_to_text_small_audio_files(file)
    speech_recognize_continuous_from_file(file)
    print(file)
print ("PROGRAM END")
toc = time.perf_counter()
print(f"Converted speech to text in {toc - tic:0.4f} seconds")
print ("####################################################################################")
