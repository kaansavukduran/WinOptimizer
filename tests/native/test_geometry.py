"""Measured desktop geometry regressions for AIONIA 1.5; no physical device claim."""
import copy
import pytest
from PySide6.QtCore import QPoint,Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QBoxLayout,QPushButton
from test_interface import application,window
from widgets import ActionRow,Button

@pytest.mark.parametrize('language',['tr','en'])
@pytest.mark.parametrize('profile',[(1600,100,100),(540,100,100),(540,200,125)])
def test_care_actions_share_geometry_without_squeezing_copy_and_resize_keeps_state(window,application,language,profile):
 w,b=window;width,scale,text=profile
 w.settings.update(language=language,scale=scale,textSize=text,font='dyslexic',operationDetails=False)
 w.state['milestones']=['health'];w.resize(width,900);w.appearance();w.go('home');QTest.qWait(80)
 before=copy.deepcopy(b.calls);rows=w.scroll.widget().findChildren(ActionRow)
 assert len(rows)==3 and len({r.action.width() for r in rows})==1
 assert all(r.row.direction()==QBoxLayout.TopToBottom or r.copy.width()>=r.width()/2 for r in rows)
 w.resize(540 if width>900 else 1600,900);QTest.qWait(80)
 assert len({r.action.width() for r in rows})==1 and w.scroll.horizontalScrollBar().maximum()==0
 assert w.state['milestones']==['health'] and b.calls==before

@pytest.mark.parametrize('page',['home','drivers','settings'])
def test_wide_content_is_bounded_centered_and_short_auxiliary_actions_are_not_stretched(window,application,page):
 w,b=window;w.settings.update(operationDetails=False,scale=100,textSize=100,font='system');w.resize(1600,1000);w.appearance();w.page=page;w.render();QTest.qWait(80)
 body=w.scroll.widget();view=w.scroll.viewport();offset=body.mapTo(view,QPoint(0,0)).x()
 assert body.width()<=1120 and abs(2*offset+body.width()-view.width())<=2
 quick=body.findChild(Button,'quick-appearance')
 assert quick.width()<=quick.sizeHint().width() and quick.sizePolicy().hasHeightForWidth()
 assert w.help_button.width()<=w.help_button.sizeHint().width() and w.help_button.sizePolicy().hasHeightForWidth()
 if w.page_picker.isVisible():assert w.page_picker.count()==10

def test_hover_focus_and_press_keep_button_outer_geometry_and_activate_once(window,application):
 w,b=window;w.go('home');QTest.qWait(60)
 button=w.scroll.widget().findChild(QPushButton,'journey-open-health');rect=button.geometry()
 QTest.mouseMove(button,button.rect().center());button.setFocus();QTest.qWait(20);assert button.geometry()==rect
 QTest.mousePress(button,Qt.LeftButton);QTest.qWait(20);assert button.geometry()==rect
 QTest.mouseRelease(button,Qt.LeftButton);QTest.qWait(40)
 assert w.focusWidget().objectName()=='health-scan'
 assert not any(c=='health' for c,_ in b.calls)

def test_live_appearance_changes_scale_bold_care_titles_and_keep_action_family_without_render(window,application):
 from PySide6.QtWidgets import QLabel
 w,b=window;w.go('home');QTest.qWait(50);body=w.scroll.widget();rows=body.findChildren(ActionRow)
 w.save_setting('scale',150);QTest.qWait(80)
 assert body is w.scroll.widget() and all(label.font().pointSizeF()==w.font().pointSizeF() and label.font().bold() for label in body.findChildren(QLabel) if label.property('careTitle'))
 assert len({r.action.width() for r in rows})==1
 assert all(button.height()>=button.heightForWidth(button.width()) for button in body.findChildren(Button) if button.isVisible())
 assert not any(c=='health' for c,_ in b.calls)
