from dataclasses import dataclass
from textual.widgets import Label
from tft import Solution


cost_to_color = {1: "white", 2: "green", 3: "cyan", 4: "purple", 5: "gold"}


def get_labels(solution: Solution, only_missing: bool = True):
    champs = solution.missing_champions if only_missing else solution.champions
    labels: list[Label] = []
    for champ in champs:
        label = Label(str(champ))
        label.styles.color = cost_to_color[champ.cost]
        labels.append(label)
    labels.append(Label(f"{solution.missing_cost}"))
    labels.append(Label(""))
    return labels


def solution_sort_key(solution: Solution):
    return solution.missing_cost


@dataclass
class Solutions:
    solutions: list[Solution]

    def order_solutions(self):
        return Solutions(sorted(self.solutions, key=solution_sort_key))

    def get_labels(self):
        return [get_labels(sol) for sol in self.solutions]

    def get_flattened_labels(self, only_missing: bool = True):
        return [
            label
            for sol in self.solutions
            for label in get_labels(sol, only_missing=only_missing)
        ]
