import asyncio

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button
from textual.worker import Worker
from tft import ActiveTrait, Champion, Solution, Team, Trait

from tftui.solutions import Solutions, cost_to_color
from tftui.widgets import (
    ChampionButton,
    LevelLabel,
    Loading,
    MinusLevelButton,
    PlusLevelButton,
    TriggerButton,
)

CHAMPIONS = sorted(Champion)
DEFAULT_LEVEL = 7
MIN_LEVEL = 1
MAX_LEVEL = 13


class TraitTracker(App[None]):
    CSS = """
    #left {
        width: 50%;
        layout: grid;
        grid-size: 6 10;
    }

    #right {
       width: 50%;
    }

    #controls {
      height: 5%;
      margin: 1 5;

    }

    .box {
        height: 100%;
        width: 100%;
        margin: 1 1;
    }

    .control {
      width: 1fr;
    }

    Button {
      border: none;
    }

    Vertical {
      height:100%;
    }
    """

    worker: Worker[None] | None = None
    level = DEFAULT_LEVEL

    def compose(self) -> ComposeResult:
        self.output = VerticalScroll()
        self.buttons: list[ChampionButton] = []

        for champ in CHAMPIONS:
            button = ChampionButton(champ, classes="box")
            button.styles.background = cost_to_color[champ.cost]
            self.buttons.append(button)

        self.trigger = TriggerButton("Start", id="trigger", classes="control")
        self.level_label = LevelLabel(str(self.level), classes="control", id="level")
        self.level_label.styles.content_align_horizontal = "center"

        self.loading = Loading(id="loading", classes="control")
        controls = Horizontal(
            self.trigger,
            self.loading,
            MinusLevelButton("-", classes="control"),
            self.level_label,
            PlusLevelButton("+", classes="control"),
            id="controls",
        )
        left = Container(*self.buttons, id="left")
        right = Container(
            Vertical(
                controls,
                self.output,
            ),
            id="right",
        )
        self.container = Horizontal(
            left,
            right,
            id="horizontal",
        )
        yield self.container

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        button = event.button
        match button:
            case ChampionButton():
                if self.worker and not self.worker.is_cancelled:
                    self.worker.cancel()
                button.toggle()
                self.trigger.stop()
                self.loading.hide()

            case TriggerButton():
                if self.worker and not self.worker.is_cancelled:
                    self.worker.cancel()

                if button.toggle():
                    self.start()
                    self.loading.show()
                else:
                    self.loading.hide()

            case PlusLevelButton():
                if self.level < MAX_LEVEL:
                    self.level += 1
                    self.level_label.update(str(self.level))

            case MinusLevelButton():
                if self.level > MIN_LEVEL:
                    self.level -= 1
                    self.level_label.update(str(self.level))
            case _:
                pass

    def get_champions(self) -> list[Champion]:
        names = [button.champion for button in self.buttons if button.selected]
        return names

    def start(self):
        self.output.remove_children()
        self.loading.show()
        champions = self.get_champions()
        team = Team(champions)
        self.worker = self.run_worker(
            self.find_champ_solutions_and_update_rust(team), exclusive=True
        )

    async def find_champ_solutions_and_update(self, team: Team) -> None:
        """Find champions and update the UI after each iteration."""
        solutions: Solutions = Solutions([])
        try:
            async for solution in team.async_find_champs(level=self.level):
                solutions.solutions.append(solution)
                self.output.remove_children()
                # We always show the cheapest solution at the top
                self.output.mount(*solutions.order_solutions().get_flattened_labels())
        except asyncio.CancelledError:
            print("find_champ_solutions_and_update was cancelled.")
            raise  # Re-raise the exception to allow proper cancellation flow
        finally:
            self.loading.hide()
            self.trigger.stop()

    async def find_champ_solutions_and_update_rust(self, team: Team) -> None:
        """Find champions and update the UI after each iteration."""
        solutions: Solutions = Solutions([])
        async for solution in team.find_champs_rust(level=self.level):
            active_traits = {
                ActiveTrait(Trait[trait.trait_.name], level=trait.level)
                for trait in solution.traits
            }
            print(solution.champions)
            champions = {Champion[champ.name] for champ in solution.champions}
            missing_champions = {
                Champion[champ.name] for champ in solution.missing_champions
            }

            solution = Solution(
                champions=champions,
                missing_champions=missing_champions,
                traits=active_traits,
            )
            # solution.champions
            solutions.solutions.append(solution)
            self.output.remove_children()
            # We always show the cheapest solution at the top
            self.output.mount(*solutions.order_solutions().get_flattened_labels())
            await asyncio.sleep(0)
        self.loading.hide()
        self.trigger.stop()
