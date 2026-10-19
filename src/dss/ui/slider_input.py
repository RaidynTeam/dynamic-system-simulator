"""Float presentation around Qt's integer slider; no calculation dependencies."""

from math import isfinite, log10

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget


class SliderInput(QWidget):
    valueChanged = Signal(float)
    valueRejected = Signal(str)

    def __init__(self, name: str, value: float, *, logarithmic: bool = False, caption: str = ""):
        super().__init__(objectName=name)
        self.logarithmic = logarithmic
        self.lower, self.upper = (1e-6, 10.0) if logarithmic else (0.01, 20.0)
        self.slider = QSlider(Qt.Orientation.Horizontal, objectName=f"{name}_slider")
        if logarithmic:
            self.slider.setRange(0, 1400)
        else:
            self.slider.setRange(1, 2000)
        self.slider.setAccessibleName(f"{name} {'logarithmic' if logarithmic else 'coefficient'} slider")
        self.slider.setPageStep(20 if logarithmic else 100)
        self.readout = QLabel(objectName=f"{name}_value")
        self.readout.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        heading = QHBoxLayout()
        heading.addWidget(QLabel(caption or name))
        heading.addStretch()
        heading.addWidget(self.readout)
        layout.addLayout(heading)
        self.slider.setFixedHeight(18)
        layout.addWidget(self.slider)
        self.setToolTip(
            "Range: 0.000001–10 s; logarithmic thumb, 200 ticks per decade. "
            "Auto and ×2/÷2 retain their exact value between thumb ticks."
            if logarithmic else "Range: 0.01–20.00; each integer slider tick represents 0.01."
        )
        self._value = value
        self.setValue(value)
        self.slider.valueChanged.connect(self._from_slider)

    def value(self) -> float:
        return self._value

    def _from_slider(self, position: int) -> None:
        value = 10 ** (-6 + position / 200) if self.logarithmic else position / 100
        self.setValue(value)

    def setValue(self, value: float) -> bool:
        """Reject out-of-range requests; never silently clamp or round input."""
        if not isfinite(value) or not self.lower <= value <= self.upper:
            self.valueRejected.emit(
                f"{self.objectName()} must be within {self.lower:g}–{self.upper:g}; "
                "the previous value was kept."
            )
            return False
        position = round((log10(value) + 6) * 200) if self.logarithmic else round(value * 100)
        if not self.logarithmic and abs(position / 100 - value) > 1e-12:
            self.valueRejected.emit(f"{self.objectName()} requires increments of 0.01; the previous value was kept.")
            return False
        changed = value != self._value
        self._value = value
        blocked = self.slider.blockSignals(True)
        self.slider.setValue(position)
        self.slider.blockSignals(blocked)
        formatted = f"{value:.4f}" if value >= 0.001 else f"{value:.3g}"
        self.readout.setText(f"{formatted} s" if self.logarithmic else f"{value:.2f}")
        self.readout.setToolTip(f"Full value: {value:.17g}")
        self.slider.setAccessibleDescription(f"{value:.17g}")
        if changed:
            self.valueChanged.emit(value)
        return True
