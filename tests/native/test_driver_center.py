import copy
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication,QComboBox,QLineEdit,QTreeWidget,QPushButton,QDialog,QDialogButtonBox
from PySide6.QtTest import QTest
from test_interface import application,window

DRIVERS=[dict(id='PCI\\ONE',name='GPU fixture',version='2.0',provider='Vendor A',problem=0,signed=True,inf='one.inf',deviceClass='Display',date='2026-11-10T10:00:00Z'),dict(id='PCI\\TWO',name='Audio fixture',version='1.2',provider='Vendor B',problem=28,signed=False),dict(id='PCI\\THREE',name='Unknown fixture',problem=None,signed=None)]

@pytest.mark.parametrize('language',['tr','en'])
def test_inventory_search_problem_filter_and_navigation_keep_results(window,application,language):
    w,b=window;w.settings['language']=language;w.state['drivers']=copy.deepcopy(DRIVERS);w.driver_section='inventory';w.go('drivers');application.processEvents()
    tree=w.scroll.widget().findChild(QTreeWidget,'driver-inventory-tree');assert tree.topLevelItemCount()==3
    search=w.scroll.widget().findChild(QLineEdit,'driver-search');search.setText('vendor b');assert tree.topLevelItemCount()==1
    search.clear();w.scroll.widget().findChild(QComboBox,'driver-filter').setCurrentIndex(1);assert tree.topLevelItemCount()==1 and '28' in tree.topLevelItem(0).text(3)
    w.go('home');w.go('drivers');assert w.scroll.widget().findChild(QComboBox,'driver-filter').currentData()=='issues'
    assert w.scroll.widget().findChild(QTreeWidget,'driver-inventory-tree').topLevelItemCount()==1
    assert not any(c=='drivers' for c,p in b.calls)

def test_ignore_selection_is_a_single_batch_and_filters_the_shared_report(window):
    w,b=window;original=b.call
    def call(cmd,payload=None,callback=None):
        if cmd=='updates.ignore-many':b.calls.append((cmd,copy.deepcopy(payload)));callback(dict(ok=True,data={'ignored':payload['ids']}))
        else:original(cmd,payload,callback)
    b.call=call;w.state['updates']=[dict(id=str(i),name=f'Driver {i}') for i in range(3)]
    w.state['report']=dict(findings=[dict(id='update:'+str(i)) for i in range(3)]+[dict(id='device:keep')]);w.go('drivers')
    tree=w.scroll.widget().findChild(QTreeWidget,'driver-updates-tree')
    for index in (0,2):tree.topLevelItem(index).setCheckState(0,Qt.Checked)
    w.scroll.widget().findChild(QPushButton,'driver-ignore-selected').click()
    assert ('updates.ignore-many',{'ids':['0','2']}) in b.calls
    assert [r['id'] for r in w.state['updates']]==['1']
    assert [r['id'] for r in w.state['report']['findings']]==['update:1','device:keep']
    assert not any(c in ('windows-install','diagnostics.updates') for c,p in b.calls)

def test_restore_all_ignored_is_local_and_requires_a_fresh_offer_check(window):
    w,b=window;w.state['library']=dict(packages=[],ignored=[dict(id='a',name='A'),dict(id='b',name='B')]);w.driver_section='ignored';original=b.call
    def call(cmd,payload=None,callback=None):
        if cmd=='updates.unignore-many':b.calls.append((cmd,payload));callback(dict(ok=True,data={'restored':payload['ids']}))
        else:original(cmd,payload,callback)
    b.call=call;w.go('drivers');w.scroll.widget().findChild(QPushButton,'driver-restore-all').click()
    assert ('updates.unignore-many',dict(ids=['a','b'])) in b.calls and w.state['library']['ignored']==[]
    assert not any(c in ('windows-install','windows-updates') for c,p in b.calls)

def test_backups_have_dates_and_inspection_does_not_apply(window):
    w,b=window;w.driver_section='backups';w.state['library']=dict(packages=[dict(id='DriverBackups/fixture',kind='DriverBackups',at='2026-11-10T10:00:00Z')],ignored=[]);w.go('drivers')
    button=w.scroll.widget().findChild(QPushButton,'driver-inspect-DriverBackups/fixture');assert button and 'fixture' not in button.text() and '2026' in button.text()
    original=b.call
    def call(cmd,payload=None,callback=None):
        if cmd=='package.inspect':b.calls.append((cmd,payload));callback(dict(ok=True,data=dict(id='plan',libraryId=payload['id'],candidates=[dict(id='a.inf',name='A',eligible=False,signed=False)])))
        else:original(cmd,payload,callback)
    b.call=call;button.click();assert ('package.inspect',dict(id='DriverBackups/fixture')) in b.calls
    apply=w.scroll.widget().findChild(QPushButton,'driver-package-apply');assert not apply.isEnabled()
    assert not any(c=='package.apply' for c,p in b.calls)

def test_package_apply_requires_selection_and_confirmation_then_discards_the_plan(window,application):
    w,b=window;w.driver_section='backups';w.state['package']=dict(id='plan',candidates=[dict(id='a.inf',name='A',eligible=True),dict(id='bad.inf',name='Bad',eligible=False)]);w.go('drivers');w.show_result=lambda _:None
    tree=w.scroll.widget().findChild(QTreeWidget,'driver-package-tree');assert not tree.topLevelItem(1).flags() & Qt.ItemIsUserCheckable
    w.scroll.widget().findChild(QPushButton,'driver-package-apply').click();assert not any(c=='package.apply' for c,p in b.calls)
    tree.topLevelItem(0).setCheckState(0,Qt.Checked)
    from PySide6.QtCore import QTimer
    QTimer.singleShot(0,lambda:QApplication.activeModalWidget().reject())
    w.scroll.widget().findChild(QPushButton,'driver-package-apply').click();assert not any(c=='package.apply' for c,p in b.calls)
    original=b.call
    def call(cmd,payload=None,callback=None):
        if cmd=='package.apply':b.calls.append((cmd,payload));callback(dict(ok=True,data=dict(success=True,items=[],changes=[])))
        else:original(cmd,payload,callback)
    b.call=call
    QTimer.singleShot(0,lambda:QApplication.activeModalWidget().findChild(QDialogButtonBox).button(QDialogButtonBox.Ok).click())
    w.scroll.widget().findChild(QPushButton,'driver-package-apply').click()
    assert ('package.apply',dict(planId='plan',ids=['a.inf'],confirm=True)) in b.calls and 'package' not in w.state

@pytest.mark.parametrize('language',['tr','en'])
def test_sections_and_offline_flow_are_accessible_with_large_text(window,application,language):
    w,_=window;w.settings.update(language=language,scale=200,textSize=125,font='dyslexic',operationDetails=False);w.resize(540,900);w.appearance();w.go('drivers')
    picker=w.scroll.widget().findChild(QComboBox,'driver-section');picker.setCurrentIndex(picker.findData('offline'));application.processEvents()
    button=w.scroll.widget().findChild(QPushButton,'driver-offline-import');assert button
    from test_recovery import until
    def visible():
        w.scroll.ensureWidgetVisible(button);application.processEvents()
        return w.scroll.viewport().rect().contains(button.mapTo(w.scroll.viewport(),button.rect().center()))
    until(application,visible);button.click();assert w.driver_section=='backups'

def test_workshop_categories_show_related_tools_and_link_to_driver_center(window):
    w,_=window;w.go('workshop');assert w.scroll.widget().findChild(QPushButton,'w.loadFocus') is None
    picker=w.scroll.widget().findChild(QComboBox,'workshop-section');picker.setCurrentIndex(picker.findData('focus'))
    assert w.scroll.widget().findChild(QPushButton,'w.loadFocus') is not None and w.scroll.widget().findChild(QPushButton,'w.prepare') is None
    w.scroll.widget().findChild(QPushButton,'workshop-driver-tools').click();assert w.page=='drivers' and w.driver_section=='backups'
