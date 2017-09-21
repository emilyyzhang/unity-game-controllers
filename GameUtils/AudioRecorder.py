"""
This is a helper class that handles the audio recording and sending it to SpeechAce
"""
# -*- coding: utf-8 -*-
# pylint: disable=import-error, wrong-import-order

import _thread as thread
import binascii
import json
import subprocess
import time
import wave
import math
import pyaudio
from six.moves import queue

from GameUtils import GlobalSettings
from GameUtils import ROSUtils

if GlobalSettings.USE_ROS:
    import rospy
    from r1d1_msgs.msg import AndroidAudio
else:
    TapGameLog = GlobalSettings.TapGameLog #Mock object, used for testing in non-ROS environments
    TapGameCommand = GlobalSettings.TapGameCommand


class AudioRecorder:
    """
    Helper class that handles audio recording, converting to wav, and sending to SpeechAce
    """

    # CONSTANTS
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000

    CHUNK = 16000
    ANDROID_MIC_TO_ROS_TOPIC = 'android_audio'

    EXTERNAL_MIC_NAME = 'USB audio CODEC: Audio (hw:1,0)'


    def __init__(self, participant_id='p00', experimenter_id='Leo'):
        # True if the phone is currently recording
        self.is_recording = False

        # Holds the audio data that turns into a wav file
        # Needed so that the data will be saved when recording audio in the new thread
        self.buffered_audio_data = []

        # 0 if never recorded before, odd if is recording, even if finished recording
        self.has_recorded = 0

        # Audio Subscriber node
        self.sub_audio = None

        # True if actually recorded from android audio
        # False so that it doesn't take the last audio data
        # Without this it won't send a pass because it didn't hear you message 
        self.valid_recording = True

        # placeholder variable so we can see how long we recorded for
        self.start_recording_time = 0

        #
        self.participant_id = participant_id
        self.experimenter_id = experimenter_id
        self.WAV_OUTPUT_FILENAME_PREFIX = 'GameUtils/PronunciationUtils/data/recordings/' + self.participant_id + '_' + self.experimenter_id + '_'
        self.expected_text = None #this dynamically updates each time start_recording is called. It is the current word we expect to be recording


    def audio_data_generator(self, buff, buffered_audio_data):
        """
        Takes the buffer and adds it to the list data.
        Stops recording after self.isRecording becomes False
        """

        while True:
            if self.is_recording is False:
                self.sub_audio.unregister()  # Unregisters from topic when not recording
                break

            buffered_audio_data += [buff.get()]
        return buffered_audio_data

    def fill_buffer(self, audio_stream, args):
        """
        Callback function for receiving audio data.
        Converts the microphone data from hex to binascii and puts it into a buffer
        """
        buff = args
        buff.put(binascii.unhexlify(audio_stream.data))

    def record_android_audio(self, buffered_audio_data):
        """
        Creates a queue that will hold the audio data
        Subscribes to the microphone to receive data
        Returns the buffered audio data
        """

        #only do the recording if we are actually getting streaming audio data
        if ROSUtils.is_rostopic_present(AudioRecorder.ANDROID_MIC_TO_ROS_TOPIC):
            self.valid_recording = True
            print('Android Audio Topic found, recording!')
            buff = queue.Queue()
            self.sub_audio = rospy.Subscriber(AudioRecorder.ANDROID_MIC_TO_ROS_TOPIC,
                                              AndroidAudio, self.fill_buffer, buff)
            return self.audio_data_generator(buff, buffered_audio_data) #TODO: Return statement necessary?    
        else:
            print('NOT RECORDING, NO ANDROID AUDIO TOPIC FOUND!')
            self.valid_recording = False
            return

    def record_usb_audio(self, record_length):
        mic_index = None
        audio = pyaudio.PyAudio()
        info = audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        #print(numdevices)
        #print("# of devices")

        for i in range(0, numdevices):

            #print(audio.get_device_info_by_host_api_device_index(0, i).get('name'))
            if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                if audio.get_device_info_by_host_api_device_index(0, i).get('name') == self.EXTERNAL_MIC_NAME:
                    mic_index = i
                    break

        if mic_index == None:
            self.valid_recording = False
            print('NOT RECORDING, NO USB AUDIO DEVICE FOUND!')
            pass
        else:
            # start Recording
            self.valid_recording = True            
            print('USB Audio Device found, recording!')
            stream = audio.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK, input_device_index=mic_index)

            frames = []
            # while self.is_recording:
            #     data = stream.read(self.CHUNK)
            #     buffered_audio_data.append(data)
            print(self.RATE)
            print(self.CHUNK)
            print(record_length)
            for i in range(math.ceil((self.RATE / self.CHUNK) * record_length)):
                data = stream.read(self.CHUNK)
                frames.append(data)

            # Stops the recording
            stream.stop_stream()
            stream.close()
        audio.terminate()

        wav_file = wave.open(self.WAV_OUTPUT_FILENAME_PREFIX + self.expected_text + '.wav', 'wb')
        wav_file.setnchannels(AudioRecorder.CHANNELS)
        wav_file.setsampwidth(2)
        wav_file.setframerate(AudioRecorder.RATE)
        wav_file.writeframes(b''.join(frames))
        wav_file.close()
        return

    def speechace(self, audio_file):
        """
        Takes the audiofile and uses the text it is supposed to match; returns a
        score and the time elapsed to calculate the score.
        """
        start_time = time.time()

        # send request to speechace api
        api_command = "curl --form text='" + self.expected_text + "' --form user_audio_file=@" + audio_file + " --form dialect=general_american --form user_id=1234 \"https://api.speechace.co/api/scoring/text/v0.1/json?key=po%2Fc4gm%2Bp4KIrcoofC5QoiFHR2BTrgfUdkozmpzHFuP%2BEuoCI1sSoDFoYOCtaxj8N6Y%2BXxYpVqtvj1EeYqmXYSp%2BfgNfgoSr5urt6%2FPQzAQwieDDzlqZhWO2qFqYKslE&user_id=002\"" # pylint: disable=line-too-long
        process = subprocess.Popen(api_command, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        process.wait()
        pouts = process.stdout.readlines()
        print("RESULT")
        print(pouts)
        out_json = pouts[3]

        elapsed_time = time.time() - start_time
        print("took " + str(elapsed_time) + " seconds to get speechAce results")

        # decode json outputs from speechace api
        try:
            result = json.loads(out_json)['text_score']
            #result_text = result['text']
            #result_qualityScore = result['quality_score']
            result_word_score_list = result['word_score_list']

            return result_word_score_list
        except: #pylint: disable= bare-except
            print("DID NOT GET VALID RESPONSE")
            print(out_json)
            return


    def start_recording(self, expected_text):
        """
        Starts a new thread that records the microphones audio.
        """
        self.expected_text = expected_text
        self.is_recording = True
        self.has_recorded += 1
        self.buffered_audio_data = []  # Resets audio data
        self.start_recording_time = time.time()

        if GlobalSettings.USE_USB_MIC:
            self.record_usb_audio(2.5)
        else: #try to use streaming audio from Android device
            thread.start_new_thread(self.record_android_audio, (self.buffered_audio_data,))
            time.sleep(.1)
        

    def stop_recording(self):
        """
        ends the recording and makes the data into
        a wav file
        """
        self.is_recording = False  # Ends the recording
        self.has_recorded += 1
        time.sleep(.1)  # Gives time to return the data

        #only if we are actually getting streaming audio data
        if len(self.buffered_audio_data) > 0:
            elapsed_time = time.time() - self.start_recording_time
            print("recorded speech for " + str(elapsed_time) + " seconds")
            print('RECORDING SUCCESSFUL, writing to wav')
            wav_file = wave.open(self.WAV_OUTPUT_FILENAME_PREFIX + self.expected_text + '.wav', 'wb')
            wav_file.setnchannels(AudioRecorder.CHANNELS)
            wav_file.setsampwidth(2)
            wav_file.setframerate(AudioRecorder.RATE)
            wav_file.writeframes(b''.join(self.buffered_audio_data))
            wav_file.close()