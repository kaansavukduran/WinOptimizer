import hashlib
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QRawFont, QImage
from PySide6.QtWidgets import QComboBox, QPushButton, QLineEdit
from PySide6.QtTest import QTest
import pytest
from test_interface import application, window, ROOT
from mascot import PAGE_CLIPS
from personalize import ink

@pytest.mark.parametrize('language',['tr','en'])
def test_font_is_visible_in_appearance_and_real_turkish_glyphs_are_bundled(window,application,language):
    w,_=window;w.settings['language']=language;w.go('settings')
    combo=w.scroll.widget().findChild(QComboBox,'setting-font');assert combo
    combo.setCurrentIndex(combo.findData('dyslexic'));application.processEvents()
    assert w.settings['font']=='dyslexic' and w.font().family()=='OpenDyslexic'
    from widgets import Paragraph
    preview=w.scroll.widget().findChild(Paragraph,'font-preview')
    assert preview.font().family()=='OpenDyslexic' and 'Ç Ğ İ Ö Ş Ü' in preview.toPlainText()
    raw=QRawFont.fromFont(preview.font());assert raw.familyName()=='OpenDyslexic'
    assert all(raw.supportsCharacter(ord(c)) for c in 'ÇĞİÖŞÜçğıöşü')
    assert (ROOT/'public/fonts/OFL.txt').is_file()
    assert w.settings['theme']=='light' and w.settings['scale']==100 and w.settings['textSize']==100

def test_color_presets_custom_picker_validation_and_independent_settings(window,monkeypatch):
    import personalize
    w,b=window;w.go('settings')
    w.scroll.widget().findChild(QPushButton,'accent-preset-blue').click()
    assert w.settings['accent']=='#066f82' and w.settings['theme']=='light'
    edit=w.scroll.widget().findChild(QLineEdit,'setting-accent');edit.setText('bad-input')
    before=len(b.calls);edit.editingFinished.emit()
    assert edit.text()=='#066f82' and len(b.calls)==before
    monkeypatch.setattr(personalize.QColorDialog,'getColor',lambda *args:QColor('#f6d3e4'))
    w.scroll.widget().findChild(QPushButton,'accent-picker').click()
    assert w.settings['accent']=='#f6d3e4' and ink(w.settings['accent'])=='#000000'
    monkeypatch.setattr(personalize.QColorDialog,'getColor',lambda *args:QColor())
    before=len(b.calls);w.scroll.widget().findChild(QPushButton,'accent-picker').click();assert len(b.calls)==before
    w.save_setting('theme','contrast');assert w.settings['accent']=='#f6d3e4'
    w.scroll.widget().findChild(QPushButton,'accent-reset').click()
    assert w.settings['accent']=='#b82e69' and w.settings['theme']=='contrast' and w.settings['font']=='system'

@pytest.mark.parametrize('page',list(PAGE_CLIPS))
def test_every_page_has_its_own_clip_quick_settings_and_pet_controls(window,application,page):
    w,_=window;w.page=page;w.render();application.processEvents()
    a=w.aion;assert a and a.page==page and a.parentWidget() is not None
    sheet,rect,_=a.frame_source();assert not sheet.isNull() and rect.width()==256
    source,row=PAGE_CLIPS[page];assert rect.y()==row*256
    assert sheet.cacheKey()==(a.sections if source=='sections' else a.core).cacheKey()
    w.scroll.widget().findChild(QPushButton,'aion-pause').click();assert a.paused
    w.scroll.widget().findChild(QPushButton,'quick-appearance').click()
    assert w.page=='settings' and w.settings_section=='appearance' and w.aion.paused
    w.scroll.widget().findChild(QPushButton,'aion-pause').click();assert not w.aion.paused

def test_animation_clock_success_return_reduced_motion_and_hidden_pause(window,application):
    w,_=window;w.settings.update(motion=True,followPointer=False);w.go('hardware');w.activateWindow();QTest.qWait(30)
    a=w.aion;first=a.frame_source()[1].x();QTest.qWait(420)
    assert a.frame_source()[1].x()!=first
    a.set_state('celebrate');a.elapsed=1320;a.tick();assert a.state=='idle'
    w.save_setting('motion',False);assert not a.motion()
    a.elapsed=720;assert a.frame_source()[1].x()==0
    a.hide();assert not a.timer.isActive()
    w.save_setting('companion',False);assert a.isHidden()
    w.go('scanFix');assert w.scroll.widget().findChild(QPushButton,'start-scan').isEnabled()

def test_generated_atlas_has_24_distinct_complete_cells_and_alpha():
    image=QImage(str(ROOT/'public/assets/aion-sections.png'))
    assert (image.width(),image.height())==(1024,1536) and image.hasAlphaChannel()
    hashes=[]
    for row in range(6):
        for col in range(4):
            cell=image.copy(col*256,row*256,256,256)
            assert cell.pixelColor(0,0).alpha()<=1 and cell.pixelColor(255,255).alpha()<=1
            assert any(cell.pixelColor(x,y).alpha()>100 for x,y in [(128,64),(128,128),(160,200)])
            hashes.append(hashlib.sha256(bytes(cell.constBits())).hexdigest())
    assert len(set(hashes))==24

@pytest.mark.parametrize('language',['tr','en'])
def test_large_text_narrow_window_keeps_font_and_color_controls_accessible(window,application,language):
    from test_recovery import until
    w,_=window;w.settings.update(language=language,scale=200,textSize=125,font='dyslexic',operationDetails=False)
    w.resize(540,900);w.appearance();w.go('settings');QTest.qWait(50)
    for cls,name in [(QComboBox,'setting-font'),(QPushButton,'accent-picker')]:
        control=w.scroll.widget().findChild(cls,name);assert control
        def visible():
            w.scroll.ensureWidgetVisible(control);application.processEvents()
            return w.scroll.viewport().rect().contains(control.mapTo(w.scroll.viewport(),control.rect().center()))
        until(application,visible)
    assert w.settings['scale']==200 and w.settings['textSize']==125
