

class ProcessingBreak(Exception):
    """ Exception raised to break processing flow with a specific message.
    """
    
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message

