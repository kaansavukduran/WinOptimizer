"""Native appearance controls and per-page companion header."""
import re
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QBoxLayout, QGridLayout, QLineEdit, QColorDialog, QPushButton
from mascot import Aion
from widgets import Button as QPushButton

PALETTE = [('pink','#b82e69'),('blue','#066f82'),('purple','#7451b8'),('green','#21734a'),('amber','#8a5100')]

class ResponsiveRow(QWidget):
    def __init__(self,parent,owner):
        super().__init__(parent)
        self.owner=owner
        self.row=QBoxLayout(QBoxLayout.LeftToRight,self)
        self.row.setContentsMargins(0,0,0,0)
        self.adapt()
    def adapt(self):
        self.row.setDirection(QBoxLayout.TopToBottom if self.owner.width()<900 else QBoxLayout.LeftToRight)
    def resizeEvent(self,event):
        self.adapt()
        super().resizeEvent(event)

def ink(hex_color):
    color=QColor(hex_color)
    channels=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in (color.redF(),color.greenF(),color.blueF())]
    luminance=sum(a*b for a,b in zip(channels,(.2126,.7152,.0722)))
    return '#000000' if (luminance+.05)/.05 >= 1.05/(luminance+.05) else '#ffffff'

def luminance(hex_color):
    color=QColor(hex_color)
    values=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in (color.redF(),color.greenF(),color.blueF())]
    return sum(a*b for a,b in zip(values,(.2126,.7152,.0722)))

def contrast(first,second):
    a,b=sorted((luminance(first),luminance(second)))
    return (b+.05)/(a+.05)

def focus_color(accent,bg,surface):
    # User colors remain free. Keyboard focus must stay visible on both surfaces.
    if min(contrast(accent,bg),contrast(accent,surface))>=3:return accent
    return max(('#63d5fa','#f4a9cd','#003b55','#741a46','#000000','#ffffff'),
               key=lambda c:min(contrast(c,bg),contrast(c,surface)))

def header(window,title=True):
    wrapper=ResponsiveRow(window.body.parentWidget(),window);window.companion_header=wrapper;row=wrapper.row;copy=QVBoxLayout()
    if title:window.label(window.t(window.page),heading=True,layout=copy)
    caption=QLabel(window.t('look.pages.'+window.page));caption.setWordWrap(True);caption.setTextFormat(Qt.PlainText);copy.addWidget(caption)
    row.addLayout(copy,1)
    window.aion=Aion(window.resource_root,lambda key:window.t('n.'+key),window.page,compact=True,parent=wrapper)
    window.aion.paused=window.aion_paused
    window.aion.configure(window.settings)
    if window.failure:window.aion.set_state('help')
    elif window.busy:window.aion.set_state('read')
    row.addWidget(window.aion)
    controls=QHBoxLayout()
    def open_settings():
        window.settings_section='appearance'
        window.go('settings')
    window.button('look.quick',open_settings,layout=controls,name='quick-appearance')
    pause=window.button('Ⅱ',window.toggle_pause,layout=controls,literal=True,name='aion-pause')
    window.aion_pause=pause
    pause.setFixedWidth(round(44*window.settings.get('scale',100)/100))
    pause.setEnabled(window.settings.get('companion',True))
    controls.addStretch()
    copy.addLayout(controls)
    window.body.addWidget(wrapper)
    sync(window)

def sync(window):
    root=window.scroll.widget() if hasattr(window,'scroll') else None
    if root:
        for button in root.findChildren(QPushButton):
            if button.objectName().startswith('accent-preset-'):
                color=button.property('accentColor')
                button.setChecked(color.lower()==window.settings.get('accent','').lower())
    if getattr(window,'aion',None):
        window.aion.configure(window.settings)
        button=getattr(window,'aion_pause',None)
        if button:
            label=window.t('n.play' if window.aion.paused else 'n.pause')
            button.setText('▶' if window.aion.paused else 'Ⅱ')
            button.setToolTip(label);button.setAccessibleName(label)
            button.setEnabled(window.settings.get('companion',True))

def font_controls(window,form):
    choose=window.choice(form,'font',[('system',window.t('systemFont')),('readable',window.t('readableFont')),('dyslexic',window.t('dyslexicFont'))])
    sample=QWidget();layout=QVBoxLayout(sample);layout.setContentsMargins(0,0,0,0)
    selected=window.label(window.t('look.preview')+' · '+choose.currentText(),layout=layout)
    selected.setObjectName('font-preview-title')
    choose.currentTextChanged.connect(lambda value:selected.setPlainText(window.t('look.preview')+' · '+value))
    preview=window.label(window.t('fontPreview'),layout=layout);preview.setObjectName('font-preview')
    preview.setAccessibleName(window.t('look.preview'))
    window.label(window.t('look.offlineFont'),layout=layout)
    form.addRow(sample)

def note(window,form,key):
    sample=QWidget();layout=QVBoxLayout(sample);layout.setContentsMargins(0,0,0,0)
    window.label(window.t(key),layout=layout);form.addRow(sample)

def accent_controls(window,form):
    row=QWidget();layout=QVBoxLayout(row)
    entry=QLineEdit(window.settings.get('accent','#b82e69'));entry.setObjectName('setting-accent');entry.setAccessibleName(window.t('accent'))
    status=window.label(window.t('look.colorHelp'),layout=layout);status.setObjectName('accent-feedback')
    def apply(color):
        window.save_setting('accent',color)
        entry.setText(window.settings['accent'])
        status.setPlainText(window.t('look.colorHelp'))
    def custom():
        candidate=entry.text().strip()
        if re.fullmatch(r'#[0-9a-fA-F]{6}',candidate):apply(candidate.lower())
        else:
            entry.setText(window.settings['accent'])
            status.setPlainText(window.t('look.colorInvalid'))
    entry.editingFinished.connect(custom)
    layout.addWidget(entry)
    palette=QGridLayout();palette.setProperty('responsiveColumns',2);layout.addLayout(palette)
    for index,(name,color) in enumerate(PALETTE):
        b=QPushButton(window.t('look.'+name));b.setObjectName('accent-preset-'+name);b.setCheckable(True)
        b.setProperty('accentColor',color);b.setChecked(window.settings.get('accent','').lower()==color)
        b.setStyleSheet(f'QPushButton{{background:{color};color:{ink(color)};}}')
        b.clicked.connect(lambda _,c=color:apply(c));palette.addWidget(b,index//2,index%2)
    def picker():
        color=QColorDialog.getColor(QColor(window.settings.get('accent','#b82e69')),window,window.t('accent'))
        if color.isValid():apply(color.name())
    window.button('look.pick',picker,layout=layout,name='accent-picker')
    window.button('n.default',lambda:apply('#b82e69'),layout=layout,name='accent-reset')
    form.addRow(window.t('accent'),row)
