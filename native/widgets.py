import math
from PySide6.QtCore import Qt, QTimer, Slot, QSize
from PySide6.QtGui import QTextBlockFormat, QTextCursor, QTextLayout, QTextOption
from PySide6.QtWidgets import (QTextEdit, QSizePolicy, QFrame, QPushButton,
    QCheckBox, QComboBox, QStylePainter, QStyleOptionButton, QStyle)

def wrapped(text,font,width):
    """Use Qt's text layout, including long words, without changing accessible text."""
    lines=[]
    for paragraph in text.split('\n'):
        layout=QTextLayout(paragraph,font);option=QTextOption()
        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere);layout.setTextOption(option)
        layout.beginLayout()
        while True:
            line=layout.createLine()
            if not line.isValid():break
            line.setLineWidth(max(1,width));lines.append(paragraph[line.textStart():line.textStart()+line.textLength()].rstrip())
        layout.endLayout()
    return '\n'.join(lines) or ' '

class Button(QPushButton):
    """Native button painting/semantics with a height that follows wrapped text."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        policy=QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);policy.setHeightForWidth(True);self.setSizePolicy(policy)
    def margin(self):return max(12,self.fontMetrics().height()//2)
    def heightForWidth(self,width):
        lines=wrapped(self.text(),self.font(),width-2*self.margin()).count('\n')+1
        return max(44,super().sizeHint().height(),lines*self.fontMetrics().lineSpacing()+2*self.margin())
    def minimumSizeHint(self):return QSize(44,max(44,super().minimumSizeHint().height()))
    def sizeHint(self):
        hint=super().sizeHint()
        preferred=max(self.fontMetrics().horizontalAdvance(line) for line in self.text().split('\n'))+2*self.margin()
        width=min(520,max(hint.width(),preferred));return QSize(width,self.heightForWidth(width))
    def paintEvent(self,event):
        painter=QStylePainter(self);option=QStyleOptionButton();self.initStyleOption(option)
        option.text=wrapped(self.text(),self.font(),self.width()-2*self.margin())
        painter.drawControl(QStyle.CE_PushButton,option)

class CheckBox(QCheckBox):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        policy=QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred);policy.setHeightForWidth(True);self.setSizePolicy(policy)
    def text_width(self,width):return max(1,width-self.style().pixelMetric(QStyle.PM_IndicatorWidth)-24)
    def heightForWidth(self,width):return max(44,super().sizeHint().height(),(wrapped(self.text(),self.font(),self.text_width(width)).count('\n')+1)*self.fontMetrics().lineSpacing()+16)
    def minimumSizeHint(self):return QSize(44,max(44,super().minimumSizeHint().height()))
    def sizeHint(self):
        width=min(520,super().sizeHint().width());return QSize(width,self.heightForWidth(width))
    def paintEvent(self,event):
        painter=QStylePainter(self);option=QStyleOptionButton();self.initStyleOption(option)
        option.text=wrapped(self.text(),self.font(),self.text_width(self.width()))
        painter.drawControl(QStyle.CE_CheckBox,option)
    def hitButton(self,pos):return self.rect().contains(pos)

class Choice(QComboBox):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.setMinimumContentsLength(1);self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.view().setWordWrap(True);self.view().setTextElideMode(Qt.ElideNone)
        self.currentTextChanged.connect(self.setToolTip)

class Paragraph(QTextEdit):
    """Plain native text with real line-height, wrapping and selection; no web engine."""
    def __init__(self, value, line_height=1.5):
        super().__init__()
        self.setReadOnly(True)
        self.setTabChangesFocus(True)
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

    def setText(self,value):self.setPlainText(str(value))
    def text(self):return self.toPlainText()

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
