from textual.widgets import Button, Label, LoadingIndicator
from tft import Champion


class Loading(LoadingIndicator):
    def __init__(self, id: str | None = None, classes: str | None = None):
        super().__init__(id=id, classes=classes)
        self.styles.opacity = 0

    def hide(self):
        self.styles.opacity = 0

    def show(self):
        self.styles.opacity = 1


class MinusLevelButton(Button):
    pass


class PlusLevelButton(Button):
    pass


class LevelLabel(Label):
    pass


class TriggerButton(Button):
    running = False

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()
        return self.running

    def start(self):
        self.running = True
        self.label = "Stop"

    def stop(self):
        self.running = False
        self.label = "Start"


class ChampionButton(Button):
    def __init__(
        self, champion: Champion, id: str | None = None, classes: str | None = None
    ):
        self.champion = champion
        super().__init__(label=champion.name, id=id, classes=classes)

    selected: bool = False

    def toggle(self):
        self.selected = not self.selected
        self.styles.opacity = 0.5 if self.selected else 1.0
