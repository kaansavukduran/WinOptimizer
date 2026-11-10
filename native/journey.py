"""Explain the three existing, persistent care milestones and reveal their actions."""
from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import QWidget,QVBoxLayout,QHBoxLayout,QLabel,QProgressBar,QPushButton,QFrame

ACTIONS={'health':'healthScan','scan':'scan','drivers':'driverBackup'}
STEPS=(('health','stepHealth','home','health-scan'),('scan','stepScan','cleanup','cleanup-scan'),('drivers','stepDrivers','drivers','driver-backup'))

def reveal_step(window,key):
    if window.busy:return
    item=next(item for item in STEPS if item[0]==key)
    window.state['journeyActiveStep']=key
    window.go(item[2])
    target=window.scroll.widget().findChild(QPushButton,item[3])
    window.notice.setText(window.t('j.locate.'+key).format(action=window.t(ACTIONS[key])))
    def reveal():
        window.scroll.ensureWidgetVisible(target,0,24)
        target.setFocus(Qt.OtherFocusReason)
    QTimer.singleShot(0,target,reveal)

def render_return(window):
    key=window.state.get('journeyActiveStep')
    item=next((item for item in STEPS if item[0]==key),None)
    if not item or window.page!=item[2]:return
    def go_back():
        window.state.pop('journeyActiveStep',None)
        window.go('home')
        window.scroll.verticalScrollBar().setValue(0)
    window.button('j.back',go_back,name='journey-return')

def render(window):
    if not window.settings.get('gamification',True):return
    t=window.t;completed=set(window.state.get('milestones',[]))
    done=sum(key in completed for key,_,_,_ in STEPS)
    panel=window.group('carePath');panel.parentWidget().setObjectName('care-journey')
    window.label(t('j.intro'),layout=panel)
    bar=QProgressBar();bar.setObjectName('journey-progress');bar.setRange(0,len(STEPS));bar.setValue(done);bar.setFormat(t('j.progress').format(done=done));bar.setAccessibleName(t('j.summary').format(done=done));panel.addWidget(bar)
    missing=next((item for item in STEPS if item[0] not in completed),None)
    if missing:
        number=STEPS.index(missing)+1
        label=window.label(t('j.next').format(number=number,title=t(missing[1])),layout=panel);label.setObjectName('journey-next-label')
        window.button('j.go.'+missing[0],lambda:reveal_step(window,missing[0]),True,panel,name='journey-next')
    else:
        window.label(t('j.allDone'),layout=panel)
        window.button('j.review',lambda:window.go('scanFix'),layout=panel,name='journey-review')
    for number,(key,title,_,_) in enumerate(STEPS,1):
        status=t('j.done' if key in completed else 'j.pending')
        box=QWidget();box.setObjectName('journey-step-'+key);layout=QVBoxLayout(box);layout.setContentsMargins(0,6,0,6);layout.setSpacing(6);panel.addWidget(box)
        header=QVBoxLayout() if window.width()<900 or window.settings.get('scale',100)>=150 else QHBoxLayout();layout.addLayout(header)
        title_label=QLabel(f'{number}. {t(title)}');title_label.setWordWrap(True);font=title_label.font();font.setBold(True);title_label.setFont(font);header.addWidget(title_label)
        label=QLabel(status);label.setWordWrap(True);label.setObjectName('journey-status-'+key);header.addWidget(label)
        button=window.button('j.reopen' if key in completed else 'j.open',lambda _,k=key:reveal_step(window,k),layout=header,name='journey-open-'+key)
        button.setAccessibleName(t(title)+' · '+button.text())
        window.label(t('j.explain.'+key).format(action=t(ACTIONS[key])),layout=layout)
        box.setAccessibleName(title_label.text()+' · '+status)
        if number<len(STEPS):
            line=QFrame();line.setFrameShape(QFrame.HLine);panel.addWidget(line)
    window.label(t('j.historyNote'),layout=panel)
