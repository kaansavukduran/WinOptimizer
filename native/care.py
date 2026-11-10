"""SysMender-inspired Windows evidence, adapted to native Qt and bounded local reports."""
from datetime import datetime
import json
from PySide6.QtWidgets import QApplication, QComboBox, QLineEdit, QTreeWidget, QTreeWidgetItem, QHeaderView, QFormLayout, QLabel, QHBoxLayout
from hardware import format_value as hardware_value, progress_state as category_progress
from mascot import Aion
from PySide6.QtCore import Qt

SECTIONS=('readiness','defender','firewall','systemEvents','appEvents','crashes','dumps','updateHistory','services')

def progress_state(trace):return category_progress(trace,SECTIONS,'care-')

def value(key,item,language,text):
    if item is None or item=='':return text('hw.unknown')
    if key in ('at','bootAt','signatureAt'):
        try:return datetime.fromisoformat(str(item).replace('Z','+00:00')).astimezone().strftime('%d.%m.%Y %H:%M:%S' if language=='tr' else '%Y-%m-%d %H:%M:%S')
        except (ValueError,TypeError):return str(item)
    if key=='uptimeSeconds':
        minutes=int(item)//60;return text('care.uptime').format(days=minutes//1440,hours=(minutes%1440)//60,minutes=minutes%60)
    if key=='restartSignals':return ', '.join(text('care.signals.'+s) for s in item) or text('care.noSignals')
    if key=='resultCode':return text('care.results.'+str(item))
    if key=='operation':return text('care.operations.'+str(item))
    if key=='level':return text('care.levels.'+str(item))
    return hardware_value(key,item,language,text)

def summary(report,language,text):
    sections={s['id']:s for s in report.get('sections',[])}
    ready=sections.get('readiness',{}).get('items',[])
    lines=[text('windowsCare'),text('care.at')+': '+value('at',report.get('at'),language,text)]
    if ready:
        row=ready[0];lines.append(str(row.get('name','Windows'))+' · '+str(row.get('version',''))+' · '+str(row.get('build','')))
        lines.append(text('care.fields.uptimeSeconds')+': '+value('uptimeSeconds',row.get('uptimeSeconds'),language,text))
        lines.append(text('care.fields.restartSignals')+': '+value('restartSignals',row.get('restartSignals',[]),language,text))
        if row.get('restartUnknown'):lines.append(text('care.restartUnknown'))
    for key in SECTIONS:
        s=sections.get(key,{})
        if not s:continue
        status='hw.emptyStatus' if s.get('status')=='empty' else 'hw.'+s.get('status','unavailable')
        lines.append(text('care.'+key)+': '+text(status)+' · '+str(len(s.get('items',[])))+(' · '+text('care.limited') if s.get('limited') else ''))
    lines.extend([text('care.historyNote'),text('care.exportNote')])
    return '\n'.join(lines)

def render(window):
    t=window.t;language=window.settings['language']
    window.label(t('care.intro'))
    window.button('care.scan',lambda:window.run('care.snapshot',callback=lambda r:window.store('care',r)),True,name='care-scan')
    report=window.state.get('care')
    if report:
        sections={s['id']:s for s in report.get('sections',[])}
        panel=window.group('care.summary');row=QHBoxLayout();form=QFormLayout();form.setRowWrapPolicy(QFormLayout.WrapLongRows)
        row.addLayout(form,1);panel.addLayout(row)
        ready=sections.get('readiness',{}).get('items',[])
        entries=[]
        if ready:
            r=ready[0];entries=[('Windows',str(r.get('name','Windows'))+' · '+str(r.get('version',''))), (t('care.fields.uptimeSeconds'),value('uptimeSeconds',r.get('uptimeSeconds'),language,t)),(t('care.fields.restartSignals'),value('restartSignals',r.get('restartSignals',[]),language,t)+((' · '+t('care.restartUnknown')) if r.get('restartUnknown') else ''))]
        for key in ('systemEvents','appEvents','crashes'):
            s=sections.get(key,{})
            entries.append((t('care.'+key),t('care.unavailable') if s.get('status')=='unavailable' else str(len(s.get('items',[])))+('+' if s.get('limited') else '')))
        for key,raw in entries:
            label=QLabel(str(raw));label.setWordWrap(True);label.setTextFormat(Qt.PlainText);label.setTextInteractionFlags(Qt.TextSelectableByMouse);form.addRow(key,label)
        if window.width()>=900 and window.settings.get('companion',True):
            window.aion=Aion(window.resource_root,lambda key:window.t('n.'+key));window.aion.configure(window.settings);row.addWidget(window.aion)
        window.label(t('care.at')+': '+value('at',report.get('at'),language,t),layout=panel)
        window.label(t('care.historyNote'))
    def copy_summary():QApplication.clipboard().setText(summary(report,language,t));window.notice.setText(t('care.copied'))
    if report:
        window.button('care.copy',copy_summary,name='care-copy')
        window.button('care.export',lambda:window.export('care.export'),name='care-export')
        window.label(t('care.exportNote'))
    window.button('care.componentButton',lambda:window.confirm(t('confirm'),t('care.componentConfirm'),[t('care.component')],lambda:window.run('component-check',dict(confirm=True),lambda r:window.store('componentState',r))),name='care-component-check')
    component=window.state.get('componentState')
    if component:
        panel=window.group('care.component')
        window.label(t('care.states.'+component.get('state','unknown')),layout=panel)
        window.label(t('care.componentScope'),layout=panel)
        window.label(t('care.fields.rebootRequired')+': '+value('rebootRequired',component.get('restartNeeded'),language,t),layout=panel)
        window.label(t('care.at')+': '+value('at',component.get('at'),language,t),layout=panel)
    window.button('care.eventViewer',lambda:window.system_open('events'))
    if not report:
        window.label(t('care.empty'));return
    view=window.state.setdefault('careView',dict(category='all',query=''))
    category=QComboBox();category.setObjectName('care-category');category.setAccessibleName(t('hw.category'));category.addItem(t('hw.all'),'all')
    for key in SECTIONS:category.addItem(t('care.'+key),key)
    category.setCurrentIndex(max(0,category.findData(view['category'])));window.body.addWidget(category)
    search=QLineEdit(view['query']);search.setObjectName('care-search');search.setPlaceholderText(t('care.search'));search.setAccessibleName(t('care.search'));window.body.addWidget(search)
    tree=QTreeWidget();tree.setObjectName('care-tree');tree.setColumnCount(2);tree.setHeaderLabels([t('hw.property'),t('hw.value')]);tree.setMinimumHeight(340);tree.setWordWrap(True);tree.header().setSectionResizeMode(0,QHeaderView.Interactive);tree.header().setSectionResizeMode(1,QHeaderView.Stretch);tree.setColumnWidth(0,310);tree.setAccessibleName(t('windowsCare'));window.body.addWidget(tree)
    no_match=window.label(t('forge.noMatches'))
    def populate():
        tree.clear();selection=category.currentData();query=search.text().strip().casefold();view.update(category=selection,query=search.text());matched=0
        for section in report.get('sections',[]):
            key=section['id']
            if selection!='all' and key!=selection:continue
            rows=section.get('items',[])
            rows=[row for row in rows if not query or query in t('care.'+key).casefold() or any(query in str(v).casefold() for v in row.values())]
            if query and not rows:continue
            matched+=len(rows)
            status='hw.emptyStatus' if section.get('status')=='empty' else 'hw.'+section.get('status','unavailable')
            top=QTreeWidgetItem(tree,[t('care.'+key),t(status)+' · '+str(len(rows))]);top.setToolTip(0,section.get('source','Windows'));top.setExpanded(True)
            if section.get('limited'):QTreeWidgetItem(top,[t('care.limited'),'100'])
            if not rows:QTreeWidgetItem(top,[t('hw.result'),t('care.unavailable' if section.get('status')=='unavailable' else 'care.noRecords')])
            for row in rows:
                name=row.get('name') or row.get('provider') or t('care.'+key)
                if 'eventId' in row:name=str(name)+' · '+str(row['eventId'])
                item=QTreeWidgetItem(top,[str(name),value('at',row['at'],language,t) if row.get('at') else ''])
                for field,raw in row.items():QTreeWidgetItem(item,[t('care.fields.'+field),value(field,raw,language,t)])
        no_match.setVisible(bool(query and not matched))
    search.textChanged.connect(populate);category.currentIndexChanged.connect(populate);populate()
    window.button('hw.expand',tree.expandAll);window.button('hw.collapse',tree.collapseAll)
    window.label(t('care.securityNote'))
