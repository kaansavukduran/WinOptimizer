"""Opt-in packaged UI self-test. Only --smoke activates it; never normal startup."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QPushButton, QCheckBox, QDialog, QDialogButtonBox

def start(window, scenario):
    evidence=Path(os.environ.get('AION_EVIDENCE',str(Path.cwd()/'work/native-evidence')))
    evidence.mkdir(parents=True,exist_ok=True)
    began=time.time()
    state={'stage':0}
    timer=QTimer(window)
    timer.setInterval(150)
    def click(name):
        button=window.findChild(QPushButton,name)
        if not button or not button.isEnabled():raise AssertionError('Button unavailable: '+name)
        button.click()
    def accept():
        dialog=window.findChild(QDialog,'confirm-dialog')
        if not dialog:raise AssertionError('Expected real confirmation dialog')
        dialog.findChild(QDialogButtonBox).button(QDialogButtonBox.Ok).click()
    def advance():
        try:
            if time.time()-began>240:raise AssertionError('NATIVE_SMOKE_TIMEOUT stage='+str(state['stage']))
            if not window.ready or window.busy:return
            stage=state['stage']
            if stage==0:
                if scenario=='verify':
                    for key,value in [('scale',135),('textSize',125),('font','dyslexic'),('theme','dark'),('language','en')]:assert window.settings[key]==value,(key,window.settings)
                if scenario in ('portable','reopen'):
                    assert window.portable
                    if scenario=='reopen':assert window.settings['theme']=='dark'
                    assert window.data.name=='WinOptimizer Aion' and window.data.parent.name=='Data'
                state['original']=dict(window.settings)
                state['fixture']=Path(os.environ['LOCALAPPDATA'])/'Temp'/('WinOptimizer-native-qt-'+str(os.getpid())+'.tmp')
                window.go('home');click('health-scan');state['stage']=1
            elif stage==1:
                assert 'Windows' in window.state['health']['os']
                window.go('scanFix');window.scan_online=False;click('start-scan');state['stage']=2
            elif stage==2:
                assert window.state['report']['online'] is False
                trace=window.trace or {}
                # Poll once after completion; then inspect actual native events, not a UI fixture.
                if trace.get('command')!='diagnostics.scan' or trace.get('status')=='running':return
                events=trace.get('events',[])
                assert any(e.get('origin')=='native' and e.get('step')=='devices' and e.get('status') in ('complete','failed') for e in events),events
                assert any(e.get('step')=='windows-updates' and e.get('status')=='skipped' and e.get('reason')=='offline' for e in events),events
                (evidence/'operation-scan.json').write_text(json.dumps(trace,indent=2),encoding='utf-8')
                window.grab().save(str(evidence/'Windows-Qt-scan.png'))
                if scenario in ('verify','portable','reopen'):
                    state['stage']=7
                    return
                fixture=state['fixture'];fixture.parent.mkdir(exist_ok=True);fixture.write_text('Native Qt cleanup restore sample',encoding='utf-8');old=time.time()-9*86400;os.utime(fixture,(old,old))
                window.go('cleanup');click('cleanup-scan');state['stage']=3
            elif stage==3:
                assert window.state['cleanup']['count']>=1
                QTimer.singleShot(100,accept);state['stage']=4;click('cleanup-apply')
            elif stage==4:
                assert not state['fixture'].exists()
                window.go('history');state['stage']=5
            elif stage==5:
                history=window.state.get('history',{})
                if not history.get('cleanup'):return
                item=history['cleanup'][0];click('restore-'+item['id']);state['stage']=6
            elif stage==6:
                assert state['fixture'].read_text(encoding='utf-8')=='Native Qt cleanup restore sample';state['fixture'].unlink()
                for key,value in [('language','en'),('theme','dark'),('scale',135),('textSize',125),('font','dyslexic')]:window.save_setting(key,value)
                state['stage']=7
            elif stage==7:
                settings=json.loads((window.data/'settings.json').read_text(encoding='utf-8')) if (window.data/'settings.json').exists() else window.settings
                if scenario=='seed':
                    for key,value in [('scale',135),('theme','dark'),('font','dyslexic'),('textSize',125)]:
                        if settings.get(key)!=value:return
                window.go('home');window.grab().save(str(evidence/'Windows-Qt-overview.png'))
                state['settings']=settings
                window.go('hardware');click('hardware-scan');state['stage']=9
            elif stage==9:
                report=window.state.get('hardware');assert report and report['readOnly'] is True and report['online'] is False
                sections=report['sections'];assert len(sections)==14
                for section_id in ('cpu','system','storage'):
                    section=next(s for s in sections if s['id']==section_id)
                    assert section['status']=='available' and section['items'],section
                trace=window.trace or {}
                if trace.get('command')!='hardware' or trace.get('status')=='running':return
                terminal=[e for e in trace.get('events',[]) if e.get('origin')=='native' and e.get('step','').startswith('hardware-') and e.get('status') in ('complete','failed')]
                assert len(terminal)==14,terminal
                (evidence/'hardware-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
                (evidence/'operation-hardware.json').write_text(json.dumps(trace,ensure_ascii=False,indent=2),encoding='utf-8')
                window.grab().save(str(evidence/'Windows-Qt-hardware.png'))
                state['hardwareViewSettings']=dict(window.settings)
                window.settings.update(language='tr',theme='dark',scale=100,textSize=100,font='system')
                window.appearance();window.render();state['stage']=10;return
            elif stage==10:
                window.scroll.verticalScrollBar().setValue(0)
                window.grab().save(str(evidence/'Windows-Qt-hardware-tr-100.png'))
                window.settings=state['hardwareViewSettings'];window.appearance();window.render()
                if scenario=='portable':
                    window.save_setting('theme','dark');state['stage']=8;return
                finish(state['settings'])
            elif stage==8:
                settings=json.loads((window.data/'settings.json').read_text(encoding='utf-8'))
                if settings.get('theme')!='dark':return
                finish(settings)
        except Exception as error:
            timer.stop()
            (evidence/'FAILED.json').write_text(json.dumps({'scenario':scenario,'stage':state['stage'],'error':repr(error),'notice':window.notice.text()},indent=2),encoding='utf-8')
            window.bridge.close();QApplication.exit(1)
    def finish(settings):
        timer.stop()
        from app import VERSION
        (evidence/f'verified-{scenario}.json').write_text(json.dumps(dict(version=VERSION,scenario=scenario,engine='Qt Widgets',portable=window.portable,data=str(window.data),settings=settings,verified=True),ensure_ascii=False,indent=2),encoding='utf-8')
        window.close()
    timer.timeout.connect(advance)
    timer.start()
