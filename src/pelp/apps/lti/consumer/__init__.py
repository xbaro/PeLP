import lti_toolbox.lti
from .base import BaseConsumer
from .canvas import CanvasConsumer
from .uoc import UOCConsumer
from .moodle import MoodleConsumer


def get_consumer_from_request(lti_request: lti_toolbox.lti.LTI):
    if not lti_request.is_valid:
        return None

    # Get the consumer
    properties = BaseConsumer.get_consumer_properties(lti_request)

    if properties.source == 0:  # UOC Campus
        return UOCConsumer(properties, lti_request)
    elif properties.source == 1:  # Moodle
        return MoodleConsumer(properties, lti_request)
    elif properties.source == 2:  # Canvas
        return CanvasConsumer(properties, lti_request)

    return None


__all__ = {
    "get_consumer_from_request",
    "BaseConsumer",
}
