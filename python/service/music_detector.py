import io
import csv
import logging
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cache_lock = threading.Lock()


class MusicDetector:
    def __init__(self):
        try:
            from tflite_runtime.interpreter import Interpreter
            self.interpreter = Interpreter('./ml-model/1.tflite')
        except ModuleNotFoundError:
            import tensorflow as tf
            self.interpreter = tf.lite.Interpreter('./ml-model/1.tflite')
        self.recording_duration = 10
        self.final_sample_rate = 16000
        self.recording_sample_rate = 44100
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.waveform_input_index = self.input_details[0]['index']
        self.scores_output_index = self.output_details[0]['index']
        self.embeddings_output_index = self.output_details[1]['index']
        self.spectrogram_output_index = self.output_details[2]['index']
        self.interpreter.resize_tensor_input(self.waveform_input_index,
                                             [self.recording_duration * self.final_sample_rate], strict=True)
        self.interpreter.allocate_tensors()

        self.class_names = None
        with open('./ml-model/yamnet_class_map.csv') as csv_file:
            class_map_csv = io.StringIO(csv_file.read())
            self.class_names = [display_name for (class_index, mid, display_name) in csv.reader(class_map_csv)]
            self.class_names = self.class_names[1:]  # Skip header

    def is_audio_music(self, waveform):
        self.interpreter.set_tensor(self.waveform_input_index, waveform)
        self.interpreter.invoke()

        scores = self.interpreter.get_tensor(self.scores_output_index)
        scores_mean = scores.mean(axis=0)
        top_i = scores_mean.argmax()

        # if the highest probability is assigned to Music with a confidence of more than 20 %
        return 'Music' in self.class_names[top_i] and scores_mean[top_i] > 0.2
