"""Task categories within the same native maintenance application."""
import json
from PySide6.QtWidgets import QComboBox
from widgets import Choice as QComboBox

SECTIONS=('runtimes','points','focus','devices')

def render(window):
    t=window.t
    window.label(t('dc.workshopIntro'))
    choose=QComboBox();choose.setObjectName('workshop-section');choose.setAccessibleName(t('dc.workshopChoose'))
    for key in SECTIONS:choose.addItem(t('dc.workshop.'+key),key)
    choose.setCurrentIndex(SECTIONS.index(window.workshop_section));choose.setEnabled(not window.busy)
    def select():window.workshop_section=choose.currentData();window.render()
    choose.currentIndexChanged.connect(select);window.body.addWidget(choose)
    window.label(t('dc.workshop.'+window.workshop_section),heading=True,level=2)
    if window.workshop_section=='runtimes':
        if window.state.get('runtimes',{}).get('available') is False:window.label(t('w.runtimeUnknown'))
        window.button('w.runtimes',lambda:window.run('runtime.inventory',callback=lambda r:window.store('runtimes',r)),True)
        for key,name in [('vc-x64','Visual C++ v14 x64'),('vc-x86','Visual C++ v14 x86'),('directx-legacy','DirectX June 2010')]:
            layout=window.group('w.runtimes');window.label(name,layout=layout)
            installed=next((i for i in window.state.get('runtimes',{}).get('items',[]) if i['id']==key),None)
            if installed:window.label(t('d.runtimePresent' if installed.get('installed') else 'd.runtimeOptional'),layout=layout)
            window.button('w.prepare',lambda _,k=key:window.run('runtime.prepare',dict(id=k),lambda r:window.prepare_runtime(r)),layout=layout)
    elif window.workshop_section=='points':
        window.button('w.listPoints',lambda:window.run('restore-points',callback=lambda r:window.store('points',r)),True)
        if 'points' in window.state:window.details('n.values',json.dumps(window.state['points'],ensure_ascii=False,indent=2))
        window.button('w.createPoint',lambda:window.confirm(t('confirm'),t('w.intro'),[t('w.createPoint')],lambda:window.run('restore-point-create',dict(confirm=True))))
        for key in ('restore','protection'):
            window.button(t('w.restoreWizard' if key=='restore' else 'w.protection'),lambda _,k=key:window.system_open(k),literal=True)
    elif window.workshop_section=='devices':
        window.button('w.deviceManager',lambda:window.system_open('devices'))
        window.button('w.ghosts',lambda:window.run('ghosts',callback=lambda r:window.store('ghosts',r)),True)
        for ghost in window.state.get('ghosts',[]):window.button(ghost['name'],lambda _,g=ghost:window.confirm(t('confirm'),t('w.ghostHelp'),[g['name']],lambda:window.run('ghost-remove',dict(id=g['id'],confirm=True))),literal=True)
    elif window.workshop_section=='focus':
        window.button('w.loadFocus',lambda:window.run('focus.inventory',callback=lambda r:window.store('focus',r)),True)
        focus=window.state.get('focus')
        if focus:
            tree=window.table(focus.get('apps',[]),[('name',t('d.name'))],check=True)
            combo=QComboBox();combo.setAccessibleName(t('n.choose_plan'))
            for p in focus.get('powers',[]):
                combo.addItem(p['name'],p['id'])
                if p.get('active'):combo.setCurrentIndex(combo.count()-1)
            window.body.addWidget(combo)
            window.button('w.startFocus',lambda:window.confirm(t('confirm'),t('n.normal_close'),[a['name'] for a in window.chosen(tree)]+[combo.currentText()],lambda:window.run('focus.start',dict(ids=[a['id'] for a in window.chosen(tree)],powerId=combo.currentData(),confirm=True),lambda _:window.reload_library())))
        if window.state.get('library',{}).get('focus'):window.button('w.stopFocus',lambda:window.run('focus.stop',dict(confirm=True),lambda _:window.reload_library()))
    def drivers():window.driver_section='backups';window.go('drivers')
    window.button('dc.driverTools',drivers,name='workshop-driver-tools')
