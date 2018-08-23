from abc import ABC, abstractmethod

class AbstractDetector(ABC):

    # constructor
    @abstractmethod
    def __init__(self):
        pass 

    @abstractmethod
    def build_graph(self):
        pass

    @abstractmethod
    def load_weights(self, path):
        pass

    @abstractmethod
    def detect(self, frame):
        pass
