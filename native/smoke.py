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
        dialog=QApplication.activeModalWidget()
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
                state['scanTrace']=trace
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
                window.settings.update(language='tr',theme='dark',scale=100,textSize=100,font='system',operationDetails=False)
                window.appearance();window.render();state['stage']=10;return
            elif stage==10:
                from hardware import summary_text,text_report,progress_state
                assert window.log_details.isHidden()
                assert progress_state(window.trace)[0]==14
                click('hardware-copy')
                copied=QApplication.clipboard().text()
                assert copied==summary_text(window.state['hardware'],'tr',window.t)
                (evidence/'hardware-summary.txt').write_text(copied,encoding='utf-8')
                (evidence/'hardware-report.txt').write_text(text_report(window.state['hardware'],'tr',window.t),encoding='utf-8')
                window.scroll.verticalScrollBar().setValue(0)
                window.notice.setText(window.t('n.done'))
                window.grab().save(str(evidence/'Windows-Qt-hardware-tr-100.png'))
                window.settings=state['hardwareViewSettings'];window.appearance();window.render()
                window.go('scanFix');state['stage']=11
            elif stage==11:
                report=window.state.get('care');assert report and report['readOnly'] is True and report['online'] is False
                assert len(report['sections'])==9
                for section_id in ('readiness','services'):
                    assert next(s for s in report['sections'] if s['id']==section_id)['status']=='available'
                trace=state['scanTrace']
                assert trace['command']=='diagnostics.scan' and trace['status']!='running'
                terminal=[e for e in trace.get('events',[]) if e.get('origin')=='native' and e.get('step','').startswith('care-') and e.get('status') in ('complete','failed')]
                assert len(terminal)==9,terminal
                (evidence/'operation-care.json').write_text(json.dumps(trace,indent=2),encoding='utf-8')
                window.bridge.call('care.export',callback=lambda reply:state.update(careExport=reply))
                state['stage']=12
            elif stage==12:
                reply=state.get('careExport')
                if not reply:return
                assert reply['ok'];safe=reply['data'];assert safe['eventMessagesOmitted'] is True
                assert len(safe['sections'])==9
                for section in safe['sections']:
                    assert len(section['items'])<=100
                    for row in section['items']:assert 'message' not in row
                (evidence/'care-support.json').write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding='utf-8')
                state['careViewSettings']=dict(window.settings)
                window.settings.update(language='tr',theme='dark',scale=100,textSize=100,font='system',operationDetails=False)
                window.appearance();window.render();window.poll();state['stage']=13
            elif stage==13:
                from care import summary
                assert window.findChild(QPushButton,'nav-windowsCare') is None
                assert not any(s.get('step')=='care.snapshot' for s in state['scanTrace']['events'])
                click('care-copy');copied=QApplication.clipboard().text()
                assert copied==summary(window.state['care'],'tr',window.t)
                (evidence/'care-summary.txt').write_text(copied,encoding='utf-8')
                window.scroll.verticalScrollBar().setValue(0)
                window.notice.setText(window.t('care.review' if window.state['care'].get('needsAttention') else 'n.done'))
                window.grab().save(str(evidence/'Windows-Qt-unified-scan-tr-100.png'))
                window.go('tools');state['stage']=14
            elif stage==14:
                from PySide6.QtWidgets import QTreeWidget
                tree=window.findChild(QTreeWidget,'tools-records-tree');assert tree and tree.topLevelItemCount()==3
                assert window.findChild(QPushButton,'care-component-check')
                window.scroll.verticalScrollBar().setValue(0)
                window.grab().save(str(evidence/'Windows-Qt-unified-tools-tr-100.png'))
                window.go('home');state['stage']=15
            elif stage==15:
                from PySide6.QtWidgets import QGroupBox
                assert any(g.title()==window.t('care.homeStatus') for g in window.findChildren(QGroupBox))
                window.grab().save(str(evidence/'Windows-Qt-unified-home-tr-100.png'))
                window.go('history');state['stage']=16
            elif stage==16:
                from PySide6.QtWidgets import QTreeWidget
                assert window.findChild(QTreeWidget,'update-records-tree').topLevelItemCount()==1
                window.grab().save(str(evidence/'Windows-Qt-unified-history-tr-100.png'))
                (evidence/'unified-scan.json').write_text(json.dumps(dict(sharedScanId=window.state['report']['id'],separateDonorTab=False,sharedCategories=9,pages=['scanFix','tools','home','history'],verified=True),indent=2),encoding='utf-8')
                window.settings.update(language='tr',theme='dark',scale=100,textSize=100,font='system',operationDetails=False,gamification=True)
                window.appearance();window.go('home');state['stage']=17
            elif stage==17:
                from PySide6.QtWidgets import QGroupBox,QProgressBar,QWidget
                from journey import STEPS
                panel=window.scroll.widget().findChild(QGroupBox,'care-journey');assert panel
                completed=window.state.get('milestones',[])
                done=sum(key in completed for key,_,_,_ in STEPS)
                assert panel.findChild(QProgressBar,'journey-progress').value()==done
                for key,_,_,_ in STEPS:assert panel.findChild(QWidget,'journey-step-'+key)
                if scenario in ('seed','verify'):assert 'health' in completed and 'scan' in completed
                state['journeyMilestones']=list(completed)
                state['journeyNext']=next((item for item in STEPS if item[0] not in completed),None)
                window.scroll.verticalScrollBar().setValue(0)
                window.grab().save(str(evidence/'Windows-Qt-journey-tr-100.png'))
                if state['journeyNext']:click('journey-next');state['stage']=18
                else:state['stage']=19
            elif stage==18:
                key,title,page,name=state['journeyNext']
                target=window.scroll.widget().findChild(QPushButton,name)
                assert window.page==page and window.focusWidget()==target
                assert window.scroll.viewport().rect().contains(target.mapTo(window.scroll.viewport(),target.rect().center()))
                assert target.text() in window.notice.text()
                window.grab().save(str(evidence/'Windows-Qt-journey-target-tr-100.png'))
                click('journey-return');state['stage']=19
            elif stage==19:
                from PySide6.QtWidgets import QProgressBar
                assert window.page=='home' and window.state.get('milestones',[])==state['journeyMilestones']
                assert window.scroll.widget().findChild(QProgressBar,'journey-progress').value()==len(state['journeyMilestones'])
                (evidence/'journey-navigation.json').write_text(json.dumps(dict(milestones=state['journeyMilestones'],steps=['health','scan','drivers'],nextStep=state['journeyNext'][0] if state['journeyNext'] else None,navigationDidNotCompleteTasks=True,actualServiceHistory=True,verified=True),indent=2),encoding='utf-8')
                window.settings=state['careViewSettings'];window.appearance();window.render()
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
