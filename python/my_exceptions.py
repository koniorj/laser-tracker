# This exception will never be thrown, because Iriun creates a dummy footage. 
# We should either delete this exception or create a helper function, which will
# analyze the message that Iriun shows us on live video footage (preferred).
class NoCameraFootage(Exception):
    """Exception raised when camera stream is inaccessible."""

    def __init__(self, camera_index: int):
        self.camera_index = camera_index
        super().__init__(f"No footage accessible from camera with index: {camera_index}")


