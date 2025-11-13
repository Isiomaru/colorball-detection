from pynput import keyboard

class Inputer(keyboard.Listener):
    def __init__(self,key_queue):
        super().__init__(on_press=self.press,on_release=self.release)
        self.key_queue=key_queue
        self.key_state = {}

    def update_key_queue(self,key):
        if self.key_queue.full():
            self.key_queue.get()
        self.key_queue.put(key)

    def get_key_char(self,key):
        try:
            key_char = key.char  # 文字キー
        except AttributeError:
            key_char = str(key)  # 特殊キー

        return key_char

    def press(self,key):
        key_char = self.get_key_char(key)
        self.key_state[key_char] = True
        self.update_key_queue(self.key_state.copy())

    def release(self, key):
        key_char = self.get_key_char(key)
        self.key_state[key_char] = False
        self.update_key_queue(self.key_state.copy())
