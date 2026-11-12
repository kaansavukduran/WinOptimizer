"""Native navigation and contextual guidance; never starts a Windows operation."""
from PySide6.QtCore import Qt, QSignalBlocker, QTimer
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (QWidget, QLabel, QHBoxLayout, QVBoxLayout, QBoxLayout,
    QPushButton, QComboBox, QDialog, QDialogButtonBox, QScrollArea, QSizePolicy)

from widgets import Button as QPushButton, Choice as QComboBox

PAGES = ('home', 'scanFix', 'cleanup', 'drivers', 'hardware', 'startup',
         'workshop', 'tools', 'history', 'settings')

def setup(window):
    bar=QWidget(); row=QBoxLayout(QBoxLayout.LeftToRight,bar); row.setContentsMargins(0,0,0,0)
    window.brand_bar,window.brand_layout=bar,row
    window.brand=QLabel('WinOptimizer Aion'); window.brand.setObjectName('app-brand')
    window.brand.setWordWrap(True);row.addWidget(window.brand,1)
    window.help_button=QPushButton(); window.help_button.setObjectName('context-help')
    policy=window.help_button.sizePolicy();policy.setHorizontalPolicy(QSizePolicy.Maximum);window.help_button.setSizePolicy(policy)
    window.help_button.clicked.connect(lambda:show_help(window));row.addStretch();row.addWidget(window.help_button)
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
    window.initial_nav_focus=QTimer(window);window.initial_nav_focus.setSingleShot(True)
    window.initial_nav_focus.timeout.connect(lambda:focus_navigation(window))

def focus_navigation(window):
    if not window.ready or window.busy:return
    if window.page_picker.isVisible():window.page_picker.setFocus(Qt.OtherFocusReason)
    else:
        for button in window.nav_widget.findChildren(QPushButton):
            if button.isChecked():button.setFocus(Qt.OtherFocusReason);break

def navigate(window,page):
    if window.ready and page in PAGES:
        window.go(page)

def sync(window):
    if not hasattr(window,'page_picker'):return
    window.help_button.setText(window.t('ux.helpButton')+' · F1')
    window.help_button.setAccessibleName(window.t('ux.help')+' · F1')
    window.page_picker.setAccessibleName(window.t('ux.section'))
    window.nav_label.setText(window.t('ux.section'))
    blocker=QSignalBlocker(window.page_picker)
    desired=[(window.t(page),page) for page in PAGES]
    if [(window.page_picker.itemText(i),window.page_picker.itemData(i)) for i in range(window.page_picker.count())]!=desired:
        window.page_picker.clear()
        for title,page in desired:window.page_picker.addItem(title,page)
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
    nav_height=max((window.nav_layout.itemAt(i).widget().sizeHint().height() for i in range(window.nav_layout.count())),default=0)
    nav_margins=window.nav_layout.contentsMargins()
    window.nav_scroll.setFixedHeight(max(round(64*window.settings.get('scale',100)/100),nav_height+nav_margins.top()+nav_margins.bottom()+2))
    focused=window.focusWidget()
    nav_had_focus=focused is not None and window.nav_widget.isAncestorOf(focused)
    picker_had_focus=focused is window.page_picker
    window.nav_scroll.setVisible(window.ready and not compact)
    window.compact_nav.setVisible(compact)
    width=window.width()-window.outer.contentsMargins().left()-window.outer.contentsMargins().right()
    # The OS title already identifies the app; keep task space at large text sizes.
    window.brand.setVisible(not compact)
    # Version remains under Settings > About; prioritize work over footer chrome.
    window.footer.setVisible(not (compact and window.font().pointSizeF()>18))
    brand_width=window.brand.fontMetrics().horizontalAdvance(window.brand.text()) if not compact else 0
    window.brand_layout.setDirection(QBoxLayout.TopToBottom if brand_width+window.help_button.sizeHint().width()+12>width else QBoxLayout.LeftToRight)
    if hasattr(window,'log_title'):
        narrow=width<900
        window.log_title.setVisible(not narrow or window.details_expanded)
        full=window.t('forge.hide' if window.details_expanded else 'forge.show')
        window.log_toggle.setText(window.t('ux.details') if narrow else full)
        window.log_toggle.setAccessibleName(full);window.log_toggle.setToolTip(full)
    if compact and nav_had_focus:window.page_picker.setFocus(Qt.OtherFocusReason)
    elif not compact and picker_had_focus:
        for button in window.nav_widget.findChildren(QPushButton):
            if button.isChecked():button.setFocus(Qt.OtherFocusReason);break
    # Forms reflow on resize without recreating inputs or losing unsaved text.
    from PySide6.QtWidgets import QFormLayout,QGridLayout
    body=window.scroll.widget()
    if body:
        from widgets import ActionRow
        for row in body.findChildren(ActionRow):row.adapt()
        for form in body.findChildren(QFormLayout):
            form.setRowWrapPolicy(QFormLayout.WrapAllRows if width<900 or window.settings.get('scale',100)>=150 else QFormLayout.WrapLongRows)
            for index in range(form.rowCount()):
                item=form.itemAt(index,QFormLayout.LabelRole)
                if item and isinstance(item.widget(),QLabel):
                    item.widget().setWordWrap(True);item.widget().setTextFormat(Qt.PlainText)
        for grid in body.findChildren(QGridLayout):
            maximum=grid.property('responsiveColumns')
            if not maximum:continue
            widgets=[grid.itemAt(i).widget() for i in range(grid.count())]
            if not widgets:continue
            available=min(grid.geometry().width() or width,width-80)
            widest=max(w.sizeHint().width() for w in widgets)
            columns=max(1,min(maximum,(available+grid.spacing())//max(1,widest+grid.spacing())))
            if grid.property('currentColumns')==columns:continue
            for widget in widgets:grid.removeWidget(widget)
            for index,widget in enumerate(widgets):grid.addWidget(widget,index//columns,index%columns)
            grid.setProperty('currentColumns',columns)

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
    window.label(window.t(window.page),heading=True,level=2,layout=layout)
    window.label(window.t('ux.pages.'+window.page),layout=layout)
    window.label(window.t('ux.feedback'),layout=layout)
    window.label(window.t('ux.keys'),layout=layout)
    layout.addStretch();scroll.setWidget(content);outer.addWidget(scroll)
    buttons=QDialogButtonBox(QDialogButtonBox.Close);buttons.rejected.connect(dialog.reject)
    buttons.button(QDialogButtonBox.Close).setText(window.t('ux.close'))
    outer.addWidget(buttons);dialog.show();buttons.button(QDialogButtonBox.Close).setFocus()
