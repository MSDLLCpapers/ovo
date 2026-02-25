import random


class ColorPicker:
    def __init__(self, seed: int = 27):
        self.rng = random.Random(seed)
        self.assignedColorsCount = 0
        # modified tab10 palette
        self.prefferedColors = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#9e4634",
            "#e377c2",
            "#bcbd22",
            "#17becf",
            "#6f6f6f",
        ]
        self.assignedValues = []
        self.assignedColorsList = []

    def __call__(self, value):
        if value in self.assignedValues:
            idx = self.assignedValues.index(value)
            return self.assignedColorsList[idx]

        if self.assignedColorsCount < len(self.prefferedColors):
            color = self.prefferedColors[self.assignedColorsCount]
        else:
            r = lambda: self.rng.randint(0, 255)
            color = "#%02X%02X%02X" % (r(), r(), r())

        self.assignedColorsCount += 1
        self.assignedColorsList.append(color)
        self.assignedValues.append(value)
        return color


def mix_colors(first_hex, second_hex):
    return "#" + "".join(
        f"{(int(first_hex[i : i + 2], 16) + int(second_hex[i : i + 2], 16)) // 2:02x}" for i in (1, 3, 5)
    )
