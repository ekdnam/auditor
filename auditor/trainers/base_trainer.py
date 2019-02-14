import logging
from abc import ABC, abstractmethod


class TrainingStep(ABC):
    logger = logging.getLogger(__name__)

    @abstractmethod
    def __init__(self, delay: int):
        self.delay = delay

    @abstractmethod
    def __call__(self, *args, **kwargs):
        pass
