import threading
from sklearn.utils import shuffle
import numpy as np
import os


class ThreadSafeIter:
    """
    Takes an iterator/generator and makes it thread-safe by
    serializing call to the `next` method of given iterator/generator.
    """

    def __init__(self, iterator):
        self.it = iterator
        self.lock = threading.Lock()

    def __iter__(self):
        return self

    def __next__(self):
        with self.lock:
            return next(self.it)


def get_objects_i(objects_count):
    """
    Cyclic generator of paths indices
    """
    current_objects_id = 0
    while True:
        yield current_objects_id
        current_objects_id = (current_objects_id + 1) % objects_count


class SpectrogramGenerator:

    def __init__(self, folder_path: str, batch_size: int = 16):
        self.folder_path = folder_path
        self.filenames = os.listdir(self.folder_path)
        self.data = shuffle(self.filenames)

        self.batch_size = batch_size

        self.objects_id_generator = ThreadSafeIter(get_objects_i(len(self.data)))

        self.lock = threading.Lock()  # mutex for input path
        self.yield_lock = threading.Lock()  # mutex for generator yielding of batch
        self.init_count = 0

    def get_audio_sample(self):
        pass

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        while True:

            self.batch_data = []
            for obj_id in self.objects_id_generator:
                curr_data_x, curr_data_mask, curr_data_y = self.data[obj_id]

                # augmentation

                curr_data_x = np.expand_dims(curr_data_x, 0)
                curr_data_mask = ...
                curr_data_y = ...

                # here we may apply some augmentations

                # Concurrent access by multiple threads to the lists below
                with self.yield_lock:
                    if len(self.batch_data) < self.batch_size:
                        self.batch_data.append((curr_data_x, curr_data_mask, curr_data_y))

                    if len(self.batch_data) % self.batch_size == 0:
                        # self.batch_data = np.concatenate(self.batch_data, axis=0)
                        batch_x = np.concatenate(([a[0] for a in self.batch_data]), axis=0)
                        batch_mask = np.concatenate(([a[1] for a in self.batch_data]), axis=0)
                        batch_y = np.concatenate(([a[2] for a in self.batch_data]), axis=0)

                        yield batch_x, batch_mask, batch_y
                        self.batch_data = []

    # def __next__(self):
    #     self.batch_data = []
    #     filename = self.data[next(self.objects_id_generator)]
    #     with self.yield_lock:
    #         if len(self.batch_data) < self.batch_size:
    #             self.batch_data.append((curr_data_x, curr_data_mask, curr_data_y))
    #
    #         if len(self.batch_data) % self.batch_size == 0:
    #             # self.batch_data = np.concatenate(self.batch_data, axis=0)
    #             batch_x = np.concatenate(([a[0] for a in self.batch_data]), axis=0)
    #             batch_mask = np.concatenate(([a[1] for a in self.batch_data]), axis=0)
    #             batch_y = np.concatenate(([a[2] for a in self.batch_data]), axis=0)
    #
    #             yield batch_x, batch_mask, batch_y
    #             self.batch_data = []