"""Real Qt controls; fixtures supply backend data, never claim Windows integration."""
from PySide6.QtCore import Qt, QObject, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QDialogButtonBox, QPushButton
import pytest
from test_interface import application, window, Window
from test_recovery import until
from personalize import contrast, focus_color, ink
from usability import PAGES

@pytest.mark.parametrize('language',['tr','en'])
def test_compact_navigation_exposes_all_sections_and_keeps_selected_page(window,application,language):
    w,b=window;w.settings.update(language=language,scale=200,textSize=125,font='dyslexic')
    w.resize(540,900);w.appearance();w.go('hardware');QTest.qWait(30)
    assert w.compact_nav.isVisible() and not w.nav_scroll.isVisible()
    assert [w.page_picker.itemData(i) for i in range(10)]==list(PAGES)
    assert w.page_picker.currentData()=='hardware'
    assert w.page_picker.minimumSizeHint().width()<w.width()
    w.page_picker.setCurrentIndex(9);w.page_picker.activated.emit(9)
    assert w.page=='settings' and w.page_picker.currentData()=='settings'
    assert not any(c in ('diagnostics.scan','diagnostics.updates','cleanup','startup-disable') for c,_ in b.calls)

def test_navigation_adapts_on_resize_and_focus_moves_to_visible_control(window,application):
    w,_=window;w.resize(2000,900);w.go('hardware');QTest.qWait(30)
    assert w.nav_scroll.isVisible() and not w.compact_nav.isVisible()
    w.activateWindow();w.findChild(QPushButton,'nav-hardware').setFocus();QTest.qWait(20)
    w.resize(540,900);QTest.qWait(30)
    assert w.compact_nav.isVisible() and w.page_picker.hasFocus()
    w.resize(2000,900);QTest.qWait(30)
    assert w.nav_scroll.isVisible() and w.findChild(QPushButton,'nav-hardware').hasFocus()

@pytest.mark.parametrize('language',['tr','en'])
@pytest.mark.parametrize('page',PAGES)
def test_context_help_is_localized_readable_and_never_runs_operations(window,application,language,page):
    from widgets import Paragraph
    w,b=window;w.settings['language']=language;w.page=page;w.render();before=list(b.calls)
    w.help_button.click();application.processEvents();dialog=w.help_dialog
    assert dialog and dialog.isVisible() and dialog.windowModality()==Qt.WindowModal
    paragraphs='\n'.join(p.toPlainText() for p in dialog.findChildren(Paragraph))
    assert w.t('ux.pages.'+page) in paragraphs and 'Ctrl+0' in paragraphs
    assert not any('ux.' in p.toPlainText() for p in dialog.findChildren(Paragraph))
    from usability import show_help
    show_help(w);assert w.help_dialog is dialog and b.calls==before
    QTest.keyClick(dialog,Qt.Key_Escape);application.processEvents();assert w.help_dialog is None
    assert w.state['milestones']==[] and b.calls==before

def test_real_keyboard_shortcuts_switch_sections_and_open_close_help(window,application):
    w,b=window;w.resize(540,900);w.activateWindow();QTest.qWait(30)
    for key,page in [(Qt.Key_5,'hardware'),(Qt.Key_0,'settings'),(Qt.Key_1,'home')]:
        QTest.keyClick(w,key,Qt.ControlModifier);until(application,lambda:w.page==page)
    before=list(b.calls);QTest.keyClick(w,Qt.Key_F1);until(application,lambda:w.help_dialog is not None)
    QTest.keyClick(w.help_dialog,Qt.Key_Escape);until(application,lambda:w.help_dialog is None)
    assert b.calls==before

@pytest.mark.parametrize('theme',['light','dark','contrast'])
@pytest.mark.parametrize('accent',['#ffffff','#000000','#b82e69','#63d5fa'])
def test_actual_theme_tokens_keep_focus_and_active_text_contrast(window,theme,accent):
    w,_=window;w.settings.update(theme=theme,accent=accent);w.appearance();t=w.visual_tokens
    for surface in [t['background'],t['surface']]:
        assert contrast(t['text'],surface)>=4.5
        assert contrast(t['focus'],surface)>=3
        assert contrast(t['border'],surface)>=3
    assert contrast(t['accentInk'],t['accent'])>=4.5
    assert 'QComboBox:focus' in w.styleSheet() and 'QTreeWidget:focus' in w.styleSheet()
    assert w.settings['accent']==accent

class DelayedBootstrap(QObject):
    failed=Signal(str)
    def call(self,command,payload=None,callback=None):
        if command=='bootstrap':self.callback=callback
    def close(self):pass

def test_startup_explains_waiting_and_failure_stops_loading(application,tmp_path):
    b=DelayedBootstrap();w=Window(b,tmp_path);w.show();application.processEvents()
    assert not w.ready and w.progress.isVisible() and w.progress.maximum()==0
    assert w.notice.text()==w.t('ux.loading') and not w.page_picker.isEnabled()
    b.callback(dict(ok=False,error='BACKEND_UNAVAILABLE'));application.processEvents()
    assert not w.progress.isVisible() and w.failure and w.backend_lost
    assert w.scroll.widget().findChild(QPushButton,'recovery-close')
    w.close();application.processEvents()
