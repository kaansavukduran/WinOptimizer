"""Native, read-only hardware browser. Missing values remain unknown, never invented."""
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLineEdit, QTreeWidget, QTreeWidgetItem, QHeaderView

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
    for section in ['cpu','gpu','motherboard']:
        names=[item.get('name') for item in items(section) if item.get('name')]
        window.label(t('hw.'+section)+': '+('; '.join(names) if names else t('hw.unknown')),layout=summary)
    installed=sum(item.get('capacityBytes') or 0 for item in items('memory'))
    if installed:window.label(t('hw.installedMemory')+': '+format_value('capacityBytes',installed,language,t),layout=summary)
    for system in items('system'):
        window.label(t('hw.fields.usableMemoryBytes')+': '+format_value('usableMemoryBytes',system.get('usableMemoryBytes'),language,t),layout=summary)
    for gpu in items('gpu'):
        value=format_value('dedicatedVideoBytes',gpu.get('dedicatedVideoBytes'),language,t)
        window.label(str(gpu.get('name','GPU'))+' · '+t('hw.fields.dedicatedVideoBytes')+': '+value,layout=summary)
    window.label(t('hw.vramHelp'))
    search=QLineEdit()
    search.setObjectName('hardware-search');search.setPlaceholderText(t('hw.search'));search.setAccessibleName(t('hw.search'));window.body.addWidget(search)
    category=QComboBox();category.setObjectName('hardware-category');category.setAccessibleName(t('hw.category'));category.addItem(t('hw.all'),'all')
    for section in sections:category.addItem(t('hw.'+section['id']),section['id'])
    window.body.addWidget(category)
    tree=QTreeWidget();tree.setObjectName('hardware-tree');tree.setColumnCount(2);tree.setHeaderLabels([t('hw.property'),t('hw.value')]);tree.setWordWrap(True);tree.setMinimumHeight(360);tree.setAccessibleName(t('hardware'))
    tree.header().setSectionResizeMode(0,QHeaderView.Interactive);tree.header().setSectionResizeMode(1,QHeaderView.Stretch);tree.setColumnWidth(0,280)
    window.body.addWidget(tree)
    def populate():
        tree.clear();query=search.text().strip().casefold();selection=category.currentData()
        for section in sections:
            if selection!='all' and section['id']!=selection:continue
            rows=section.get('items',[])
            matching=[row for row in rows if not query or any(query in str(value).casefold() or query in t('hw.fields.'+key).casefold() for key,value in row.items()) or query in t('hw.'+section['id']).casefold()]
            if query and not matching:continue
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
