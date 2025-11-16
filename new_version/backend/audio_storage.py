import os

class AudioStorageManager:
    def __init__(self, storage_path='audio_storage'):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    def delete_audio(self, filepath):
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False