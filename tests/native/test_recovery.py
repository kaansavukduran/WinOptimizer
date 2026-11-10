import copy
import json
from pathlib import Path
import sys
import time
import pytest
from PySide6.QtWidgets import QPushButton, QGroupBox
from PySide6.QtCore import QProcess
from test_interface import application, window, FixtureBridge
from app import Window
from bridge import Bridge
from recovery import guidance


def until(application, predicate):
    deadline = time.monotonic() + 5
    while not predicate() and time.monotonic() < deadline:
        application.processEvents()
        time.sleep(.005)
    assert predicate()


@pytest.fixture
def protocol_bridge(application, tmp_path):
    desktop = tmp_path / 'desktop'
    desktop.mkdir()
    (desktop / 'native-bridge.cjs').write_text('''import json,sys
for line in sys.stdin:
 r=json.loads(line)
 if r['command']=='exit':sys.exit(3)
 if r['command']=='bad':print('[]',flush=True);continue
 print(json.dumps(dict(id=r['id'],ok=True,data=r['payload'])),flush=True)
''', encoding='utf-8')
    bridge = Bridge(tmp_path, tmp_path, False, 'en', sys.executable)
    yield bridge
    bridge.close()


def test_starting_request_and_disconnect_settle_once_without_pending_growth(application, protocol_bridge):
    bridge = protocol_bridge
    replies, failures = [], []
    bridge.failed.connect(failures.append)
    bridge.call('read', {'sample': 1}, replies.append)
    until(application, lambda: bool(replies))
    assert replies == [dict(id=1, ok=True, data={'sample': 1})]
    bridge.call('exit', callback=replies.append)
    until(application, lambda: bool(failures))
    assert replies[-1] == dict(ok=False, error='BACKEND_DISCONNECTED')
    assert len(replies) == 2 and failures == ['BACKEND_DISCONNECTED']
    for _ in range(30):
        bridge.call('operation.status', callback=replies.append)
    assert len(replies) == 32 and not bridge.pending
    assert failures == ['BACKEND_DISCONNECTED']


def test_missing_process_fails_bootstrap_and_later_requests(application, tmp_path):
    bridge = Bridge(tmp_path, tmp_path, False, 'en', tmp_path / 'does-not-exist.exe')
    replies, failures = [], []
    bridge.failed.connect(failures.append)
    bridge.call('bootstrap', callback=replies.append)
    until(application, lambda: bool(replies))
    assert replies == [dict(ok=False, error='BACKEND_UNAVAILABLE')]
    assert failures == ['BACKEND_UNAVAILABLE'] and not bridge.pending
    bridge.call('hardware', callback=replies.append)
    assert len(replies) == 2
    bridge.close()
    assert failures == ['BACKEND_UNAVAILABLE']


def test_bad_envelope_fails_pending_without_replaying(application, protocol_bridge):
    replies = []
    protocol_bridge.call('bad', callback=replies.append)
    until(application, lambda: bool(replies))
    assert replies == [dict(ok=False, error='BACKEND_PROTOCOL_FAILED')]
    assert protocol_bridge.unavailable and not protocol_bridge.pending


def test_normal_close_has_no_unexpected_disconnect_signal(application, protocol_bridge):
    bridge = protocol_bridge
    until(application, lambda: bridge.has_started)
    failures = []
    bridge.failed.connect(failures.append)
    bridge.close()
    assert bridge.process.state() == QProcess.NotRunning
    assert not failures and not bridge.pending


def test_ui_callback_exception_is_not_misreported_as_protocol_failure(application, protocol_bridge):
    bridge = protocol_bridge
    until(application, lambda: bridge.has_started)
    bridge.process.blockSignals(True)
    def callback(_):
        raise ValueError('UI callback failure')
    bridge.call('read', callback=callback)
    bridge.process.waitForBytesWritten(2000)
    assert bridge.process.waitForReadyRead(2000)
    with pytest.raises(ValueError, match='UI callback failure'):
        bridge.read()
    assert not bridge.unavailable and not bridge.pending
    bridge.process.blockSignals(False)


@pytest.mark.parametrize('language', ['tr', 'en'])
def test_read_failure_retries_only_its_snapshot_and_preserves_results(window, application, language):
    w, bridge = window
    w.settings['language'] = language
    w.go('scanFix')
    w.state['report'] = dict(id='previous', findings=[])
    original = bridge.call
    failures = [True]
    def call(command, payload=None, callback=None):
        if command == 'diagnostics.scan' and failures:
            failures.pop();bridge.calls.append((command, copy.deepcopy(payload)))
            callback(dict(ok=False, error='OPERATION_TIMEOUT'))
        else:
            original(command, payload, callback)
    bridge.call = call
    payload = {'online': False}
    w.run('diagnostics.scan', payload, lambda r: w.store('report', r))
    payload['online'] = True
    assert not w.busy and w.state['report']['id'] == 'previous'
    assert w.scroll.widget().findChild(QGroupBox, 'operation-recovery')
    w.go('hardware')
    w.scroll.widget().findChild(QPushButton, 'recovery-retry').click()
    assert w.page == 'scanFix' and w.state['report']['online'] is False
    assert [p for c,p in bridge.calls if c=='diagnostics.scan'] == [{'online':False}, {'online':False}]
    assert w.failure is None


@pytest.mark.parametrize('command', ['diagnostics.updates', 'cleanup', 'runtime.install', 'driver-backup'])
def test_mutations_have_navigation_only_and_never_replay(window, command):
    w, bridge = window
    w.go('workshop')
    original = bridge.call
    def call(cmd, payload=None, callback=None):
        if cmd == command:
            bridge.calls.append((cmd, copy.deepcopy(payload)))
            callback(dict(ok=False, error='OPERATION_TIMEOUT'))
        else:original(cmd, payload, callback)
    bridge.call = call
    w.run(command, dict(confirm=True, privatePath='private-local-path'))
    panel = w.scroll.widget().findChild(QGroupBox, 'operation-recovery')
    assert panel and panel.findChild(QPushButton, 'recovery-retry') is None
    before = copy.deepcopy(bridge.calls)
    panel.findChild(QPushButton, 'recovery-copy').click()
    from PySide6.QtWidgets import QApplication
    assert 'private-local-path' not in QApplication.clipboard().text()
    assert 'confirm' not in QApplication.clipboard().text()
    panel.findChild(QPushButton, 'recovery-origin').click()
    assert bridge.calls == before and w.page == 'workshop'


def test_disconnect_retains_reports_stops_polling_and_keeps_mutation_context(window):
    w, bridge = window
    w.state['report'] = dict(id='saved', findings=[])
    w.state['milestones'] = ['health', 'scan']
    request = dict(command='diagnostics.updates', page='scanFix', settings_section='general')
    w.error('BACKEND_DISCONNECTED', request)
    bridge.failed.emit('BACKEND_DISCONNECTED')
    w.error('BACKEND_DISCONNECTED')  # a settings write cannot erase the affected operation
    assert w.failure['request'] == request
    assert not w.poller.isActive() and w.backend_lost
    before = len(bridge.calls)
    w.poll()
    assert len(bridge.calls) == before
    panel = w.scroll.widget().findChild(QGroupBox, 'operation-recovery')
    assert panel and not panel.findChild(QPushButton, 'recovery-retry')
    message, retry = guidance(w.failure, 'tr', True)
    assert 'doğrulanamadı' in message and not retry
    assert w.state['report']['id'] == 'saved' and w.state['milestones'] == ['health', 'scan']


def test_startup_failure_shows_actionable_shell(application, tmp_path):
    class MissingBridge(FixtureBridge):
        def call(self, command, payload=None, callback=None):
            if callback:callback(dict(ok=False, error='BACKEND_UNAVAILABLE'))
    w = Window(MissingBridge({}), tmp_path)
    w.show();application.processEvents()
    assert not w.ready and not w.busy and not w.poller.isActive()
    assert w.scroll.widget().findChild(QPushButton, 'recovery-close')
    assert not w.scroll.widget().findChild(QPushButton, 'recovery-retry')
    w.close()


def test_retry_restores_update_section_but_requestless_error_never_retries_old_install(window):
    w, _ = window
    w.page, w.settings_section = 'settings', 'updates'
    request = dict(command='updates.check', payload=None, callback=lambda r:w.store('appUpdate',r), silent=False, page='settings',settings_section='updates')
    w.error('OPERATION_TIMEOUT',request)
    w.settings_section = 'appearance'
    w.render()
    w.scroll.widget().findChild(QPushButton,'recovery-retry').click()
    assert w.settings_section == 'updates' and w.state.get('appUpdate')
    w.last_request = ('updates.install', {'confirm':True}, None, False)
    w.error('OPERATION_FAILED')
    assert w.failure['request'] is None
    assert not w.scroll.widget().findChild(QPushButton,'recovery-retry')


@pytest.mark.parametrize('language', ['tr', 'en'])
def test_recovery_remains_scrollable_at_large_text_and_cancel_keeps_report(window, application, language):
    w,_ = window
    w.settings.update(language=language,scale=200,textSize=125,font='dyslexic')
    w.resize(540,900);w.appearance()
    w.state['report'] = dict(id='previous',findings=[])
    w.error('SCAN_CANCELLED',dict(command='diagnostics.scan',payload={'online':False},callback=None,silent=False,page='scanFix',settings_section='general'))
    application.processEvents()
    assert w.scroll.verticalScrollBar().maximum()>0
    button=w.scroll.widget().findChild(QPushButton,'recovery-retry')
    assert button and button.isEnabled()
    def visible():
        w.scroll.ensureWidgetVisible(button)
        application.processEvents()
        return w.scroll.viewport().rect().contains(button.mapTo(w.scroll.viewport(),button.rect().center()))
    until(application, visible)
    assert w.state['report']['id']=='previous'
