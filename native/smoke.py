"""Opt-in packaged UI self-test. Only --smoke activates it; never normal startup."""
import hashlib
import math
import json
import os
from pathlib import Path
import sys
import time
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QPushButton, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QTreeWidget, QLineEdit

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
            if time.time()-began>360:raise AssertionError('NATIVE_SMOKE_TIMEOUT stage='+str(state['stage']))
            if not window.ready or window.busy:return
            stage=state['stage']
            if stage==0:
                if scenario in ('seed','portable'):
                    assert window.settings['theme']=='dark' and window.settings['font']=='system',('Fresh AIONIA defaults',window.settings)
                    (evidence/'first-launch.json').write_text(json.dumps(dict(verified=True,actualPackagedWindows=True,theme=window.settings['theme'],font=window.settings['font'],scenario=scenario)),encoding='utf-8')
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
                tree=window.findChild(QTreeWidget,'tools-records-tree');assert tree and tree.topLevelItemCount()==3
                assert window.findChild(QPushButton,'care-component-check')
                window.scroll.verticalScrollBar().setValue(0)
                window.grab().save(str(evidence/'Windows-Qt-unified-tools-tr-100.png'))
                window.go('home');state['stage']=15
            elif stage==15:
                from PySide6.QtWidgets import QGroupBox
                assert any(g.accessibleName()==window.t('care.homeStatus') for g in window.scroll.widget().findChildren(QGroupBox))
                window.grab().save(str(evidence/'Windows-Qt-unified-home-tr-100.png'))
                window.go('history');state['stage']=16
            elif stage==16:
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
            elif stage==20:
                if not window.backend_lost:return
                from PySide6.QtWidgets import QGroupBox
                panel=window.scroll.widget().findChild(QGroupBox,'operation-recovery')
                assert panel and not window.busy and not window.poller.isActive()
                assert panel.findChild(QPushButton,'recovery-retry') is None
                assert window.state['report']['id']==state['recoveryReport']
                assert window.state['milestones']==state['recoveryMilestones']
                # A new request after the child died must fail immediately, not spin forever.
                window.run('hardware')
                assert not window.busy and window.last_error=='BACKEND_DISCONNECTED'
                assert not window.bridge.pending
                assert window.state['hardware']==state['recoveryHardware']
                window.settings.update(language='tr',theme='dark',scale=100,textSize=100,font='system',operationDetails=False)
                window.appearance();window.render();window.scroll.verticalScrollBar().setValue(0)
                state['stage']=21
            elif stage==21:
                window.grab().save(str(evidence/'Windows-Qt-recovery-tr-100.png'))
                (evidence/'backend-recovery.json').write_text(json.dumps(dict(verified=True,actualPackagedChild=True,intentionalIdleFailure=True,requestsFailImmediately=True,pending=0,pollingStopped=True,reportsPreserved=True,milestonesPreserved=True,noAutomaticReplay=True),indent=2),encoding='utf-8')
                state['recoveryChecked']=True
                finish(state['finalSettings'])
            elif stage==22:
                state['personalOriginal']=dict(window.settings)
                state['personalMilestones']=list(window.state['milestones'])
                window.settings.update(language='tr',theme='dark',scale=100,textSize=100,font='system',motion=True,followPointer=False,operationDetails=False)
                window.appearance();window.settings_section='appearance';window.page='settings';window.render()
                combo=window.scroll.widget().findChild(QComboBox,'setting-font');assert combo
                combo.setCurrentIndex(combo.findData('dyslexic'));click('accent-preset-blue');state['stage']=23
            elif stage==23:
                stored=json.loads((window.data/'settings.json').read_text(encoding='utf-8'))
                if stored.get('font')!='dyslexic' or stored.get('accent')!='#066f82':return
                assert window.font().family()=='OpenDyslexic'
                from PySide6.QtGui import QRawFont
                raw=QRawFont.fromFont(window.font());assert all(raw.supportsCharacter(ord(c)) for c in 'ÇĞİÖŞÜçğıöşü')
                window.scroll.verticalScrollBar().setValue(0)
                window.grab().save(str(evidence/'Windows-Qt-personalize-tr-100.png'))
                window.scroll.ensureWidgetVisible(window.scroll.widget().findChild(QPushButton,'accent-picker'))
                state.update(galleryIndex=0,gallery=[],stage=28)
            elif stage==28:
                window.grab().save(str(evidence/'Windows-Qt-personalize-colors.png'))
                state['stage']=24
            elif stage==24:
                from mascot import PAGE_CLIPS
                page=list(PAGE_CLIPS)[state['galleryIndex']]
                window.page=page;window.render();window.activateWindow();window.raise_()
                window.scroll.ensureWidgetVisible(window.aion)
                state.update(galleryPage=page,galleryAt=time.time(),galleryFirst=window.aion.frame_source()[1].x(),stage=25)
            elif stage==25:
                window.scroll.ensureWidgetVisible(window.aion)
                if time.time()-state['galleryAt']<.5:return
                moving=window.aion.motion();changed=window.aion.frame_source()[1].x()!=state['galleryFirst']
                if moving and not changed and time.time()-state['galleryAt']<3:return
                assert not moving or changed
                assert window.aion.page==state['galleryPage']
                window.grab().save(str(evidence/('Windows-Qt-Aion-'+state['galleryPage']+'.png')))
                state['gallery'].append(dict(page=state['galleryPage'],motionAvailable=moving,clockAdvanced=changed,visible=window.aion.isVisible()))
                state['galleryIndex']+=1
                if state['galleryIndex']<10:state['stage']=24;return
                window.page='settings';window.settings_section='gameSettings';window.render()
                window.scroll.widget().findChild(QCheckBox,'setting-motion').setChecked(False)
                window.scroll.widget().findChild(QCheckBox,'setting-companion').setChecked(False)
                state['stage']=26
            elif stage==26:
                stored=json.loads((window.data/'settings.json').read_text(encoding='utf-8'))
                if stored.get('motion') is not False or stored.get('companion') is not False:return
                assert window.aion.isHidden() and not window.aion.motion()
                assert window.state['milestones']==state['personalMilestones']
                window.settings=state['personalOriginal'];window.save_setting('theme',window.settings['theme']);state['stage']=27
            elif stage==27:
                stored=json.loads((window.data/'settings.json').read_text(encoding='utf-8'))
                if stored!=state['personalOriginal']:return
                (evidence/'personalization.json').write_text(json.dumps(dict(verified=True,bundledTurkishGlyphs=True,realFontAndAccentControls=True,settingsRestored=True,milestonesUnchanged=True,animationOffAndCompanionOffVerified=True,pages=state['gallery']),indent=2),encoding='utf-8')
                window.appearance();window.render();state['personalizeChecked']=True
                finish(state['personalFinalSettings'])
            elif stage==29:
                state['driverViewPreferences']=dict(window.settings)
                state['driverMilestones']=list(window.state['milestones'])
                window.settings.update(language='tr',theme='dark',scale=100,textSize=100,font='system',operationDetails=False)
                window.appearance();window.page='drivers';window.driver_section='inventory';window.render()
                click('driver-inventory');state['stage']=30
            elif stage==30:
                rows=window.state.get('drivers');assert rows and all('name' in r and 'version' in r for r in rows)
                search=window.scroll.widget().findChild(QLineEdit,'driver-search');assert search
                search.setText(rows[0]['name'][:8]);tree=window.scroll.widget().findChild(QTreeWidget,'driver-inventory-tree');assert 0<tree.topLevelItemCount()<=len(rows)
                window.scroll.ensureWidgetVisible(tree)
                state['driverCount']=len(rows);state['stage']=31
            elif stage==31:
                window.grab().save(str(evidence/'Windows-Qt-driver-inventory.png'))
                picker=window.scroll.widget().findChild(QComboBox,'driver-section');picker.setCurrentIndex(picker.findData('backups'));state['stage']=32
            elif stage==32:
                assert 'library' in window.state
                import tempfile
                fixture=Path(tempfile.mkdtemp(prefix='aion-driver-inspect-'))
                (fixture/'unsigned-fixture.inf').write_text('[Version]\nClass=Net\nProvider=WinOptimizer smoke fixture\nDriverVer=11/11/2026,1.0\n',encoding='utf-8')
                state['driverImportFixture']=fixture
                window.state['packageSource']=window.t('dc.imported')
                from driver_center import imported
                window.run('package.import',dict(directory=str(fixture)),lambda r:imported(window,r));state['stage']=33
            elif stage==33:
                plan=window.state.get('package');assert plan and len(plan['candidates'])==1
                assert all(r.get('eligible') is False and r.get('signed') is False for r in plan['candidates'])
                assert not window.scroll.widget().findChild(QPushButton,'driver-package-apply').isEnabled()
                tree=window.scroll.widget().findChild(QTreeWidget,'driver-package-tree');assert not tree.topLevelItem(0).flags() & Qt.ItemIsUserCheckable
                window.scroll.ensureWidgetVisible(tree);state['driverTestPackageId']=plan['libraryId'];state['stage']=34
            elif stage==34:
                window.grab().save(str(evidence/'Windows-Qt-driver-package-blocked.png'))
                # Remove only this invocation's uniquely created, unsigned test import.
                import re,shutil
                parts=state['driverTestPackageId'].split('/')
                assert len(parts)==2 and parts[0]=='DriverPackages' and re.fullmatch(r'[a-f0-9-]{36}',parts[1])
                owned=window.data/'DriverPackages'/parts[1]
                assert owned.parent.resolve()==(window.data/'DriverPackages').resolve()
                shutil.rmtree(owned);shutil.rmtree(state['driverImportFixture'])
                for key in ('package','packageSource','library'):window.state.pop(key,None)
                window.driver_section='offline';window.render();click('driver-offline-read');state['stage']=35
            elif stage==35:
                assert window.state.get('offline',{}).get('devices')
                window.driver_section='ignored';window.render();click('driver-ignored-refresh');state['stage']=36
            elif stage==36:
                assert 'ignored' in window.state['library']
                window.page='workshop';window.workshop_section='points';window.render();assert window.scroll.widget().findChild(QPushButton,'w.listPoints')
                window.workshop_section='focus';window.render();assert window.scroll.widget().findChild(QPushButton,'w.loadFocus')
                assert window.state['milestones']==state['driverMilestones']
                (evidence/'driver-center.json').write_text(json.dumps(dict(verified=True,actualDriverRows=state['driverCount'],realUnsignedImportBlocked=True,noDriverInstalled=True,ownedFixtureRemoved=True,offlineInventory=True,ignoredLibrary=True,workshopCategories=True,milestonesUnchanged=True),indent=2),encoding='utf-8')
                window.settings=state['driverViewPreferences'];window.driver_section='updates';window.workshop_section='runtimes';window.appearance();window.render()
                state['driverCenterChecked']=True;finish(state['driverFinalSettings'])
            elif stage==37:
                state['usabilityPreferences']=dict(window.settings)
                state['usabilitySize']=(window.width(),window.height())
                state['usabilityMilestones']=list(window.state['milestones'])
                window.settings.update(language='tr',theme='dark',accent='#ffffff',scale=150,textSize=125,font='dyslexic',operationDetails=False)
                window.resize(540,900);window.appearance();window.page='home';window.render()
                window.activateWindow();window.raise_();state['stage']=38
            elif stage==38:
                from usability import PAGES
                from personalize import contrast
                assert window.compact_nav.isVisible() and not window.nav_scroll.isVisible()
                assert [window.page_picker.itemData(i) for i in range(10)]==list(PAGES)
                t=window.visual_tokens
                assert min(contrast(t['focus'],t[s]) for s in ['background','surface'])>=3
                QTest.keyClick(window,Qt.Key_5,Qt.ControlModifier)
                assert window.page=='hardware' and window.page_picker.currentData()=='hardware'
                window.grab().save(str(evidence/'Windows-Qt-compact-navigation.png'))
                QTest.keyClick(window,Qt.Key_F1);assert window.help_dialog
                state['stage']=39
            elif stage==39:
                assert window.help_dialog.isVisible()
                window.help_dialog.grab().save(str(evidence/'Windows-Qt-usage-guide.png'))
                QTest.keyClick(window.help_dialog,Qt.Key_Escape);assert window.help_dialog is None
                assert window.state['milestones']==state['usabilityMilestones']
                window.settings=state['usabilityPreferences'];window.resize(*state['usabilitySize']);window.appearance();window.render()
                (evidence/'aionia-usability.json').write_text(json.dumps(dict(verified=True,standard='AIONIA 1.1',actualPackagedQt=True,compactNavigationAllTenPages=True,realKeyboardNavigation=True,localizedContextHelp=True,focusContrastVerified=True,preferencesRestored=True,milestonesUnchanged=True),indent=2),encoding='utf-8')
                state['usabilityChecked']=True;finish(state['usabilityFinalSettings'])
            elif stage==40:
                state['layoutPreferences']=dict(window.settings)
                state['layoutSize']=(window.width(),window.height())
                state['layoutSettingsSection']=window.settings_section
                state['layoutMilestones']=list(window.state['milestones'])
                state['layoutPages']=list(__import__('usability').PAGES)
                state['layoutProfiles']=[dict(id='wide-light-tr',width=1240,language='tr',theme='light',scale=100,textSize=100),dict(id='compact-dark-en',width=540,language='en',theme='dark',scale=100,textSize=100),dict(id='large-dark-tr',width=540,language='tr',theme='dark',scale=200,textSize=125),dict(id='large-light-en',width=540,language='en',theme='light',scale=200,textSize=125),dict(id='wide-dark-system-tr',width=1600,language='tr',theme='dark',font='system',scale=100,textSize=100)]
                state.update(layoutIndex=0,layoutRows=[],stage=41)
            elif stage==41:
                index=state['layoutIndex'];profile=state['layoutProfiles'][index//10];page=state['layoutPages'][index%10]
                window.settings.update({k:v for k,v in profile.items() if k not in ('id','width')})
                window.settings.update(font=profile.get('font','dyslexic'),operationDetails=False,motion=False)
                window.resize(profile['width'],900);window.appearance();window.page=page
                if page=='settings':window.settings_section='appearance'
                began_render=time.perf_counter();window.render();state['layoutRenderMs']=(time.perf_counter()-began_render)*1000
                window.notice.setText(window.t('ux.ready'));window.scroll.verticalScrollBar().setValue(0)
                state.update(layoutProfile=profile,layoutPage=page,stage=42)
            elif stage==42:
                # Real Qt geometry after its deferred text layout, not only a pixel diff.
                assert window.scroll.horizontalScrollBar().maximum()==0,(state['layoutProfile'],state['layoutPage'],window.scroll.widget().width(),window.scroll.viewport().width())
                from widgets import Button,ActionRow
                from PySide6.QtCore import QPoint
                buttons=window.scroll.widget().findChildren(QPushButton)
                assert sum(bool(b.property('primary')) for b in buttons)<=1
                assert all(b.height()>=b.heightForWidth(b.width()) for b in buttons if isinstance(b,Button) and b.isVisible())
                assert state['layoutRenderMs']<=2000,('Synchronous Qt render exceeded the predeclared 2000 ms CI budget',state['layoutRenderMs'])
                profile,page=state['layoutProfile'],state['layoutPage']
                content=window.scroll.widget();viewport=window.scroll.viewport()
                offset=content.mapTo(viewport,QPoint(0,0)).x()
                assert abs(2*offset+content.width()-viewport.width())<=2,('Content is not optically centered',offset,content.width(),viewport.width())
                rows=content.findChildren(ActionRow)
                assert len({r.action.width() for r in rows})<=1,('Unequal equivalent care actions',[(r.action.text(),r.action.width()) for r in rows])
                assert all(r.row.direction()==r.row.TopToBottom or r.copy.width()>=r.width()/2 for r in rows)
                window.grab().save(str(evidence/('Windows-Qt-layout-'+profile['id']+'-'+page+'.png')))
                if page=='settings' and profile['scale']==200:
                    from PySide6.QtWidgets import QSpinBox
                    for button in buttons:
                        if '%' in button.text() or button.objectName().startswith('accent-preset-'):
                            word=max(button.text().split(),key=button.fontMetrics().horizontalAdvance)
                            assert button.fontMetrics().horizontalAdvance(word)<=button.width()-2*button.margin()
                    target=window.scroll.widget().findChild(QSpinBox,'setting-scale');assert target
                    window.scroll.ensureWidgetVisible(target)
                    window.grab().save(str(evidence/('Windows-Qt-layout-'+profile['id']+'-settings-scale.png')))
                state['layoutRows'].append(dict(profile=profile['id'],page=page,requestedWidth=profile['width'],actualWidth=window.width(),actualHeight=window.height(),viewportWidth=viewport.width(),bodyWidth=content.width(),bodyOffset=offset,equivalentActionWidths=[r.action.width() for r in rows],outerHorizontalMaximum=0,primaryActions=sum(bool(b.property('primary')) for b in buttons),synchronousRenderMs=round(state['layoutRenderMs'],2)))
                state['layoutIndex']+=1
                if state['layoutIndex']<len(state['layoutProfiles'])*10:state['stage']=41;return
                assert window.state['milestones']==state['layoutMilestones']
                timings=sorted(r['synchronousRenderMs'] for r in state['layoutRows'])
                (evidence/'aionia-layout.json').write_text(json.dumps(dict(verified=True,standard='AIONIA 1.5',actualPackagedWindows=True,rows=state['layoutRows'],renderBudgetMs=2000,p95SynchronousRenderMs=timings[math.ceil(len(timings)*.95)-1],preferencesRestored=True,milestonesUnchanged=True,physicalDeviceCertification=False),indent=2),encoding='utf-8')
                window.settings=state['layoutPreferences'];window.settings_section=state['layoutSettingsSection'];window.resize(*state['layoutSize']);window.appearance();window.render()
                state['layoutChecked']=True;finish(state['layoutFinalSettings'])
        except Exception as error:
            timer.stop()
            (evidence/'FAILED.json').write_text(json.dumps({'scenario':scenario,'stage':state['stage'],'error':repr(error),'notice':window.notice.text()},indent=2),encoding='utf-8')
            window.bridge.close();QApplication.exit(1)
    def finish(settings):
        if not state.get('driverCenterChecked'):
            state.update(driverFinalSettings=settings,stage=29)
            return
        if not state.get('personalizeChecked'):
            state.update(personalFinalSettings=settings,stage=22)
            return
        if not state.get('usabilityChecked'):
            state.update(usabilityFinalSettings=settings,stage=37)
            return
        if not state.get('layoutChecked'):
            state.update(layoutFinalSettings=settings,stage=40)
            return
        if not state.get('recoveryChecked'):
            assert not window.busy
            state.update(finalSettings=settings,recoveryReport=window.state['report']['id'],
                recoveryHardware=window.state['hardware'],recoveryMilestones=list(window.state['milestones']),stage=20)
            # Test only: terminate this app's own bundled Node after all Windows work finished.
            # Never terminate PowerShell or an in-flight installation/cleanup operation.
            window.bridge.process.kill()
            return
        timer.stop()
        from app import VERSION
        (evidence/f'verified-{scenario}.json').write_text(json.dumps(dict(version=VERSION,scenario=scenario,engine='Qt Widgets',portable=window.portable,data=str(window.data),settings=settings,verified=True),ensure_ascii=False,indent=2),encoding='utf-8')
        window.close()
    timer.timeout.connect(advance)
    timer.start()
