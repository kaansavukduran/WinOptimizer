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
        elif command=='care.snapshot':data=dict(schema=1,at='2026-11-10T12:00:00Z',readOnly=True,online=False,success=False,needsAttention=True,sections=[dict(id=key,status='unavailable' if key=='defender' else 'available' if key in ('readiness','systemEvents') else 'empty',source='Fixture local provider',items=[dict(name='Fixture Windows',version='11',build='fixture',uptimeSeconds=3600,restartSignals=[],restartUnknown=False)] if key=='readiness' else [dict(provider='Fixture event',eventId=41,level=1,message='private local event message',at='2026-11-10T12:00:00Z')] if key=='systemEvents' else []) for key in ('readiness','defender','firewall','systemEvents','appEvents','crashes','dumps','updateHistory','services')])
        elif command=='component-check':data=dict(state='healthy',at='2026-11-10T12:00:00Z',readOnly=True,mode='recorded-only',success=True)
        elif command=='hardware':data=dict(schema=1,readOnly=True,online=False,at='2026-11-10T12:00:00Z',sections=[dict(id='gpu',status='available',source='Fixture DXGI',items=[dict(name='Fixture GPU',dedicatedVideoBytes=12*1024**3,sharedSystemBytes=16*1024**3,memorySource='DXGI'),dict(name='Fixture fallback',dedicatedVideoBytes=None,memorySource='unavailable')]),dict(id='memory',status='available',source='Fixture CIM',items=[dict(name='DIMM A',capacityBytes=32*1024**3,memoryType=34)]),dict(id='battery',status='empty',source='Fixture CIM',items=[]),dict(id='bios',status='unavailable',source='Fixture CIM',items=[])])
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
    for page in ('home','scanFix','cleanup','drivers','hardware','windowsCare','startup','workshop','tools','history','settings'):
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


@pytest.mark.parametrize('language',['tr','en'])
def test_native_errors_use_human_translations_instead_of_missing_translation_keys(window,language):
    w,_=window;w.settings['language']=language
    for code in ['SCAN_EXPIRED','INVALID_SELECTION','UPDATE_HASH_INVALID']:
        w.error(code)
        assert code in w.notice.text()
        assert 'errorExpired' not in w.notice.text() and 'errorSelection' not in w.notice.text() and 'errorHash' not in w.notice.text()
        assert len(w.notice.text())>len(code)+20


def test_native_log_preserves_distinct_driver_results_even_with_identical_titles(window):
    w,bridge=window;bridge.trace=dict(command='windows-install',status='attention',events=[dict(at='2026-11-10T12:00:00Z',origin='native',action='windows-install',step='install-item',status='failed',item='Same driver title',count=1),dict(at='2026-11-10T12:00:01Z',origin='native',action='windows-install',step='install-item',status='complete',item='Same driver title',count=2)])
    w.poll();assert w.log.topLevelItemCount()==2;assert w.log.topLevelItem(0).text(3)=='Başarısız';assert 'Başarısız: 1' in w.log_hint.text()


@pytest.mark.parametrize('language',['tr','en'])
def test_hardware_scan_search_unknowns_and_export_existing_report(window,application,tmp_path,monkeypatch,language):
    from PySide6.QtWidgets import QTreeWidget, QLineEdit, QFileDialog
    from hardware import format_value
    w,bridge=window;w.settings['language']=language;w.go('hardware')
    assert w.nav_layout.itemAt(4).widget().text()==text(language,'hardware')
    w.findChild(QPushButton,'hardware-scan').click()
    assert len([c for c,_ in bridge.calls if c=='hardware'])==1
    assert format_value('dedicatedVideoBytes',12*1024**3,language,w.t).startswith('12,0' if language=='tr' else '12.0')
    assert format_value('dedicatedVideoBytes',None,language,w.t)==w.t('hw.unknown')
    tree=w.findChild(QTreeWidget,'hardware-tree');assert tree.topLevelItemCount()==4
    assert w.t('hw.emptyStatus') in tree.topLevelItem(2).text(1)
    assert w.t('hw.unavailable') in tree.topLevelItem(3).text(1)
    search=w.findChild(QLineEdit,'hardware-search');search.setText('fixture gpu')
    assert tree.topLevelItemCount()==1 and tree.topLevelItem(0).childCount()==1
    search.setText('');category=w.findChild(QComboBox,'hardware-category');category.setCurrentIndex(category.findData('memory'))
    assert tree.topLevelItemCount()==1 and tree.topLevelItem(0).child(0).child(2).text(1)=='DDR5'
    saved=copy.deepcopy(w.state['hardware']);w.save_setting('theme','dark');w.go('home');w.go('hardware')
    assert w.state['hardware']==saved
    monkeypatch.setattr(w,'export',lambda command:bridge.call(command))
    w.findChild(QPushButton,'hardware-export').click()
    assert ('hardware.export',{}) in bridge.calls
    assert len([c for c,_ in bridge.calls if c=='hardware'])==1

@pytest.mark.parametrize('language',['tr','en'])
def test_hardware_readable_summary_clipboard_text_and_filter_retention(window,application,tmp_path,monkeypatch,language):
    from PySide6.QtWidgets import QLineEdit, QLabel
    from hardware import QFileDialog, summary_text
    w,bridge=window;w.settings['language']=language;w.go('hardware');w.findChild(QPushButton,'hardware-scan').click();application.processEvents()
    report=w.state['hardware'];summary=summary_text(report,language,w.t)
    assert 'bytes' not in summary and '12' in summary and 'GiB' in summary
    w.findChild(QPushButton,'hardware-copy').click();assert application.clipboard().text()==summary
    destination=tmp_path/'donanım.txt'
    monkeypatch.setattr(QFileDialog,'getSaveFileName',lambda *args:(str(destination),'Text (*.txt)'))
    w.findChild(QPushButton,'hardware-text-export').click();exported=destination.read_text(encoding='utf-8')
    assert '12,884,901,888' in exported or '12.884.901.888' in exported
    assert w.t('hw.noProvider') in exported and w.t('hw.noDevices') in exported
    w.findChild(QLineEdit,'hardware-search').setText('no such fixture')
    assert not w.findChild(QObject,'hardware-no-matches').isHidden()
    w.go('home');application.processEvents();w.go('hardware');application.processEvents()
    assert w.findChild(QLineEdit,'hardware-search').text()=='no such fixture'
    w.findChild(QPushButton,'hardware-clear-filter').click()
    assert w.findChild(QLineEdit,'hardware-search').text()==''
    assert w.findChild(QObject,'hardware-no-matches').isHidden()
    assert len([c for c,_ in bridge.calls if c=='hardware'])==1

def test_hardware_progress_uses_actual_native_terminal_categories_and_never_old_trace(window):
    w,bridge=window;w.busy=True;w.active_command='hardware'
    from hardware import CATEGORIES
    events=[dict(origin='native',step='hardware-'+name,status='complete') for name in CATEGORIES[:6]]
    events += [dict(origin='native',step='hardware-bios',status='failed'),dict(origin='native',step='hardware-storage',status='running'),dict(origin='app',step='hardware-devices',status='complete')]
    bridge.trace=dict(command='hardware',status='running',at='2026-11-10T12:00:00Z',events=events);w.poll()
    assert w.progress.maximum()==14 and w.progress.value()==7
    assert '7/14' in w.notice.text() and w.t('hw.storage') in w.notice.text()
    events += [dict(origin='native',step='hardware-cpu',status='complete')];w.poll();assert w.progress.value()==7
    bridge.trace=dict(command='diagnostics.scan',status='running',events=[]);w.poll();assert w.progress.value()==7

def test_collapsing_operation_details_preserves_live_failures_and_preference(window,application):
    w,bridge=window;application.processEvents();before=w.scroll.height()
    w.log_toggle.click();application.processEvents()
    assert w.settings['operationDetails'] is False and w.log_details.isHidden()
    assert w.scroll.height()>before
    bridge.trace=dict(command='hardware',status='attention',events=[dict(origin='native',step='hardware-bios',status='failed')]);w.poll()
    assert 'Başarısız: 1' in w.log_hint.text() and w.trace['events'][0]['status']=='failed'
    w.log_toggle.click();application.processEvents();assert not w.log_details.isHidden()
    assert w.log.topLevelItem(0).text(3)=='Başarısız'


def test_native_installer_handoff_requests_fresh_onefile_payload(window,monkeypatch):
    import app as native_app
    w,_=window;calls=[]
    monkeypatch.setenv('PYINSTALLER_RESET_ENVIRONMENT','0')
    monkeypatch.setattr(native_app.subprocess,'Popen',lambda *args,**kwargs:calls.append((args,kwargs)))
    monkeypatch.setattr(native_app.QTimer,'singleShot',lambda *args:None)
    w.install_app({'installer':'C:/Verified/Setup.exe'})
    args,kwargs=calls[0]
    assert args[0]==['C:/Verified/Setup.exe','/S','--updated','--force-run']
    assert kwargs['env']['PYINSTALLER_RESET_ENVIRONMENT']=='1' and kwargs['close_fds'] is True

def test_native_installer_launch_failure_keeps_interface_available(window,monkeypatch):
    import app as native_app
    w,_=window
    def reject(*args,**kwargs):raise OSError('Controlled launch failure')
    monkeypatch.setattr(native_app.subprocess,'Popen',reject)
    w.install_app({'installer':'C:/Verified/Setup.exe'})
    assert w.last_error=='OPERATION_FAILED' and w.isVisible() and not w.busy
    assert w.t('errorDefault') in w.notice.text()


@pytest.mark.parametrize('language',['tr','en'])
def test_windows_care_scans_once_keeps_unknowns_and_copies_reduced_summary(window,application,language):
    from PySide6.QtWidgets import QTreeWidget,QLineEdit
    w,bridge=window;w.settings['language']=language;w.go('windowsCare');application.processEvents()
    assert w.nav_layout.itemAt(5).widget().text()==w.t('windowsCare')
    w.findChild(QPushButton,'care-scan').click();application.processEvents()
    assert ('care.snapshot',{}) in bridge.calls and w.t('care.review') in w.notice.text()
    tree=w.findChild(QTreeWidget,'care-tree');assert tree.topLevelItemCount()==9
    assert w.t('hw.unavailable') in tree.topLevelItem(1).text(1)
    assert w.t('hw.emptyStatus') in tree.topLevelItem(4).text(1)
    w.findChild(QPushButton,'care-copy').click()
    assert 'private local event message' not in application.clipboard().text()
    assert w.t('care.historyNote') in application.clipboard().text()
    w.findChild(QLineEdit,'care-search').setText('Fixture event');assert tree.topLevelItemCount()==1
    w.go('home');application.processEvents();w.go('windowsCare');application.processEvents()
    assert w.findChild(QLineEdit,'care-search').text()=='Fixture event'
    assert len([c for c,_ in bridge.calls if c=='care.snapshot'])==1

def test_component_check_cancel_never_elevates_and_accept_sends_only_confirmation(window,application):
    w,bridge=window;w.go('windowsCare');application.processEvents()
    QTimer.singleShot(0,lambda:application.activeModalWidget().reject())
    w.findChild(QPushButton,'care-component-check').click();assert not any(c=='component-check' for c,_ in bridge.calls)
    def accept():application.activeModalWidget().findChild(QDialogButtonBox).button(QDialogButtonBox.Ok).click()
    QTimer.singleShot(0,accept);w.findChild(QPushButton,'care-component-check').click()
    assert ('component-check',dict(confirm=True)) in bridge.calls
    assert w.state['componentState']['state']=='healthy'

def test_care_progress_counts_real_category_receipts_and_preserves_failure(window):
    w,bridge=window;w.busy=True;w.active_command='care.snapshot'
    bridge.trace=dict(command='care.snapshot',status='running',events=[dict(origin='native',step='care-readiness',status='complete'),dict(origin='native',step='care-defender',status='failed'),dict(origin='native',step='care-systemEvents',status='complete'),dict(origin='native',step='care-firewall',status='running')])
    w.poll();assert w.progress.maximum()==9 and w.progress.value()==3
    assert w.t('care.firewall') in w.notice.text() and '3/9' in w.notice.text()
    assert 'Başarısız: 1' in w.log_hint.text()
