import copy
import json
from pathlib import Path
import sys
import time
import pytest
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtWidgets import QApplication, QPushButton, QDialog, QDialogButtonBox, QComboBox

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'native'))
from app import Window, text

class FixtureBridge(QObject):
    failed=Signal(str)
    def __init__(self,settings,portable=False):
        super().__init__();self.settings=copy.deepcopy(settings);self.calls=[];self.portable=portable;self.trace=None
    def call(self,command,payload=None,callback=None):
        payload=copy.deepcopy(payload or {});self.calls.append((command,payload))
        if command=='bootstrap':data=dict(settings=self.settings,version='6.0.0',portable=self.portable,milestones=[])
        elif command=='settings.save':self.settings=payload;data=self.settings
        elif command=='operation.status':data=dict(trace=self.trace)
        elif command=='diagnostics.scan':data=dict(id='fixture-report',online=payload['online'],at='2026-11-10T12:00:00Z',findings=[dict(id=f'update:{i}',category='devices',status='update',reason='driverUpdate',evidence=dict(name=f'Fixture driver {i}'),actions=[dict(id='update-driver',kind='update')]) for i in range(24)])
        elif command=='diagnostics.updates':data=dict(success=False,reboot=True,items=[dict(id=i,name='Fixture driver',success=False,code=4) for i in payload['ids']])
        elif command in ('history','workshop.library'):data=dict(events=[],cleanup=[],packages=[],ignored=[])
        elif command=='updates.check':data=dict(available=True,version='6.1.0',notes={'tr':'Fixture'},portable=dict(bytes=100))
        elif command=='updates.portable':data={}
        else:data=[]
        if callback:callback(dict(ok=True,data=copy.deepcopy(data)))
    def close(self):pass

@pytest.fixture(scope='session')
def application():
    return QApplication.instance() or QApplication([])

@pytest.fixture
def window(application,tmp_path):
    settings=dict(schema=1,language='tr',theme='light',scale=100,textSize=100,font='system',lineHeight=1.5,letterSpacing=0,accent='#b82e69',density='comfortable',motion=False,sound=False,gamification=True,companion=True,followPointer=True,petting=True,mascotSize=100,channel='stable')
    bridge=FixtureBridge(settings);w=Window(bridge,tmp_path);w.show();application.processEvents();yield w,bridge;w.busy=False;w.close();application.processEvents()

@pytest.mark.parametrize('language',['tr','en'])
def test_native_scan_update_all_requires_no_checkboxes_and_confirms_every_driver(window,application,language):
    w,bridge=window;w.settings['language']=language;w.go('scanFix');w.show_result=lambda result:None
    w.findChild(QPushButton,'start-scan').click()
    assert ('diagnostics.scan',dict(online=True)) in bridge.calls
    button=w.findChild(QPushButton,'update-all');assert button and '(24)' in button.text()
    def accept():
        dialog=w.findChild(QDialog,'confirm-dialog');assert dialog
        dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok).click()
    QTimer.singleShot(0,accept);button.click()
    payload=next(p for c,p in bridge.calls if c=='diagnostics.updates')
    assert payload==dict(reportId='fixture-report',ids=[str(i) for i in range(24)],confirm=True)
    assert '24' not in w.notice.text() or w.state['updateResult']['success'] is False
    assert w.state['updateResult']['success'] is False

def test_native_scan_cancel_never_installs(window,application):
    w,bridge=window;w.go('scanFix');w.findChild(QPushButton,'start-scan').click()
    def reject():w.findChild(QDialog,'confirm-dialog').reject()
    QTimer.singleShot(0,reject);w.findChild(QPushButton,'update-all').click()
    assert not any(c=='diagnostics.updates' for c,_ in bridge.calls)

def test_native_routes_and_scaled_preferences_remain_available(window,application):
    w,bridge=window
    for page in ('home','scanFix','cleanup','drivers','startup','workshop','tools','history','settings'):
        w.page=page;w.render();application.processEvents()
    for key,value in [('language','en'),('theme','contrast'),('font','dyslexic'),('scale',200),('textSize',125)]:w.save_setting(key,value)
    w.settings_section='accessibility';w.resize(540,900);w.render();application.processEvents()
    assert w.settings['scale']==200 and w.settings['textSize']==125 and w.settings['font']=='dyslexic'
    assert w.findChild(QPushButton,'nav-settings') is not None
    assert w.scroll.verticalScrollBar().maximum()>0
    assert w.font().family()=='OpenDyslexic'

def test_native_trace_distinguishes_windows_events_skips_and_failures_and_retains_all_for_export(window,application):
    w,bridge=window;bridge.trace=dict(command='diagnostics.scan',status='attention',at='2026-11-10T12:00:00Z',events=[dict(at='2026-11-10T12:00:00Z',origin='native',step='devices',status='failed',reason='PROVIDER_FAILED'),dict(at='2026-11-10T12:00:01Z',origin='app',step='windows-updates',status='skipped',reason='offline')]);w.poll()
    assert w.log.topLevelItemCount()==2
    assert w.log.topLevelItem(0).text(1)=='Windows'
    assert w.log.topLevelItem(0).text(3)=='Başarısız'
    assert w.log.topLevelItem(1).text(3)=='Atlandı'
    assert 'Çevrimiçi kontrol kapalı' in w.log.topLevelItem(1).text(4)

def test_portable_native_update_never_calls_setup(window,application):
    w,bridge=window;w.portable=True;w.settings_section='updates';w.go('settings');w.findChild(QPushButton,'check-app-update').click()
    assert w.findChild(QPushButton,'install-app-update') is None
    button=w.findChild(QPushButton,'portableDownload');assert button;button.click()
    assert any(c=='updates.portable' for c,_ in bridge.calls)
    assert not any(c=='updates.install' for c,_ in bridge.calls)


def test_primary_scan_action_is_visible_before_scrolling_and_trace_keeps_latest_step_status(window,application):
    w,bridge=window;w.resize(1024,750);w.go('scanFix');application.processEvents()
    button=w.findChild(QPushButton,'start-scan')
    assert w.scroll.viewport().rect().contains(button.mapTo(w.scroll.viewport(),button.rect().center()))
    bridge.trace=dict(command='diagnostics.scan',status='complete',events=[dict(at='2026-11-10T12:00:00Z',origin='native',action='diagnostics',step='devices',status='running'),dict(at='2026-11-10T12:00:01Z',origin='native',action='diagnostics',step='devices',status='complete',count=12)])
    w.poll();assert w.log.topLevelItemCount()==1;assert w.log.topLevelItem(0).text(3)=='Tamamlandı';assert len(w.trace['events'])==2
