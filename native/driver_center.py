"""One native driver workflow, sharing the existing signed-package backend."""
from PySide6.QtCore import Qt, QTimer, QDateTime, QLocale
from PySide6.QtWidgets import QComboBox, QLineEdit, QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog
from widgets import Choice as QComboBox

SECTIONS=('updates','inventory','backups','offline','ignored')

def library(window):
    window.run('workshop.library',callback=lambda r:window.store('library',r),silent=True)

def queue_library(window):
    def refresh():
        if window.page=='drivers' and window.driver_section=='backups' and not window.busy and not window.backend_lost:library(window)
    QTimer.singleShot(0,window,refresh)

def section(window,value):
    window.driver_section=value
    window.render()
    if value in ('backups','ignored') and 'library' not in window.state and not window.backend_lost:library(window)

def result(window,key,value,target):
    window.driver_section=target
    window.store(key,value)

def backup(window):
    def finished(value):
        window.state.pop('library',None)
        result(window,'driverBackupResult',value,'backups')
        queue_library(window)
    window.run('driver-backup',callback=finished)

def render(window):
    t=window.t
    window.label(t('driversIntro'))
    from journey import render_return
    render_return(window)
    picker=QComboBox();picker.setObjectName('driver-section');picker.setAccessibleName(t('dc.choose'))
    for key in SECTIONS:picker.addItem(t('dc.'+key),key)
    picker.setCurrentIndex(SECTIONS.index(window.driver_section));picker.setEnabled(not window.busy)
    picker.currentIndexChanged.connect(lambda _:section(window,picker.currentData()))
    window.body.addWidget(picker)
    window.label(t('dc.'+window.driver_section),heading=True,level=2)
    window.label(t('dc.help.'+window.driver_section))
    updates=window.state.get('updates')
    if window.driver_section=='updates' and updates:
        window.button(f'{t("updateAllDrivers")} ({len(updates)})',lambda:window.install_offers(updates),True,literal=True,name='update-all')
    window.button('checkDrivers',lambda:window.run('windows-updates',callback=lambda r:result(window,'updates',r,'updates')),window.driver_section=='updates' and not updates,name='driver-check')
    window.button('inventory',lambda:window.run('drivers',callback=lambda r:result(window,'drivers',r,'inventory')),name='driver-inventory',primary=window.driver_section=='inventory')
    window.button('driverBackup',lambda:backup(window),name='driver-backup',primary=window.driver_section=='backups' and not window.state.get('package'))
    saved=window.state.get('driverBackupResult')
    if isinstance(saved,dict):window.label(t('j.backupCreated').format(count=saved.get('packages',0)) if saved.get('packages',0)>0 else t('j.noPackages'))
    globals()['render_'+window.driver_section](window)

def render_updates(window):
    t=window.t;updates=window.state.get('updates')
    if updates is None:window.label(t('dc.notScanned'))
    elif updates:
        tree=window.table(updates,[('name',t('availableUpdates')),('manufacturer',t('provider')),('bytes',t('d.bytes'))],check=True)
        tree.setObjectName('driver-updates-tree')
        window.button('updateDrivers',lambda:window.install_offers(window.chosen(tree)) if window.chosen(tree) else None,name='driver-update-selected')
        window.button('w.ignore',lambda:ignore(window,window.chosen(tree)),name='driver-ignore-selected')
    else:window.label(t('noUpdates'))
    window.label(t('driverExplain'))
    window.button('windowsUpdate',lambda:window.external('windows'))
    for key in ('oem-nvidia','oem-amd','oem-intel'):window.button(key.split('-')[1].upper(),lambda _,k=key:window.external(k),literal=True)

def ignore(window,rows):
    if not rows:return
    ids=[r['id'] for r in rows]
    def finished(_):
        window.state['updates']=[r for r in window.state.get('updates',[]) if r['id'] not in ids]
        report=window.state.get('report')
        if report:report['findings']=[r for r in report['findings'] if r['id'] not in ['update:'+i for i in ids]]
        window.state.pop('library',None)
        window.render()
    window.run('updates.ignore-many',dict(ids=ids),finished)

def render_inventory(window):
    t=window.t
    if 'drivers' not in window.state:window.label(t('dc.notScanned'));return
    rows=window.state['drivers'];view=window.state.setdefault('driverView',dict(query='',issues=False))
    search=QLineEdit(view['query']);search.setObjectName('driver-search');search.setPlaceholderText(t('dc.search'));search.setAccessibleName(t('dc.search'));window.body.addWidget(search)
    mode=QComboBox();mode.setObjectName('driver-filter');mode.setAccessibleName(t('dc.filter'));mode.addItem(t('dc.all'),'all');mode.addItem(t('dc.issues'),'issues');mode.setCurrentIndex(1 if view['issues'] else 0);window.body.addWidget(mode)
    count=window.label('');count.setObjectName('driver-match-count')
    tree=QTreeWidget();tree.setObjectName('driver-inventory-tree');tree.setAccessibleName(t('dc.inventory'));tree.setColumnCount(4);tree.setHeaderLabels([t('d.name'),t('version'),t('provider'),t('problem')]);tree.setWordWrap(True);tree.setMinimumHeight(300);window.body.addWidget(tree)
    def populate():
        query=search.text().strip().casefold();view.update(query=search.text(),issues=mode.currentData()=='issues');tree.clear()
        for row in rows:
            if view['issues'] and (row.get('problem') is None or row.get('problem')==0):continue
            if query and not any(query in str(row.get(k,'')).casefold() for k in ('name','provider','version','inf','deviceClass','id')):continue
            code=row.get('problem');status=t('unknown') if code is None else t('dc.noCode') if code==0 else t('dc.code').format(code=code)
            parent=QTreeWidgetItem(tree,[str(row.get('name','')),str(row.get('version') or t('unknown')),str(row.get('provider') or t('unknown')),status])
            for key,label in [('id','dc.instance'),('inf','dc.inf'),('deviceClass','dc.deviceClass'),('date','dc.date'),('signed','dc.signed')]:
                value=row.get(key)
                if key=='signed':value=t('dc.signedYes') if value is True else t('dc.signedNo') if value is False else t('unknown')
                if key=='date' and value:value=friendly_date(value,window.settings['language'])
                QTreeWidgetItem(parent,[t(label),str(value if value is not None else t('unknown'))])
        tree.resizeColumnToContents(0);tree.setColumnWidth(0,min(400,tree.columnWidth(0)))
        count.setPlainText(t('dc.matches').format(shown=tree.topLevelItemCount(),total=len(rows)))
    search.textChanged.connect(populate);mode.currentIndexChanged.connect(populate);populate()
    window.button('dc.clear',lambda:(search.clear(),mode.setCurrentIndex(0)))
    window.label(t('dc.codeHelp'))
    window.button('w.deviceManager',lambda:window.system_open('devices'))

def friendly_date(value,language):
    date=QDateTime.fromString(str(value),Qt.ISODateWithMs)
    if not date.isValid():date=QDateTime.fromString(str(value),Qt.ISODate)
    return QLocale('tr_TR' if language=='tr' else 'en_US').toString(date.toLocalTime(),QLocale.ShortFormat) if date.isValid() else str(value)

def render_backups(window):
    t=window.t
    window.button('dc.refreshLibrary',lambda:library(window),name='driver-library-refresh')
    window.button('openDriverBackups',lambda:window.open_folder('drivers'))
    window.button('w.import',lambda:import_package(window),name='driver-import')
    items=window.state.get('library',{}).get('packages',[])
    if 'library' in window.state and not items:window.label(t('dc.noBackups'))
    for package in items:
        name=t('dc.backup' if package['kind']=='DriverBackups' else 'dc.imported')+' · '+friendly_date(package.get('at',''),window.settings['language'])
        def inspect(_,p=package,label=name):
            window.state.pop('package',None);window.state.pop('driverPackageResult',None)
            window.state['packageSource']=label
            window.run('package.inspect',dict(id=p['id']),lambda r:window.store('package',r))
        window.button(name,inspect,literal=True,name='driver-inspect-'+package['id'])
    plan=window.state.get('package')
    if plan:
        window.label(window.state.get('packageSource',t('dc.backup')))
        window.label(t('dc.plan').format(count=len(plan.get('candidates',[]))))
        window.label(t('n.restore_note'))
        tree=window.table(plan.get('candidates',[]),[('name',t('d.name')),('provider',t('provider')),('version',t('version')),('publisher',t('dc.publisher'))],check=True);tree.setObjectName('driver-package-tree')
        window.label(t('w.blocked')+': '+str(sum(not r.get('eligible') for r in plan.get('candidates',[]))))
        selection=window.label(t('dc.selection').format(count=0));selection.setObjectName('driver-package-selection')
        apply=window.button('w.apply',lambda:apply_package(window,plan,window.chosen(tree)),name='driver-package-apply',enabled=False,primary=True)
        def selected():
            count=len(window.chosen(tree));selection.setPlainText(t('dc.selection').format(count=count))
            apply.setEnabled(not window.busy and 1<=count<=20)
        tree.itemChanged.connect(lambda *_:selected())
    previous=window.state.get('driverPackageResult')
    if previous:
        window.label(t('dc.applied').format(changes=len(previous.get('changes',[]))))
        if previous.get('reboot'):window.label(t('reboot'))

def import_package(window):
    directory=QFileDialog.getExistingDirectory(window,window.t('w.import'))
    if directory:
        window.state.pop('package',None);window.state.pop('driverPackageResult',None)
        window.state['packageSource']=window.t('dc.imported')
        window.run('package.import',dict(directory=directory),lambda r:imported(window,r))

def imported(window,value):
    window.state.pop('library',None)
    window.store('package',value)
    queue_library(window)

def apply_package(window,plan,rows):
    if not rows or len(rows)>20:return
    def complete(value):
        window.state.pop('package',None)
        window.store('driverPackageResult',value)
        window.show_result(value)
    window.confirm(window.t('confirm'),window.t('n.automatic_backup'),[r['name'] for r in rows],lambda:window.run('package.apply',dict(planId=plan['id'],ids=[r['id'] for r in rows],confirm=True),complete))

def render_offline(window):
    window.button('w.exportHardware',lambda:window.export('offline.export'),name='driver-offline-export')
    window.button('w.readHardware',lambda:window.run('offline.inventory',callback=lambda r:window.store('offline',r)),name='driver-offline-read',primary=True)
    if window.state.get('offline'):
        tree=window.table(window.state['offline']['devices'],[('name',window.t('d.name')),('hardwareIds',window.t('w.hardware'))],check=True)
        def search():
            selected=window.chosen(tree)
            if selected:window.bridge.call('hardware.search',dict(id=selected[0]['id']),window.open_reply)
        window.button('w.catalog',search,name='driver-offline-search')
    window.button('dc.openPackages',lambda:section(window,'backups'),name='driver-offline-import')

def render_ignored(window):
    window.button('dc.refreshLibrary',lambda:library(window),name='driver-ignored-refresh',primary=True)
    items=window.state.get('library',{}).get('ignored',[])
    if 'library' in window.state and not items:window.label(window.t('dc.noIgnored'))
    if not items:return
    tree=window.table(items,[('name',window.t('d.name'))],check=True);tree.setObjectName('driver-ignored-tree')
    def restore(rows):
        if not rows:return
        ids=[r['id'] for r in rows]
        def finished(_):
            window.state['library']['ignored']=[r for r in items if r['id'] not in ids]
            window.render()
        window.run('updates.unignore-many',dict(ids=ids),finished)
    window.button('dc.restoreSelected',lambda:restore(window.chosen(tree)),name='driver-restore-selected')
    window.button('dc.restoreAll',lambda:restore(items),name='driver-restore-all')
