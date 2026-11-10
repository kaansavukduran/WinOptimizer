import math
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPixmap, QPainter, QCursor
from PySide6.QtWidgets import QWidget, QApplication, QToolTip

class Aion(QWidget):
    def __init__(self, root, text):
        super().__init__()
        self.text = text
        self.pet = QPixmap(str(root / 'public/assets/aion-pet.png'))
        self.core = QPixmap(str(root / 'public/assets/aion-optimizer.png'))
        self.preferences = {}
        self.state, self.frame, self.direction, self.pet_until, self.paused = 'idle', 0, 8, 0, False
        self.elapsed, self.pet_row = 0, 3
        self.setAccessibleName(text('pet'))
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(120)
        self.configure({})

    def configure(self, settings):
        self.preferences = settings
        size = int(170 * settings.get('mascotSize', 100) / 100 * settings.get('scale', 100) / 100)
        self.setFixedSize(size, int(size * 208 / 192))
        self.setVisible(settings.get('companion', True))
        self.update()

    def motion(self):
        reduced = False
        if __import__('sys').platform == 'win32':
            try:
                import ctypes
                enabled = ctypes.c_int(1)
                ctypes.windll.user32.SystemParametersInfoW(0x1042, 0, ctypes.byref(enabled), 0)
                reduced = not bool(enabled.value)
            except (OSError, AttributeError):
                pass
        return self.preferences.get('motion', True) and not self.paused and not reduced

    def tick(self):
        if not self.isVisible() or not self.window().isActiveWindow():
            return
        self.elapsed += 120
        if not self.motion():
            self.update()
            return
        self.frame += 1
        if self.state == 'celebrate' and self.elapsed > 2000:
            self.state = 'idle'
        if self.state in ('idle', 'help', 'game') and self.preferences.get('followPointer', True) and self.pet_until <= self.elapsed:
            point = self.mapFromGlobal(QCursor.pos())
            if self.window().rect().contains(self.window().mapFromGlobal(QCursor.pos())):
                dx, dy = point.x() - self.width() / 2, point.y() - self.height() / 2
                if math.hypot(dx / max(1, self.width()), dy / max(1, self.height())) > .15:
                    self.direction = round((math.atan2(dy, dx) + math.pi / 2) / (2 * math.pi) * 16) % 16
        self.update()

    def set_state(self, state):
        self.state, self.elapsed, self.frame = state, 0, 0
        self.update()

    def paintEvent(self, _):
        if self.pet_until > self.elapsed:
            count = 5 if self.pet_row == 4 else 4
            row, col, sheet, cell = self.pet_row, (self.frame // 2) % count if self.motion() else 0, self.pet, (192, 208)
        elif self.state in ('idle', 'help', 'game'):
            direction = self.direction if self.motion() else 8
            row, col, sheet, cell = 9 + direction // 8, direction % 8, self.pet, (192, 208)
        else:
            row = {'read': 1, 'repair': 2, 'celebrate': 3}.get(self.state, 0)
            row, col, sheet, cell = row, self.frame % 4 if self.motion() else 0, self.core, (256, 256)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        source = QRect(col * cell[0], row * cell[1], *cell)
        ratio = min(self.width() / cell[0], self.height() / cell[1])
        w, h = int(cell[0] * ratio), int(cell[1] * ratio)
        painter.drawPixmap(QRect((self.width() - w) // 2, self.height() - h, w, h), sheet, source)

    def react(self, x=.5, y=.3):
        if not self.preferences.get('petting', True):
            return
        part = 'head' if y < .55 else 'feet' if y > .86 else 'tail' if x < .27 or x > .73 else 'belly'
        self.pet_row, self.pet_until, self.frame = 4 if part == 'feet' else 3, self.elapsed + 1200, 0
        QToolTip.showText(self.mapToGlobal(self.rect().center()), self.text('pet_' + part), self)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.react(event.position().x() / self.width(), event.position().y() / self.height())

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.react()
        else:
            super().keyPressEvent(event)
