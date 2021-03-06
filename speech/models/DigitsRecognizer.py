import numpy as np

from speech.models.model_utils import label_from_sparse_tensor


class DigitsRecognizer(object):
    def __init__(self, model, sess):
        self._model = model
        self._sess = sess

    def recognize(self, features, raw=False):
        """
        Translates MFCC features/raw audio of spoken digits to a string of the digits. ASR

        :param features: The MFCC features of an audio sample of a person saying a string of digits
        :param raw: If False, we are using MFCC features.
        :return: digit
        """
        seq_len = np.array([features.shape[0]])
        input_features = np.expand_dims(features, axis=0)
        input_feed = self._model.create_feed_dict(input_features, seq_len)
        digits = label_from_sparse_tensor(
            self._sess.run(self._model.decoded_sequence, input_feed)
        )
        return digits
