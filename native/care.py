"""SysMender-inspired Windows evidence, adapted to native Qt and bounded local reports."""
from datetime import datetime
import json
from PySide6.QtWidgets import QApplication, QComboBox, QLineEdit, QTreeWidget, QTreeWidgetItem, QHeaderView, QFormLayout, QLabel, QHBoxLayout
from hardware import format_value as hardware_value, progress_state as category_progress
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

def report_for(window):
    return window.state.get('care')

def render_support(window):
    report=report_for(window)
    if not report:return
    def copy_summary():QApplication.clipboard().setText(summary(report,window.settings['language'],window.t));window.notice.setText(window.t('care.copied'))
    window.button('care.copy',copy_summary,name='care-copy')
    window.button('care.export',lambda:window.export('care.export'),name='care-export')
    window.label(window.t('care.exportNote'))

def render_home(window):
    report=report_for(window)
    if not report:return
    ready=next((s for s in report.get('sections',[]) if s['id']=='readiness'),{})
    panel=window.group('care.homeStatus')
    if ready.get('items'):
        row=ready['items'][0]
        window.label(window.t('care.fields.restartSignals')+': '+value('restartSignals',row.get('restartSignals',[]),window.settings['language'],window.t),layout=panel)
        if row.get('restartUnknown'):window.label(window.t('care.restartUnknown'),layout=panel)
    else:window.label(window.t('care.unavailable'),layout=panel)
    window.label(window.t('care.at')+': '+value('at',report.get('at'),window.settings['language'],window.t),layout=panel)

def render_component(window):
    t=window.t;language=window.settings['language']
    window.button('care.componentButton',lambda:window.confirm(t('confirm'),t('care.componentConfirm'),[t('care.component')],lambda:window.run('component-check',dict(confirm=True),lambda r:window.store('componentState',r))),name='care-component-check')
    component=window.state.get('componentState')
    if component:
        panel=window.group('care.component')
        window.label(t('care.states.'+component.get('state','unknown')),layout=panel)
        window.label(t('care.componentScope'),layout=panel)
        window.label(t('care.fields.rebootRequired')+': '+value('rebootRequired',component.get('restartNeeded'),language,t),layout=panel)
        window.label(t('care.at')+': '+value('at',component.get('at'),language,t),layout=panel)

def render_records(window,report,ids,context,layout=None):
    from PySide6.QtWidgets import QWidget,QVBoxLayout
    t=window.t;language=window.settings['language']
    container=QWidget();outer=QVBoxLayout(container);outer.setContentsMargins(0,0,0,0);(layout or window.body).addWidget(container)
    view=window.state.setdefault('careView:'+context,dict(category='all',query=''))
    category=QComboBox();category.setObjectName(context+'-category');category.setAccessibleName(t('hw.category'));category.addItem(t('hw.all'),'all')
    for key in ids:category.addItem(t('care.'+key),key)
    category.setCurrentIndex(max(0,category.findData(view['category'])));outer.addWidget(category)
    search=QLineEdit(view['query']);search.setObjectName(context+'-search');search.setPlaceholderText(t('care.search'));search.setAccessibleName(t('care.search'));outer.addWidget(search)
    tree=QTreeWidget();tree.setObjectName(context+'-tree');tree.setColumnCount(2);tree.setHeaderLabels([t('hw.property'),t('hw.value')]);tree.setMinimumHeight(260);tree.setWordWrap(True);tree.header().setSectionResizeMode(0,QHeaderView.Interactive);tree.header().setSectionResizeMode(1,QHeaderView.Stretch);tree.setColumnWidth(0,310);tree.setAccessibleName(t({'scan-records':'care.scanRecords','tools-records':'care.toolsStatus','update-records':'care.updateHistory'}[context]));outer.addWidget(tree)
    no_match=QLabel(t('forge.noMatches'));no_match.setWordWrap(True);outer.addWidget(no_match)
    def populate():
        tree.clear();selection=category.currentData();query=search.text().strip().casefold();view.update(category=selection,query=search.text());matched=0
        for section in report.get('sections',[]):
            key=section['id']
            if key not in ids or (selection!='all' and key!=selection):continue
            rows=[row for row in section.get('items',[]) if not query or query in t('care.'+key).casefold() or any(query in str(v).casefold() for v in row.values())]
            if query and not rows:continue
            matched+=len(rows);status='hw.emptyStatus' if section.get('status')=='empty' else 'hw.'+section.get('status','unavailable')
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

def render_scan(window):
    report=report_for(window)
    panel=window.group('care.scanRecords')
    if not report:
        window.label(window.t('care.sharedUnavailable'),layout=panel);return
    t=window.t;language=window.settings['language'];sections={s['id']:s for s in report.get('sections',[])}
    counts=[]
    for key in ('systemEvents','appEvents','crashes','dumps'):
        section=sections.get(key,{})
        status=t('care.unavailable') if section.get('status')=='unavailable' else str(len(section.get('items',[])))+('+' if section.get('limited') else '')
        counts.append(t('care.'+key)+': '+status)
    window.label(' · '.join(counts),layout=panel)
    window.label(t('care.at')+': '+value('at',report.get('at'),language,t),layout=panel)
    window.label(t('care.historyNote'),layout=panel)
    detail=window.group('care.scanDetails',True,False)
    render_records(window,report,('systemEvents','appEvents','crashes','dumps'),'scan-records',detail)
    window.button('care.eventViewer',lambda:window.system_open('events'))
    render_support(window)

def render_tools(window):
    window.button('care.refreshLocal',lambda:window.run('diagnostics.scan',dict(online=False),lambda r:window.store('report',r)),True,name='tools-refresh-local')
    report=report_for(window)
    if report:
        panel=window.group('care.toolsStatus')
        window.label(window.t('care.at')+': '+value('at',report.get('at'),window.settings['language'],window.t),layout=panel)
        render_records(window,report,('defender','firewall','services'),'tools-records',panel)
        window.label(window.t('care.securityNote'),layout=panel)
    else:window.label(window.t('care.sharedEmpty'))
    render_component(window)

def render_history(window):
    report=report_for(window)
    if not report:return
    panel=window.group('care.updateHistory')
    window.label(window.t('care.at')+': '+value('at',report.get('at'),window.settings['language'],window.t),layout=panel)
    render_records(window,report,('updateHistory',),'update-records',panel)
    render_support(window)
