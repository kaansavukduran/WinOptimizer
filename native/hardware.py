"""Native, read-only hardware browser. Missing values remain unknown, never invented."""
from datetime import datetime
from PySide6.QtCore import Qt
from pathlib import Path
from PySide6.QtWidgets import QApplication, QLabel, QComboBox, QLineEdit, QTreeWidget, QTreeWidgetItem, QHeaderView, QFormLayout, QFileDialog

MEMORY_TYPES={20:'DDR',21:'DDR2',22:'DDR2 FB-DIMM',24:'DDR3',26:'DDR4',27:'LPDDR',28:'LPDDR2',29:'LPDDR3',30:'LPDDR4',34:'DDR5',35:'LPDDR5'}
ARCHITECTURES={0:'x86',5:'ARM',6:'Itanium',9:'x64',12:'ARM64'}

def number(value,language,decimals=0):
    result=f'{value:,.{decimals}f}'
    return result.translate(str.maketrans(',.','.,')) if language=='tr' else result

def format_value(key,value,language,text):
    if value is None or value=='':return text('hw.unknown')
    if isinstance(value,bool):return text('hw.yes' if value else 'hw.no')
    if key=='memoryType':return MEMORY_TYPES.get(value,str(value))
    if key=='architecture':return ARCHITECTURES.get(value,str(value))
    if key=='memorySource':return 'DXGI (64-bit)' if value=='DXGI' else text('hw.unknown')
    if key.endswith('Bytes') and isinstance(value,(int,float)):
        return number(value/1024**3,language,1)+' GiB · '+number(value,language)+' bytes'
    if key=='releaseDate':
        try:return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone().strftime('%d.%m.%Y' if language=='tr' else '%Y-%m-%d')
        except (ValueError,TypeError):return str(value)
    if isinstance(value,(int,float)):return number(value,language)
    if isinstance(value,list):return ', '.join(str(item) for item in value)
    return str(value)

CATEGORIES=('system','cpu','gpu','memory','memoryArrays','motherboard','bios','storage','volumes','displays','network','audio','battery','devices')

def progress_state(trace):
    latest={}
    for event in trace.get('events',[]):
        step=event.get('step','')
        if event.get('origin')=='native' and step.startswith('hardware-') and step[9:] in CATEGORIES:
            latest[step[9:]]=event.get('status')
    done=sum(status in ('complete','failed','skipped') for status in latest.values())
    active=next((key for key,value in reversed(list(latest.items())) if value=='running'),None)
    return done,len(CATEGORIES),active

def adapter_name(item,text):
    name=item.get('name') or 'GPU'
    flag='software' if item.get('software') is True else 'remote' if item.get('remote') is True else None
    return name+(' ('+text('forge.'+flag)+')' if flag else '')

def summary_entries(report,language,text):
    by_id={s['id']:s for s in report.get('sections',[])}
    def items(key):return by_id.get(key,{}).get('items',[])
    rows=[]
    for section in ('cpu','gpu','motherboard'):
        names=[adapter_name(row,text) if section=='gpu' else row.get('name') for row in items(section)]
        rows.append((text('hw.'+section),'; '.join(n for n in names if n) or text('hw.unknown')))
    def compact(key,value):return format_value(key,value,language,text).split(' · ')[0]
    installed=sum(row.get('capacityBytes') or 0 for row in items('memory'))
    rows.append((text('hw.installedMemory'),compact('capacityBytes',installed or None)))
    for system in items('system'):rows.append((text('hw.fields.usableMemoryBytes'),compact('usableMemoryBytes',system.get('usableMemoryBytes'))))
    for gpu in items('gpu'):
        rows.append((text('hw.fields.dedicatedVideoBytes')+' · '+adapter_name(gpu,text),compact('dedicatedVideoBytes',gpu.get('dedicatedVideoBytes'))))
    return rows

def summary_text(report,language,text):
    return text('hw.summary')+'\n'+'\n'.join(f'{key}: {value}' for key,value in summary_entries(report,language,text))

def text_report(report,language,text):
    lines=[summary_text(report,language,text),'',text('hw.at')+': '+str(report.get('at','')),text('hw.vramHelp')]
    for section in report.get('sections',[]):
        status='emptyStatus' if section.get('status')=='empty' else section.get('status','unavailable')
        lines+=['','['+text('hw.'+section['id'])+'] '+text('hw.'+status),text('hw.source')+': '+str(section.get('source','Windows'))]
        if section.get('limited'):lines.append(text('hw.limit')+': '+str(len(section.get('items',[])))+' / '+str(section.get('total','')))
        for row in section.get('items',[]):
            lines.append('  '+str(row.get('name') or text('hw.'+section['id'])))
            for key,value in row.items():lines.append('    '+text('hw.fields.'+key)+': '+format_value(key,value,language,text))
        if not section.get('items'):lines.append(text('hw.noProvider' if section.get('status')=='unavailable' else 'hw.noDevices'))
    return '\n'.join(lines)+'\n'

def render(window):
    t=window.t
    language=window.settings['language']
    report=window.state.get('hardware')
    if not report:window.label(t('hw.intro'))
    window.button('hw.scan',lambda:window.run('hardware',callback=lambda result:window.store('hardware',result)),True,name='hardware-scan')
    if not report:
        window.label(t('hw.empty'));return
    sections=report.get('sections',[])
    by_id={section['id']:section for section in sections}
    def items(name):return by_id.get(name,{}).get('items',[])
    summary=window.group('hw.summary')
    form=QFormLayout()
    form.setRowWrapPolicy(QFormLayout.WrapAllRows if window.width()<850 else QFormLayout.WrapLongRows)
    summary.addLayout(form)
    for key,value in summary_entries(report,language,t):
        left,right=QLabel(key),QLabel(value)
        for label in (left,right):
            label.setWordWrap(True);label.setTextFormat(Qt.PlainText);label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        form.addRow(left,right)
    def copy_summary():
        QApplication.clipboard().setText(summary_text(report,language,t));window.notice.setText(t('forge.copied'))
    def save_text():
        file,_=QFileDialog.getSaveFileName(window,t('forge.textExport'),'WinOptimizer-Hardware.txt','Text (*.txt)')
        if not file:return
        try:Path(file).write_text(text_report(report,language,t),encoding='utf-8');window.notice.setText(t('n.report_saved'))
        except OSError:window.error('OPERATION_FAILED')
    window.button('forge.copy',copy_summary,name='hardware-copy')
    window.button('forge.textExport',save_text,name='hardware-text-export')
    window.label(t('hw.vramHelp'))
    view=window.state.setdefault('hardwareView',dict(query='',category='all'))
    search=QLineEdit()
    search.setText(view.get('query',''))
    search.setObjectName('hardware-search');search.setPlaceholderText(t('hw.search'));search.setAccessibleName(t('hw.search'));window.body.addWidget(search)
    category=QComboBox();category.setObjectName('hardware-category');category.setAccessibleName(t('hw.category'));category.addItem(t('hw.all'),'all')
    for section in sections:category.addItem(t('hw.'+section['id']),section['id'])
    category.setCurrentIndex(max(0,category.findData(view.get('category','all'))))
    window.body.addWidget(category)
    matches=window.label('');matches.setObjectName('hardware-match-count')
    empty=window.label(t('forge.noMatches'));empty.setObjectName('hardware-no-matches');empty.hide()
    def clear_filter():search.clear();category.setCurrentIndex(0)
    window.button('forge.clear',clear_filter,name='hardware-clear-filter')
    tree=QTreeWidget();tree.setObjectName('hardware-tree');tree.setColumnCount(2);tree.setHeaderLabels([t('hw.property'),t('hw.value')]);tree.setWordWrap(True);tree.setMinimumHeight(360);tree.setAccessibleName(t('hardware'))
    tree.header().setSectionResizeMode(0,QHeaderView.Interactive);tree.header().setSectionResizeMode(1,QHeaderView.Stretch);tree.setColumnWidth(0,280)
    window.body.addWidget(tree)
    def populate():
        tree.clear();query=search.text().strip().casefold();selection=category.currentData()
        view.update(query=search.text(),category=selection)
        shown=0;total=sum(len(s.get('items',[])) for s in sections)
        for section in sections:
            if selection!='all' and section['id']!=selection:continue
            rows=section.get('items',[])
            matching=[row for row in rows if not query or any(query in str(value).casefold() or query in t('hw.fields.'+key).casefold() for key,value in row.items()) or query in t('hw.'+section['id']).casefold()]
            if query and not matching:continue
            shown+=len(matching)
            label=t('hw.'+section['id'])
            status=t('hw.emptyStatus' if section.get('status')=='empty' else 'hw.'+section.get('status','unavailable'))
            top=QTreeWidgetItem(tree,[label,f'{len(matching)} · {status}'])
            top.setToolTip(0,str(section.get('source','Windows')))
            if section.get('limited'):QTreeWidgetItem(top,[t('hw.limit'),f'{len(rows)} / {section.get("total",len(rows))}'])
            if not rows:
                QTreeWidgetItem(top,[t('hw.source'),str(section.get('source','Windows'))]);QTreeWidgetItem(top,[t('hw.result'),t('hw.noProvider' if section.get('status')=='unavailable' else 'hw.noDevices')])
            for row in matching:
                name=str(row.get('name') or row.get('partNumber') or label)
                subtitle=[]
                for key in ('capacityBytes','dedicatedVideoBytes','driverVersion','deviceClass'):
                    if key in row:subtitle.append(format_value(key,row[key],language,t))
                item=QTreeWidgetItem(top,[name,' · '.join(subtitle)])
                for key,value in row.items():
                    field=t('hw.fields.'+key)
                    QTreeWidgetItem(item,[field,format_value(key,value,language,t)])
            top.setExpanded(True)
        matches.setText(t('forge.matches').format(shown=shown,total=total))
        empty.setVisible(bool((query or selection!='all') and not shown))
    search.textChanged.connect(populate);category.currentIndexChanged.connect(populate)
    window.button('hw.expand',tree.expandAll)
    window.button('hw.collapse',tree.collapseAll)
    populate()
    window.button('hw.export',lambda:window.export('hardware.export'),name='hardware-export')
    if report.get('at'):
        try:at=datetime.fromisoformat(report['at'].replace('Z','+00:00')).astimezone().strftime('%d.%m.%Y %H:%M:%S' if language=='tr' else '%Y-%m-%d %H:%M:%S')
        except ValueError:at=report['at']
        window.label(t('hw.at')+': '+at)
    window.label(t('hw.scope'))
