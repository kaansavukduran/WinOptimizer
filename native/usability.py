"""Native navigation and contextual guidance; never starts a Windows operation."""
from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QPushButton, QComboBox, QDialog, QDialogButtonBox, QScrollArea)

PAGES = ('home', 'scanFix', 'cleanup', 'drivers', 'hardware', 'startup',
         'workshop', 'tools', 'history', 'settings')

def setup(window):
    bar=QWidget(); row=QHBoxLayout(bar); row.setContentsMargins(0,0,0,0)
    window.brand=QLabel('WinOptimizer Aion'); window.brand.setObjectName('app-brand')
    row.addWidget(window.brand); row.addStretch()
    window.help_button=QPushButton(); window.help_button.setObjectName('context-help')
    window.help_button.clicked.connect(lambda:show_help(window)); row.addWidget(window.help_button)
    window.outer.insertWidget(0,bar)
    window.compact_nav=QWidget(); layout=QHBoxLayout(window.compact_nav); layout.setContentsMargins(0,0,0,0)
    window.nav_label=QLabel(); layout.addWidget(window.nav_label)
    window.page_picker=QComboBox(); window.page_picker.setObjectName('page-picker')
    window.nav_label.setBuddy(window.page_picker); layout.addWidget(window.page_picker,1)
    window.page_picker.activated.connect(lambda i:navigate(window,window.page_picker.itemData(i)))
    window.outer.insertWidget(1,window.compact_nav)
    window.compact_nav.hide()
    window.nav_shortcuts=[]
    for index,page in enumerate(PAGES):
        shortcut=QShortcut(QKeySequence('Ctrl+'+str((index+1)%10)),window)
        shortcut.activated.connect(lambda p=page:navigate(window,p)); window.nav_shortcuts.append(shortcut)
    help_key=QShortcut(QKeySequence('F1'),window);help_key.activated.connect(lambda:show_help(window))
    window.nav_shortcuts.append(help_key)

def navigate(window,page):
    if window.ready and page in PAGES:
        window.go(page)

def sync(window):
    if not hasattr(window,'page_picker'):return
    window.help_button.setText(window.t('ux.help')+' · F1')
    window.page_picker.setAccessibleName(window.t('ux.section'))
    window.nav_label.setText(window.t('ux.section'))
    blocker=QSignalBlocker(window.page_picker)
    window.page_picker.clear()
    for page in PAGES:window.page_picker.addItem(window.t(page),page)
    window.page_picker.setCurrentIndex(max(0,window.page_picker.findData(window.page)))
    del blocker
    window.page_picker.setEnabled(window.ready)
    for index in range(window.nav_layout.count()):
        button=window.nav_layout.itemAt(index).widget()
        button.setToolTip(button.text()+' · Ctrl+'+str((index+1)%10))
    adapt(window)

def adapt(window):
    if not hasattr(window,'compact_nav'):return
    required=sum(window.nav_layout.itemAt(i).widget().sizeHint().width() for i in range(window.nav_layout.count()))
    required+=window.nav_layout.spacing()*max(0,window.nav_layout.count()-1)+window.nav_layout.contentsMargins().left()+window.nav_layout.contentsMargins().right()
    compact=window.ready and required>window.width()-window.outer.contentsMargins().left()-window.outer.contentsMargins().right()-8
    focused=window.focusWidget()
    nav_had_focus=focused is not None and window.nav_widget.isAncestorOf(focused)
    picker_had_focus=focused is window.page_picker
    window.nav_scroll.setVisible(window.ready and not compact)
    window.compact_nav.setVisible(compact)
    if compact and nav_had_focus:window.page_picker.setFocus(Qt.OtherFocusReason)
    elif not compact and picker_had_focus:
        for button in window.nav_widget.findChildren(QPushButton):
            if button.isChecked():button.setFocus(Qt.OtherFocusReason);break

def show_help(window):
    # Reuse one dialog. Opening help never retries an operation or changes progress.
    dialog=getattr(window,'help_dialog',None)
    if dialog is not None:
        dialog.raise_(); dialog.activateWindow(); return
    dialog=QDialog(window); window.help_dialog=dialog
    dialog.setObjectName('usage-guide'); dialog.setWindowTitle(window.t('ux.help'))
    dialog.setWindowModality(Qt.WindowModal)
    dialog.setAttribute(Qt.WA_DeleteOnClose)
    dialog.finished.connect(lambda _:setattr(window,'help_dialog',None))
    dialog.resize(min(620,max(360,window.width()-40)),min(620,max(420,window.height()-60)))
    outer=QVBoxLayout(dialog); scroll=QScrollArea();scroll.setWidgetResizable(True)
    content=QWidget(); layout=QVBoxLayout(content)
    window.label(window.t('ux.guideTitle'),heading=True,layout=layout)
    window.label(window.t('ux.firstMinute'),layout=layout)
    window.label(window.t(window.page),heading=True,layout=layout)
    window.label(window.t('ux.pages.'+window.page),layout=layout)
    window.label(window.t('ux.feedback'),layout=layout)
    window.label(window.t('ux.keys'),layout=layout)
    layout.addStretch();scroll.setWidget(content);outer.addWidget(scroll)
    buttons=QDialogButtonBox(QDialogButtonBox.Close);buttons.rejected.connect(dialog.reject)
    buttons.button(QDialogButtonBox.Close).setText(window.t('ux.close'))
    outer.addWidget(buttons);dialog.show();buttons.button(QDialogButtonBox.Close).setFocus()
