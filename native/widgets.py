import math
from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QTextBlockFormat, QTextCursor
from PySide6.QtWidgets import QTextEdit, QSizePolicy, QFrame

class Paragraph(QTextEdit):
    """Plain native text with real line-height, wrapping and selection; no web engine."""
    def __init__(self, value, line_height=1.5):
        super().__init__()
        self.setReadOnly(True)
        self.setPlainText(value)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet('QTextEdit { background: transparent; padding: 0; }')
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum)
        self.document().setDocumentMargin(1)
        cursor=self.textCursor();cursor.select(QTextCursor.Document)
        block=QTextBlockFormat();block.setLineHeight(line_height*100,QTextBlockFormat.ProportionalHeight.value)
        cursor.mergeBlockFormat(block)
        self.fit_timer=QTimer(self)
        self.fit_timer.setSingleShot(True)
        self.fit_timer.timeout.connect(self.fit)
        self.document().documentLayout().documentSizeChanged.connect(self.queue_fit)
        self.queue_fit()

    @Slot()
    def queue_fit(self,*_):
        self.fit_timer.start(0)

    @Slot()
    def fit(self):
        height=max(24,math.ceil(self.document().size().height())+6)
        if self.minimumHeight()!=height or self.maximumHeight()!=height:self.setFixedHeight(height)

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.document().setTextWidth(max(40,self.viewport().width()))
        self.queue_fit()
