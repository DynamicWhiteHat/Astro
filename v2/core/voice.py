from yapper import Yapper

class StoppableYapper(Yapper):
    def stop(self):
        try:
            if hasattr(self.speaker, "engine"):
                self.speaker.engine.stop()
        except Exception as e:
            print(f"[WARN] Could not stop speaker: {e}")

speaker = StoppableYapper()
