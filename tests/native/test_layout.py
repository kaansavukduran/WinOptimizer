"""AIONIA 1.2 native window profiles, not physical phone/tablet certification."""
import copy
import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QPushButton,QCheckBox,QComboBox,QLabel,QFormLayout
from test_interface import application,window,fixture_care
from test_recovery import until
from usability import PAGES
from widgets import Button,CheckBox,wrapped,Paragraph

def populate(w):
    w.state.update(care=fixture_care(),report=dict(id='layout-fixture',online=False,at='2026-11-12T12:00:00Z',findings=[dict(id='update:0',category='devices',status='update',reason='driverUpdate',evidence=dict(name='Fixture audio processing driver with a deliberately long localized description'),actions=[dict(kind='update',id='update-driver')])]),
        updates=[dict(id='0',name='Fixture audio driver',manufacturer='Fixture',bytes=100)],
        drivers=[dict(id='0',name='Fixture driver',provider='Fixture',version='1.0',problem=None)],
        startup=[dict(id=str(i),name='Fixture startup '+str(i),command='C:\\Fixture\\'+'long-path-segment'*8) for i in range(2)],
        library=dict(packages=[],ignored=[],focus=None),history=dict(cleanup=[],events=[]),
        offline=dict(devices=[dict(id='0',name='Fixture device',hardwareIds=['PCI\\VEN_FIXTURE'])]))

@pytest.mark.parametrize('language',['tr','en'])
@pytest.mark.parametrize('profile',[(540,200,125),(540,100,100),(1240,100,100)])
@pytest.mark.parametrize('page',PAGES)
def test_populated_main_pages_reflow_without_outer_horizontal_scrolling(window,application,language,profile,page):
    w,_=window;populate(w);width,scale,text=profile
    w.settings.update(language=language,theme='dark' if scale==200 else 'light',scale=scale,textSize=text,font='dyslexic',operationDetails=False)
    w.resize(width,900);w.appearance();w.page=page;w.render();QTest.qWait(60)
    until(application,lambda:w.scroll.horizontalScrollBar().maximum()==0)
    assert w.scroll.widget().width()<=w.scroll.viewport().width()
    assert all(b.height()>=b.heightForWidth(b.width()) for b in w.scroll.widget().findChildren(Button) if b.isVisible())
    assert len([b for b in w.scroll.widget().findChildren(QPushButton) if b.property('primary')])<=1
    titles=[x for x in w.scroll.widget().findChildren(Paragraph) if x.property('heading') and x.property('headingLevel')==1]
    assert len(titles)==1 and titles[0].toPlainText()==w.t(page)

@pytest.mark.parametrize('language',['tr','en'])
@pytest.mark.parametrize('page,section',[(p,s) for p,items in [('drivers',['updates','inventory','backups','offline','ignored']),('workshop',['runtimes','points','focus','devices']),('settings',['general','appearance','accessibility','gameSettings','dataSettings','updates','about'])] for s in items])
def test_subsections_have_named_headings_and_fit_large_text(window,application,language,page,section):
    w,_=window;populate(w);w.settings.update(language=language,scale=200,textSize=125,font='dyslexic',operationDetails=False)
    w.resize(540,900);w.appearance();setattr(w,{'drivers':'driver_section','workshop':'workshop_section','settings':'settings_section'}[page],section)
    w.page=page;w.render();QTest.qWait(60)
    until(application,lambda:w.scroll.horizontalScrollBar().maximum()==0)
    headings=[x for x in w.scroll.widget().findChildren(Paragraph) if x.property('headingLevel')==2]
    expected=w.t('dc.'+section if page=='drivers' else 'dc.workshop.'+section if page=='workshop' else section)
    assert any(x.toPlainText()==expected for x in headings)
    assert len([b for b in w.scroll.widget().findChildren(QPushButton) if b.property('primary')])<=1

def test_native_wrapped_controls_keep_complete_accessible_text_and_keyboard_semantics(application):
    text='A long confirmation action with several words and '+('longidentifier'*7)
    button=Button(text);button.resize(180,button.heightForWidth(180));button.show();QTest.qWait(20)
    assert button.text()==text and button.heightForWidth(180)>button.heightForWidth(500)
    clicked=[];button.clicked.connect(lambda:clicked.append(True));button.setFocus();QTest.keyClick(button,Qt.Key_Space);assert clicked
    check=CheckBox(text);check.resize(180,check.heightForWidth(180));check.show();QTest.qWait(20)
    check.setFocus();QTest.keyClick(check,Qt.Key_Space);assert check.isChecked() and check.text()==text
    assert check.heightForWidth(180)>44
    button.close();check.close()

def test_startup_empty_state_and_single_selection_explain_disabled_action(window,application):
    w,b=window;w.go('startup');QTest.qWait(20)
    from widgets import Paragraph
    assert any(p.toPlainText()==w.t('layout.startupEmpty') for p in w.scroll.widget().findChildren(Paragraph))
    populate(w);w.render();QTest.qWait(20)
    from PySide6.QtWidgets import QTreeWidget
    tree=w.scroll.widget().findChild(QTreeWidget,'startup-tree');button=w.scroll.widget().findChild(QPushButton,'startup-disable');assert not button.isEnabled()
    tree.topLevelItem(0).setCheckState(0,Qt.Checked);assert button.isEnabled()
    tree.topLevelItem(1).setCheckState(0,Qt.Checked);assert not button.isEnabled()
    assert w.scroll.widget().findChild(Paragraph,'startup-selection-hint').toPlainText()==w.t('layout.oneStartup')
    assert not any(c=='startup-disable' for c,_ in b.calls)

def test_resize_preserves_field_input_and_disclosure_state(window,application):
    w,_=window;w.go('settings');QTest.qWait(20)
    from PySide6.QtWidgets import QLineEdit
    entry=w.scroll.widget().findChild(QLineEdit,'setting-accent');entry.setText('#abc123');w.resize(540,900);QTest.qWait(30)
    assert entry.text()=='#abc123' and all(f.rowWrapPolicy()==QFormLayout.WrapAllRows for f in w.scroll.widget().findChildren(QFormLayout))
    w.go('scanFix');QTest.qWait(20);toggle=w.scroll.widget().findChild(QCheckBox,'scan-options-toggle');toggle.setChecked(True)
    online=w.scroll.widget().findChild(QCheckBox,'scan-online');online.setChecked(False);w.render();QTest.qWait(20)
    assert w.scroll.widget().findChild(QCheckBox,'scan-options-toggle').isChecked()
    assert not w.scroll.widget().findChild(QCheckBox,'scan-online').isChecked()

@pytest.mark.parametrize('language',['tr','en'])
def test_expanded_options_and_long_hardware_labels_do_not_force_page_panning(window,application,language):
    w,b=window;w.settings.update(language=language,scale=200,textSize=125,font='dyslexic',operationDetails=False)
    w.resize(540,900);w.appearance();w.go('scanFix');QTest.qWait(30)
    w.scroll.widget().findChild(QCheckBox,'scan-options-toggle').setChecked(True);QTest.qWait(30)
    assert w.scroll.horizontalScrollBar().maximum()==0
    online=w.scroll.widget().findChild(QCheckBox,'scan-online');assert online.height()>=online.heightForWidth(online.width())
    b.call('hardware',callback=lambda r:w.state.update(hardware=r['data']))
    w.page='hardware';w.render();QTest.qWait(50);until(application,lambda:w.scroll.horizontalScrollBar().maximum()==0)

@pytest.mark.parametrize('language',['tr','en'])
def test_large_text_error_state_keeps_recovery_actions_reachable(window,application,language):
    w,_=window;w.settings.update(language=language,scale=200,textSize=125,font='dyslexic',operationDetails=False)
    w.resize(540,900);w.appearance();w.page='hardware';w.error('BACKEND_PROTOCOL_FAILED');QTest.qWait(60)
    assert w.scroll.horizontalScrollBar().maximum()==0 and w.notice.tabChangesFocus()
    button=w.scroll.widget().findChild(QPushButton,'recovery-copy');assert button
    w.scroll.ensureWidgetVisible(button);QTest.qWait(50)
    assert w.scroll.viewport().rect().contains(button.mapTo(w.scroll.viewport(),button.rect().center()))

def test_reduced_scale_navigation_does_not_clip_wrapped_tab_buttons(window,application):
    from PySide6.QtCore import QRect
    w,_=window;w.settings.update(scale=80,textSize=100,density='compact')
    w.resize(1200,900);w.appearance();w.render();QTest.qWait(60)
    if w.nav_scroll.isVisible():
        viewport=w.nav_scroll.viewport()
        for button in w.nav_widget.findChildren(QPushButton):
            assert viewport.rect().contains(QRect(button.mapTo(viewport,button.rect().topLeft()),button.size()))
    else:assert w.page_picker.isVisible() and w.page_picker.count()==10
