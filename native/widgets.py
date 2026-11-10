import math
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextBlockFormat, QTextCursor
from PySide6.QtWidgets import QTextEdit, QSizePolicy, QFrame

class Paragraph(QTextEdit):
    """Plain native text with real line-height, wrapping and selection; no web engine."""
    def __init__(self, value, line_height=1.5):
        super().__init__()
        self.setReadOnly(True)
        self.setPlainText(value)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet('QTextEdit { border: none; background: transparent; padding: 0; }')
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Minimum)
        self.document().setDocumentMargin(1)
        cursor=self.textCursor();cursor.select(QTextCursor.Document)
        block=QTextBlockFormat();block.setLineHeight(line_height*100,QTextBlockFormat.ProportionalHeight.value)
        cursor.mergeBlockFormat(block)
        self.document().documentLayout().documentSizeChanged.connect(self.fit)
        QTimer.singleShot(0,self.fit)

    def fit(self,*_):
        self.setFixedHeight(max(24,math.ceil(self.document().size().height())+6))

    def resizeEvent(self,event):
        super().resizeEvent(event)
        self.document().setTextWidth(max(40,self.viewport().width()))
        self.fit()
