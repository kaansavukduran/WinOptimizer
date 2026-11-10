import math
from functools import lru_cache
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPixmap, QPainter, QCursor
from PySide6.QtWidgets import QWidget, QApplication, QToolTip

PAGE_CLIPS = {'home':('core',0), 'scanFix':('core',1), 'cleanup':('sections',0),
    'drivers':('sections',1), 'hardware':('sections',2), 'startup':('sections',3),
    'workshop':('core',5), 'tools':('sections',4), 'history':('sections',5), 'settings':('core',4)}

@lru_cache(maxsize=4)
def sheets(root):
    return {name:QPixmap(str(root / ('public/assets/aion-'+name+'.png'))) for name in ('pet','optimizer','sections')}

class Aion(QWidget):
    def __init__(self, root, text, page='home', compact=False, parent=None):
        super().__init__(parent)
        self.text = text
        assets = sheets(root)
        self.pet, self.core, self.sections = assets['pet'], assets['optimizer'], assets['sections']
        self.page, self.base_size = page, 112 if compact else 170
        self.preferences = {}
        self.state, self.frame, self.direction, self.pet_until, self.paused = 'idle', 0, 8, 0, False
        self.elapsed, self.pet_row = 0, 3
        self.gaze_until, self.last_pointer = 0, None
        self.setAccessibleName(text('pet'))
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(120)
        self.configure({})

    def configure(self, settings):
        self.preferences = settings
        size = int(self.base_size * settings.get('mascotSize', 100) / 100 * settings.get('scale', 100) / 100)
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
        if not self.isVisible() or self.visibleRegion().isEmpty() or not self.window().isActiveWindow():
            return
        self.elapsed += 120
        if self.state == 'celebrate' and self.elapsed >= 1440:
            self.state, self.elapsed, self.frame = 'idle', 0, 0
        if not self.motion():
            self.update()
            return
        self.frame += 1
        if self.state == 'idle' and self.preferences.get('followPointer', True) and self.pet_until <= self.elapsed:
            point = self.mapFromGlobal(QCursor.pos())
            pointer = (QCursor.pos().x(), QCursor.pos().y())
            if pointer != self.last_pointer and self.window().rect().contains(self.window().mapFromGlobal(QCursor.pos())):
                dx, dy = point.x() - self.width() / 2, point.y() - self.height() / 2
                if math.hypot(dx / max(1, self.width()), dy / max(1, self.height())) > .15:
                    self.direction = round((math.atan2(dy, dx) + math.pi / 2) / (2 * math.pi) * 16) % 16
                    self.gaze_until = self.elapsed + 840
            self.last_pointer = pointer
        self.update()

    def set_state(self, state):
        self.state, self.elapsed, self.frame = state, 0, 0
        self.update()

    def frame_source(self):
        if self.pet_until > self.elapsed:
            count = 5 if self.pet_row == 4 else 4
            row, col, sheet, cell = self.pet_row, (self.frame // 2) % count if self.motion() else 0, self.pet, (192, 208)
        elif self.state == 'idle' and self.motion() and self.gaze_until > self.elapsed:
            row, col, sheet, cell = 9 + self.direction // 8, self.direction % 8, self.pet, (192, 208)
        else:
            source, row = PAGE_CLIPS.get(self.page, PAGE_CLIPS['home'])
            if self.state in ('repair','celebrate','help','game'):
                source, row = 'core', {'repair':2,'celebrate':3,'help':4,'game':5}[self.state]
            elif self.state == 'read' and source == 'core':
                row = 1
            sheet, cell = self.sections if source == 'sections' else self.core, (256,256)
            col = min(3,self.elapsed//360) if self.state=='celebrate' else (self.elapsed//360)%4
            if not self.motion():col = 0
        return sheet, QRect(col * cell[0], row * cell[1], *cell), cell

    def paintEvent(self, _):
        sheet, source, cell = self.frame_source()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        ratio = min(self.width() / cell[0], self.height() / cell[1])
        w, h = int(cell[0] * ratio), int(cell[1] * ratio)
        painter.drawPixmap(QRect((self.width() - w) // 2, self.height() - h, w, h), sheet, source)

    def hideEvent(self, event):
        self.timer.stop()
        super().hideEvent(event)

    def showEvent(self, event):
        self.timer.start(120)
        super().showEvent(event)

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
