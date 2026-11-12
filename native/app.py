"""Native Windows Qt Widgets interface. No Chromium, WebEngine, HTML or Electron."""
import json
from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime

from PySide6.QtCore import Qt, QTimer, QUrl, QLocale, QLockFile, QSignalBlocker
from PySide6.QtGui import QFont, QFontDatabase, QIcon, QDesktopServices, QPalette, QColor
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QGroupBox, QCheckBox, QComboBox, QSpinBox,
    QSlider, QDoubleSpinBox, QFormLayout, QProgressBar, QTreeWidget, QTreeWidgetItem,
    QAbstractItemView, QFileDialog, QMessageBox, QDialog, QDialogButtonBox, QLineEdit,
    QSizePolicy, QSplitter, QGridLayout)
from bridge import Bridge
from mascot import Aion
from widgets import Paragraph, Button as QPushButton, CheckBox as QCheckBox, Choice as QComboBox
import recovery
import personalize
import usability

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
VERSION = json.loads((ROOT / 'package.json').read_text(encoding='utf-8'))['version']
LOCALES = json.loads((ROOT / 'native/locales.json').read_text(encoding='utf-8'))
NATIVE = {
 'tr': dict(native='Yerel Windows uygulaması · Chromium gerekmez', trace='İşlem adımları', source='Kaynak', step='Adım', result='Durum', time='Saat', running='Çalışıyor', complete='Tamamlandı', failed='Başarısız', skipped='Atlandı', cancelled='İptal edildi', interrupted='Önceki işlem yarıda kesildi', attention='İncelenecek sonuçlar var', app='Uygulama', native_source='Windows', waiting='Windows yanıtı bekleniyor. İşlem sürüyor; henüz sonuç yok.', no_trace='Henüz işlem yapılmadı. Başlamak için Tara ve Düzelt’i kullan.', export_log='Günlüğü dışa aktar', elapsed='Geçen süre', more_events='Son {shown} / {total} adım gösteriliyor. Dışa aktarma bütün günlüğü içerir.', request='İşlem isteği', launch='Windows işlemini başlat', response='Windows yanıtı', devices='Aygıtlar ve sürücüler', audio='Ses servisleri', network='Ağ bağlantıları', display='Ekran bilgileri', runtimes='Oyun bileşenleri', dns='DNS denetimi', backup='Sürücü yedeği', download='Paket indirme', install='Sürücü kurulumu', install_item='Sürücü başına kurulum sonucu', offline='Çevrimiçi kontrol kapalı', no_link='Etkin ağ bağlantısı yok', excluded='Firmware kapsam dışında', firmware='Firmware teklifleri', ignored='Kullanıcının atladığı teklifler', default='Varsayılana dön', choices='Ayrıntılı seçenekler', issues='Sorunlar ve öneriler', other='Diğer sonuçlar', all_results='Bütün sonuçları göster', local_data='Kayıtlar yalnız bu cihazda tutulur.', error='İşlem tamamlanamadı', retry='Yeniden dene', done='İşlem tamamlandı. Sonuçları ve işlem adımlarını incele.', close_busy='İşlem sürerken uygulamayı kapatamazsın. Bitmesini bekle; taramayı İptal ile durdurabilirsin.', confirm_count='{count} öğe için devam edilsin mi?', select='Seç', language='Dil', current='Yüklü sürüm', values='Ayrıntılar', no_items='Gösterilecek öğe yok.', port='Portable sürüm', pet='Aion’u sev', pet_head='Aion başının sevilmesine mutlu oldu.', pet_belly='Aion gülümsedi!', pet_tail='Aion kuyruğunu oynattı.', pet_feet='Aion’un ayakları gıdıklandı!', pause='Aion animasyonunu duraklat', play='Aion animasyonunu oynat', read_only='Yazılabilir bir klasör seç. Data klasörü oluşturulamadı.', backend_error='Windows işlem motoruyla bağlantı kurulamadı. Aşağıdaki açıklamayı incele.', save='Kaydedildi', steps='1. Tara → 2. Sonuçları incele → 3. Onayla ve uygula', ready='Hazır', scope='Bir tarama her sorunu saptayamaz. Kontrol edilemeyen sonuçlar sağlıklı sayılmaz.', restore_note='Windows daha uygun sürücüyü korumuş olabilir; paket kabulü aygıt sürümünün değiştiği anlamına gelmez.', files='Dosya', reason='Neden / sonuç kodu', automatic_backup='Mevcut üçüncü taraf sürücüler önce otomatik yedeklenir.', choose_plan='Mevcut güç planı', normal_close='Seçilen kullanıcı pencerelerine normal kapatma isteği gönderilir. Açık çalışmalarını kaydet.', accepted='Microsoft lisans koşullarını kabul ediyorum', preview='Kaynak önizlemesi: Windows işlemleri yalnız Windows üzerinde çalışır.', show_details='Ayrıntıları göster', recent='Son işlem', no_background='Tarama ve güncelleme sen başlatınca çalışır.', filter='Sonuç filtresi', amount='Adet', report_saved='Dosya kaydedildi.', choose_color='Vurgu rengi', engine='Arayüz: Python + Qt Widgets; Windows işlemleri: Node.js + PowerShell. Gerekli çalışma zamanları paketin içindedir.'),
 'en': dict(native='Native Windows app · No Chromium required', trace='Operation steps', source='Source', step='Step', result='Status', time='Time', running='Running', complete='Completed', failed='Failed', skipped='Skipped', cancelled='Cancelled', interrupted='Previous operation was interrupted', attention='Some results need attention', app='Application', native_source='Windows', waiting='Waiting for a Windows response. The operation is running; no result yet.', no_trace='No operations yet. Start with Scan & Fix.', export_log='Export operation log', elapsed='Elapsed', more_events='Showing the last {shown} / {total} steps. Export includes the entire log.', request='Operation request', launch='Launch Windows operation', response='Windows response', devices='Devices and drivers', audio='Audio services', network='Network connections', display='Display information', runtimes='Game runtimes', dns='DNS check', backup='Driver backup', download='Package download', install='Driver installation', install_item='Per-driver installation result', offline='Online checks are off', no_link='No active network link', excluded='Firmware is outside scope', firmware='Firmware offers', ignored='Offers skipped by the user', default='Reset to default', choices='Advanced options', issues='Issues and suggestions', other='Other results', all_results='Show all results', local_data='Records stay on this device.', error='The operation could not finish', retry='Try again', done='Operation completed. Review its results and steps.', close_busy='An operation is running. Wait for it to finish; Cancel can stop a read-only scan.', confirm_count='Continue with {count} items?', select='Select', language='Language', current='Installed version', values='Details', no_items='No items to display.', port='Portable mode', pet='Pet Aion', pet_head='Aion enjoyed the head pats.', pet_belly='Aion smiles!', pet_tail='Aion wiggles its tail.', pet_feet='Aion has ticklish feet!', pause='Pause Aion animation', play='Play Aion animation', read_only='Choose a writable folder. Data could not be created.', backend_error='The Windows operation engine is unavailable. Review the guidance below.', save='Saved', steps='1. Scan → 2. Review → 3. Confirm and apply', ready='Ready', scope='One scan cannot detect every issue. Unavailable checks are not treated as healthy.', restore_note='Windows may retain a better driver; package acceptance does not prove a device version changed.', files='Files', reason='Reason / result code', automatic_backup='Current third-party drivers are backed up automatically first.', choose_plan='Existing power plan', normal_close='Selected user windows receive normal close requests. Save your open work.', accepted='I accept Microsoft license terms', preview='Source preview: Windows operations run on Windows only.', show_details='Show details', recent='Last operation', no_background='Scanning and updates start when you request them.', filter='Result filter', amount='Count', report_saved='File saved.', choose_color='Accent color', engine='Interface: Python + Qt Widgets; Windows operations: Node.js + PowerShell. Required runtimes are included in the package.')
}

NATIVE['tr'].update(cleanup_scan='Temizlik adaylarını tara', cleanup_exclusion='Temizlik kapsamı dışında', missing='Klasör bulunamadı', unavailable='Dosya veya klasöre erişilemedi', links='Bağlantı/junction koruması', recent='Son 7 gün içinde değişmiş dosya', changed='Tarama sırasında değişmiş öğe', limit='10.000 aday sınırına ulaşıldı')
NATIVE['en'].update(cleanup_scan='Scan cleanup candidates', cleanup_exclusion='Excluded from cleanup', missing='Folder was not found', unavailable='File or folder could not be accessed', links='Link/junction protection', recent='File changed within the last 7 days', changed='Item changed during scanning', limit='Reached the 10,000 candidate limit')

def text(language, key):
    if key.startswith('n.'):
        return NATIVE[language].get(key[2:], key[2:])
    value = LOCALES[language]
    for part in key.split('.'):
        if not isinstance(value, dict) or part not in value:
            return key
        value = value[part]
    return value

class Window(QMainWindow):
    def __init__(self, bridge, data, portable=False):
        super().__init__()
        self.bridge, self.data, self.portable = bridge, data, portable
        self.settings = dict(language='tr', theme='system', scale=100, textSize=100, font='system', motion=True, companion=True, gamification=True)
        self.resource_root=ROOT
        self.page, self.busy, self.ready = 'home', False, False
        self.backend_lost, self.failure = False, None
        # Qt can resize the window before the asynchronous bootstrap replies.
        self.details_expanded = True
        self.state, self.selected, self.trace, self.trace_signature = {}, set(), None, None
        self.save_serial = 0
        self.settings_section = 'appearance'
        self.driver_section, self.workshop_section = 'updates', 'runtimes'
        self.aion_paused = False
        self.last_error, self.last_request, self.scan_online, self.filter_status = None, None, True, 'all'
        self.setWindowTitle('WinOptimizer Aion')
        self.setWindowIcon(QIcon(str(ROOT / 'public/assets/aion.ico')))
        self.resize(1240, 900)
        self.setMinimumSize(480, 560)
        for font in ('OpenDyslexic-Regular.otf', 'OpenDyslexic-Bold.otf'):
            QFontDatabase.addApplicationFont(str(ROOT / 'public/fonts' / font))
        central = QWidget()
        self.setCentralWidget(central)
        self.outer = QVBoxLayout(central)
        self.nav_widget, self.nav_layout = QWidget(), QHBoxLayout()
        self.nav_widget.setLayout(self.nav_layout)
        self.nav_scroll = QScrollArea()
        self.nav_scroll.setWidget(self.nav_widget)
        self.nav_scroll.setWidgetResizable(True)
        self.nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.nav_scroll.setMinimumHeight(64)
        self.nav_scroll.setMaximumHeight(100)
        self.outer.addWidget(self.nav_scroll)
        self.notice = Paragraph('')
        self.notice.setAccessibleName(self.t('n.result'))
        self.outer.addWidget(self.notice)
        self.progress = QProgressBar()
        self.progress.hide()
        self.outer.addWidget(self.progress)
        self.cancel = QPushButton(self.t('cancel'))
        self.cancel.setObjectName('cancel-scan')
        self.cancel.clicked.connect(lambda: self.bridge.call('diagnostics.cancel'))
        self.cancel.hide()
        self.outer.addWidget(self.cancel)
        splitter = QSplitter(Qt.Vertical)
        self.splitter = splitter
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        splitter.addWidget(self.scroll)
        log = QWidget()
        layout = QVBoxLayout(log)
        self.log_panel = log
        header = QHBoxLayout()
        self.log_title = QLabel(self.t('n.trace'))
        self.log_title.setWordWrap(True)
        header.addWidget(self.log_title,1)
        self.log_toggle = QPushButton()
        self.log_toggle.setObjectName('operation-details-toggle')
        self.log_toggle.setCheckable(True)
        self.log_toggle.clicked.connect(lambda checked:self.set_operation_details(checked,True))
        header.addWidget(self.log_toggle)
        layout.addLayout(header)
        self.log_hint = QLabel()
        self.log_hint.setWordWrap(True)
        layout.addWidget(self.log_hint)
        self.log_details = QWidget()
        detail_layout = QVBoxLayout(self.log_details)
        detail_layout.setContentsMargins(0,0,0,0)
        self.log = QTreeWidget()
        self.log.setColumnCount(5)
        self.log.setHeaderLabels([self.t('n.time'), self.t('n.source'), self.t('n.step'), self.t('n.result'), self.t('n.reason')])
        self.log.setAccessibleName(self.t('n.trace'))
        self.log.setRootIsDecorated(False)
        self.log.setWordWrap(True)
        self.log.setMinimumHeight(170)
        detail_layout.addWidget(self.log)
        self.export_log = QPushButton(self.t('n.export_log'))
        self.export_log.clicked.connect(lambda: self.export('report.export'))
        detail_layout.addWidget(self.export_log)
        layout.addWidget(self.log_details)
        self.log_scroll=QScrollArea()
        self.log_scroll.setWidgetResizable(True)
        self.log_scroll.setWidget(log)
        self.log_scroll.setAccessibleName(self.t('n.trace'))
        self.log_scroll.setMinimumHeight(80)
        splitter.addWidget(self.log_scroll)
        splitter.setSizes([620, 200])
        self.outer.addWidget(splitter, 1)
        self.footer = QLabel()
        self.footer.setWordWrap(True)
        self.outer.addWidget(self.footer)
        usability.setup(self)
        self.notice.setText(self.t('ux.loading'))
        self.progress.setRange(0,0)
        self.progress.show()
        self.appearance()
        usability.sync(self)
        bridge.failed.connect(self.backend_failed)
        bridge.call('bootstrap', callback=self.bootstrap)
        self.poller = QTimer(self)
        self.poller.timeout.connect(self.poll)
        if not self.backend_lost:
            self.poller.start(700)

    def t(self, key):
        return text(self.settings.get('language', 'tr'), key)

    def bootstrap(self, reply):
        if not reply.get('ok'):
            self.error(reply.get('error', 'BACKEND_UNAVAILABLE'))
            self.appearance()
            return
        data = reply['data']
        self.settings, self.portable = data['settings'], data.get('portable', self.portable)
        self.state['milestones'] = data.get('milestones', [])
        self.ready = True
        self.progress.hide()
        self.notice.setText(self.t('ux.ready'))
        self.appearance()
        self.render()

    def appearance(self):
        scale = self.settings.get('scale', 100) / 100
        system_font = QFontDatabase.systemFont(QFontDatabase.GeneralFont).family()
        font_name = {'system': system_font, 'readable': 'Verdana', 'dyslexic': 'OpenDyslexic'}.get(self.settings.get('font'), system_font)
        font = QFont(font_name)
        font.setPointSizeF(10 * scale * self.settings.get('textSize', 100) / 100)
        font.setLetterSpacing(QFont.AbsoluteSpacing, self.settings.get('letterSpacing', 0))
        QApplication.setFont(font)
        self.setFont(font)
        for paragraph in self.findChildren(Paragraph):
            use=QFont(font)
            if paragraph.property('heading'):
                use.setPointSizeF(font.pointSizeF()*(1.35 if paragraph.property('headingLevel')!=2 else 1.12));use.setBold(True)
            paragraph.setFont(use)
            paragraph.document().setDefaultFont(use)
        for label in self.findChildren(QLabel):
            if label.property('heading'):
                heading=QFont(font);heading.setPointSizeF(font.pointSizeF()*(1.35 if label.property('headingLevel')!=2 else 1.12));heading.setBold(True);label.setFont(heading)
        theme = self.settings.get('theme', 'system')
        dark = theme in ('dark', 'contrast') or (theme == 'system' and QApplication.palette().window().color().lightness() < 128)
        high = theme == 'contrast'
        bg, surface, fg, line, accent = ('#000000', '#111111', '#ffffff', '#ffffff', '#ffff00') if high else ('#18151e', '#29222f', '#fff5fa', '#aa8fa8', self.settings.get('accent', '#b82e69')) if dark else ('#fcf7fb', '#ffffff', '#302838', '#8e748a', self.settings.get('accent', '#b82e69'))
        accent_ink=personalize.ink(accent)
        focus=personalize.focus_color(accent,bg,surface)
        danger,success=('#ffff00','#ffffff') if high else ('#ffb0bd','#9ce2c2') if dark else ('#9c2242','#1c6849')
        self.visual_tokens=dict(background=bg,surface=surface,text=fg,border=line,accent=accent,accentInk=accent_ink,focus=focus,danger=danger,success=success)
        pad = round((6 if self.settings.get('density')=='compact' else 8) * scale)
        self.nav_scroll.setFixedHeight(round(64*scale))
        self.setStyleSheet(f'QWidget{{color:{fg};background:{bg};selection-background-color:{accent};selection-color:{accent_ink};}} QGroupBox,QTreeWidget,QLineEdit,QComboBox,QSpinBox,QDoubleSpinBox{{background:{surface};border:1px solid {line};border-radius:4px;padding:{pad}px;}} QGroupBox{{margin-top:14px;padding-top:24px;}} QGroupBox[section="true"]{{margin-top:0;padding-top:12px;}} QGroupBox::title{{subcontrol-origin:margin;left:12px;}} QPushButton{{background:{surface};border:1px solid {line};border-radius:4px;padding:{pad}px;min-height:{round(24*scale)}px;}} QPushButton:hover{{border:2px solid {focus};}} QPushButton:pressed{{border:3px solid {focus};}} QPushButton[danger="true"]{{color:{danger};border:2px solid {danger};}} QPushButton:disabled{{color:#888888;}} QPushButton[primary="true"]{{background:{accent};color:{accent_ink};font-weight:bold;}} QPushButton:checked{{border:2px solid {focus};}} QPushButton:focus,QComboBox:focus,QLineEdit:focus,QSpinBox:focus,QDoubleSpinBox:focus,QTreeWidget:focus,QTextEdit:focus{{border:3px solid {focus};}} QCheckBox:focus,QSlider:focus,QGroupBox:focus{{outline:2px solid {focus};}} QHeaderView::section{{background:{surface};padding:{pad}px;}} QProgressBar{{border:1px solid {line};min-height:12px;}} QProgressBar::chunk{{background:{accent};}} QCheckBox{{spacing:8px;padding:6px;}} QLabel{{background:transparent;}} QToolTip{{background:{surface};color:{fg};border:1px solid {line};}} QLabel#app-brand{{font-weight:bold;}}')
        self.outer.setSpacing(round(10 * scale))
        self.set_operation_details(self.settings.get('operationDetails',True))
        if hasattr(self,'body'):self.body.setSpacing(round((10 if self.settings.get('density')=='compact' else 14)*scale))
        self.footer.setText(f'{VERSION} · Windows x64 · {self.t("n.port") if self.portable else "Setup"}')
        personalize.sync(self)
        usability.adapt(self)

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def render(self):
        if not self.ready and not self.failure:
            return
        self.aion = None
        self.clear_layout(self.nav_layout)
        # Settings remains the last, rightmost navigation item at every window size.
        for key in (usability.PAGES if self.ready else ()):
            button = QPushButton(self.t(key))
            button.setObjectName('nav-' + key)
            button.setCheckable(True)
            button.setChecked(self.page == key)
            button.clicked.connect(lambda _, key=key: self.go(key))
            self.nav_layout.addWidget(button)
        usability.sync(self)
        body = QWidget()
        self.body = QVBoxLayout(body)
        self.body.setSpacing(round(14 * self.settings.get('scale', 100) / 100))
        self.actions = []
        if self.ready:
            guided_home=self.page=='home' and not self.failure
            if guided_home:
                self.label(self.t('home'),heading=True)
                from journey import render
                render(self)
            personalize.header(self,title=not guided_home)
        else:self.label('WinOptimizer Aion',heading=True)
        recovery.render(self)
        if self.ready:
            getattr(self, 'page_' + self.page)()
        self.body.addStretch()
        old = self.scroll.takeWidget()
        self.scroll.setWidget(body)
        if old:
            old.deleteLater()
        self.log_title.setText(self.t('n.trace'))
        self.log.setHeaderLabels([self.t('n.time'), self.t('n.source'), self.t('n.step'), self.t('n.result'), self.t('n.reason')])
        self.export_log.setText(self.t('n.export_log'))
        self.trace_signature = None
        self.set_operation_details(self.settings.get('operationDetails',True))
        personalize.sync(self)
        usability.adapt(self)

    def set_operation_details(self, expanded, persist=False):
        changed=getattr(self,'details_expanded',None)!=expanded
        self.details_expanded=expanded
        self.log_details.setVisible(expanded)
        self.log_toggle.setChecked(expanded)
        self.log_toggle.setText(self.t('forge.hide' if expanded else 'forge.show'))
        self.log_toggle.setAccessibleName(self.log_toggle.text())
        self.log_panel.layout().activate()
        self.log_panel.setMaximumHeight(16777215 if expanded else max(self.log_panel.sizeHint().height(),self.log_panel.minimumSizeHint().height(),self.log_panel.layout().totalHeightForWidth(self.log_panel.width())))
        self.log_scroll.setMaximumHeight(self.log_panel.maximumHeight())
        if changed:self.splitter.setSizes([620,200] if expanded else [1000,self.log_panel.maximumHeight()])
        if persist:self.save_setting('operationDetails',expanded)
        usability.adapt(self)

    def go(self, page):
        self.page = page
        self.selected.clear()
        self.render()
        if self.backend_lost:
            return
        if page == 'history':
            self.run('history', callback=lambda r: self.store('history', r), silent=True)
        if page == 'workshop':
            self.run('workshop.library', callback=lambda r: self.store('library', r), silent=True)

    def label(self, value, heading=False, layout=None, level=1):
        label = Paragraph(str(value),1.15 if heading else self.settings.get('lineHeight',1.5))
        if heading:
            label.setProperty('heading',True)
            label.setProperty('headingLevel',level)
            label.setAccessibleName(str(value))
        if heading:
            font = self.font()
            font.setPointSizeF(font.pointSizeF() * (1.35 if level==1 else 1.12))
            font.setBold(True)
            label.setFont(font)
            label.document().setDefaultFont(font)
        (layout or self.body).addWidget(label)
        return label

    def button(self, key, callback, primary=False, layout=None, enabled=True, literal=False, name=None, danger=False):
        button = QPushButton(key if literal else self.t(key))
        button.setObjectName(name or key)
        button.setProperty('primary',primary and (not self.failure or name in ('recovery-retry','recovery-origin','recovery-close')))
        button.setProperty('danger',danger or key in ('purge','disable'))
        button.setEnabled(enabled and not self.busy)
        button.clicked.connect(callback)
        (layout or self.body).addWidget(button)
        self.actions.append(button)
        return button

    def group(self, key, checkable=False, checked=False):
        group = QGroupBox()
        group.setAccessibleName(self.t(key))
        group.setProperty('section',True)
        outer = QVBoxLayout(group)
        self.body.addWidget(group)
        if checkable:
            open_states=self.state.setdefault('disclosures',{})
            toggle=QCheckBox(self.t(key));toggle.setObjectName('section-toggle-'+key)
            toggle.setChecked(open_states.get(key,checked));outer.addWidget(toggle)
            panel=QWidget();inner=QVBoxLayout(panel);inner.setContentsMargins(0,0,0,0)
            outer.addWidget(panel);panel.setVisible(toggle.isChecked())
            toggle.toggled.connect(lambda value:(open_states.update({key:value}),panel.setVisible(value)))
            return inner
        self.label(self.t(key),heading=True,level=2,layout=outer)
        return outer

    def details(self, key, content, layout=None):
        group = QGroupBox(self.t(key))
        group.setCheckable(True)
        group.setChecked(False)
        inner = QVBoxLayout(group)
        label = self.label(content, layout=inner)
        label.hide()
        group.toggled.connect(label.setVisible)
        (layout or self.body).addWidget(group)

    def confirm(self, title, description, names, callback, license=False):
        dialog = QDialog(self)
        dialog.setObjectName('confirm-dialog')
        dialog.setWindowTitle(title)
        dialog.resize(min(660, max(400, self.width() - 60)), 480)
        outer = QVBoxLayout(dialog)
        self.label(description, layout=outer)
        self.label(self.t('n.confirm_count').format(count=len(names)), layout=outer)
        tree = QTreeWidget()
        tree.setHeaderHidden(True)
        for name in names:
            QTreeWidgetItem(tree, [str(name)])
        outer.addWidget(tree)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText(self.t('confirm'))
        buttons.button(QDialogButtonBox.Cancel).setText(self.t('cancel'))
        if license:
            accept = QCheckBox(self.t('n.accepted'))
            buttons.button(QDialogButtonBox.Ok).setEnabled(False)
            accept.toggled.connect(buttons.button(QDialogButtonBox.Ok).setEnabled)
            outer.addWidget(accept)
        outer.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        accepted = dialog.exec() == QDialog.Accepted
        dialog.deleteLater()
        if accepted:
            callback()

    def run(self, command, payload=None, callback=None, silent=False):
        if self.busy:
            return
        if self.backend_lost:
            self.error(self.failure['code'] if self.failure and self.failure['code'] in recovery.BACKEND_ERRORS else 'BACKEND_DISCONNECTED')
            return
        self.busy, self.last_error, self.failure = True, None, None
        self.active_command = command
        self.last_request = (command, payload, callback, silent)
        request = dict(command=command, payload=deepcopy(payload), callback=callback,
                       silent=silent, page=self.page, settings_section=self.settings_section, driver_section=self.driver_section, workshop_section=self.workshop_section)
        self.notice.setText(self.t('n.waiting'))
        total={'hardware':14,'care.snapshot':9}.get(command,0)
        self.progress.setRange(0,total)
        self.progress.setValue(0)
        self.progress.setFormat(self.t('forge.categories').format(done=0,total=total)+' · %p%' if total else '%p%')
        self.progress.show()
        self.cancel.setVisible(command == 'diagnostics.scan')
        for button in self.actions:
            button.setEnabled(False)
        if getattr(self, 'aion', None):
            self.aion.set_state('read' if command in recovery.READ_OPERATIONS or command=='component-check' else 'repair')
        def finished(reply):
            self.busy = False
            self.progress.hide()
            self.cancel.hide()
            if not reply.get('ok'):
                self.last_error = reply.get('error', 'OPERATION_FAILED')
                self.error(self.last_error, request)
                return
            result = reply.get('data')
            failed = isinstance(result, dict) and (result.get('success') is False or result.get('skipped',0)>0 or result.get('conflicts',0)>0 or any(i.get('success') is False for i in result.get('items', [])))
            attention=isinstance(result,dict) and (result.get('needsAttention') is True or any(f.get('status') in ('issue','unknown') for f in result.get('findings',[])))
            self.notice.setText('' if silent else self.t('care.review' if attention else 'partialFailure' if failed else 'n.done'))
            if callback:
                callback(result)
            else:
                self.render()
            if getattr(self, 'aion', None):
                self.aion.set_state('help' if failed or attention else 'idle' if silent else 'celebrate')
            if self.settings.get('sound') and not failed and not silent:QApplication.beep()
            def milestones(reply):
                if reply.get('ok'):
                    updated=reply['data'].get('milestones',[])
                    if updated!=self.state.get('milestones'):
                        self.state['milestones']=updated
                        if self.page=='home':self.render()
            self.bridge.call('history',callback=milestones)
            self.poll()
        self.bridge.call(command, payload, finished)

    def backend_failed(self, code):
        self.backend_lost = True
        if hasattr(self, 'poller'):
            self.poller.stop()
        self.error(code)

    def error(self, code, request=None):
        if not self.ready:self.progress.hide()
        if code in recovery.BACKEND_ERRORS:
            self.backend_lost = True
            if hasattr(self, 'poller'):
                self.poller.stop()
        # Preserve the affected operation when the disconnect signal follows its callback.
        if not (request is None and self.failure and self.failure['code'] in recovery.BACKEND_ERRORS):
            self.failure = dict(code=code, request=request)
        self.last_error = code
        key = {'WINDOWS_ONLY': 'n.preview', 'BACKEND_UNAVAILABLE': 'n.backend_error', 'BACKEND_DISCONNECTED': 'n.backend_error', 'BACKEND_PROTOCOL_FAILED': 'n.backend_error', 'SCAN_EXPIRED': 'errorScan', 'ADMIN_CANCELLED': 'errorAdmin', 'INVALID_SELECTION': 'errorDefault', 'UPDATE_SIGNATURE_INVALID': 'errorSignature', 'UPDATE_HASH_INVALID': 'errorSignature', 'SCAN_CANCELLED': 'cancel', 'OPERATION_TIMEOUT': 'errorTimeout'}.get(code, code if code.startswith('n.') else 'errorDefault')
        self.notice.setText(f'{self.t(key)}  ({code})')
        self.notice.setAccessibleName(self.t('n.error'))
        self.render()

    def store(self, key, value):
        self.state[key] = value
        if key=='report' and isinstance(value,dict) and 'care' in value:self.state['care']=value['care']
        self.render()

    def poll(self):
        if not self.ready or self.backend_lost:
            return
        def receive(reply):
            if not reply.get('ok'):
                return
            data = reply.get('data') or {}
            trace = data.get('trace')
            if data.get('total') and self.busy:
                self.progress.setRange(0, max(1, data['total']))
                self.progress.setValue(data.get('bytes', 0))
                self.progress.setFormat(f'{data.get("bytes", 0)} / {data["total"]} bytes')
            if trace and self.busy and trace.get('command')==getattr(self,'active_command',None) and trace.get('status')=='running':
                try:
                    seconds=int((datetime.now().astimezone()-datetime.fromisoformat(trace['at'].replace('Z','+00:00'))).total_seconds())
                    self.notice.setText(f'{self.t("n.running")} · {self.t("n.elapsed")}: {seconds}s · {self.t("n.waiting")}')
                except (ValueError,KeyError):pass
                if trace.get('command') in ('hardware','care.snapshot'):
                    if trace['command']=='hardware':
                        from hardware import progress_state
                        prefix='hw.'
                    else:
                        from care import progress_state
                        prefix='care.'
                    done,total,current=progress_state(trace)
                    self.progress.setRange(0,total);self.progress.setValue(done)
                    self.progress.setFormat(self.t('forge.categories').format(done=done,total=total)+' · %p%')
                    message=self.t('forge.finalizing') if done==total else self.t(prefix+current) if current else self.t('n.waiting')
                    self.notice.setText(self.t('n.running')+' · '+self.t('forge.categories').format(done=done,total=total)+' · '+message)
                elif trace['command']=='diagnostics.scan':
                    current=next((e for e in reversed(trace.get('events',[])) if e.get('origin')=='native' and e.get('step','').startswith('care-')),None)
                    if current and current.get('status')=='running':
                        self.notice.setText(self.t('n.running')+' · '+self.t('care.'+current['step'][5:])+' · '+self.t('n.waiting'))
            signature = json.dumps(trace, ensure_ascii=False)
            if signature == self.trace_signature:
                return
            self.trace, self.trace_signature = trace, signature
            self.log.clear()
            if not trace:
                self.log_hint.setText(self.t('n.no_trace'))
                self.set_operation_details(self.settings.get('operationDetails',True))
                return
            events = trace.get('events', [])
            latest={}
            for event in events:
                if event.get('step') in ('request','launch','response'):continue
                target=(event.get('item'),event.get('count')) if event.get('step')=='install-item' else None
                latest[(event.get('origin'),event.get('action'),event.get('step'),target)]=event
            display=list(latest.values())
            for event in display[-60:]:
                time = event.get('at', '')[11:19]
                reason = event.get('reason', '')
                translated = self.t('n.' + reason) if reason in ('offline', 'no-link', 'excluded','missing','unavailable','links','recent','changed','limit') else reason
                detail = ' · '.join(str(x) for x in (event.get('item'), translated, event.get('count')) if x is not None and x != '')
                step = self.t('hw.'+event['step'][9:]) if event.get('step','').startswith('hardware-') else self.t('n.' + event.get('step', 'request').replace('-', '_'))
                if event.get('step','').startswith('care-'):step=self.t('care.'+event['step'][5:])
                if not event.get('step','').startswith(('hardware-','care-')) and event.get('step','').replace('-','_') not in NATIVE[self.settings['language']]:
                    step = self.action_name(event.get('step') if event.get('step')=='windows-updates' else event.get('action', ''))
                item=QTreeWidgetItem(self.log, [time, self.t('n.native_source' if event.get('origin') == 'native' else 'n.app'), step, ('Başladı' if self.settings['language']=='tr' else 'Started') if event.get('status')=='running' else self.t('n.' + event.get('status', 'running')), detail])
                if event.get('status') in ('complete','failed'):
                    item.setForeground(3,QColor(self.visual_tokens['success' if event['status']=='complete' else 'danger']))
            self.log.resizeColumnToContents(0)
            self.log.resizeColumnToContents(1)
            self.log.resizeColumnToContents(2)
            if trace.get('status')=='running':self.log.scrollToBottom()
            else:self.log.scrollToTop()
            self.log_title.setText(f'{self.t("n.trace")} · {self.action_name(trace.get("command", ""))} · {self.t("n." + trace.get("status", "running"))}')
            counts={status:sum(e.get('status')==status for e in display) for status in ('complete','failed','skipped')}
            summary=' · '.join(f'{self.t("n."+status)}: {count}' for status,count in counts.items())
            self.log_hint.setText(summary+' · '+self.t('n.more_events').format(shown=min(60,len(display)),total=len(events)))
            self.set_operation_details(self.settings.get('operationDetails',True))
        self.bridge.call('operation.status', callback=receive)

    def action_name(self, command):
        keys = {'care':'care.scanRecords','care.snapshot':'windowsCare','component-check':'care.component','hardware':'hardware','updates.check':'checkUpdates','updates.install':'installUpdate','diagnostics.scan':'scanFix', 'diagnostics.updates':'updateAllDrivers', 'diagnostics.repair':'d.repair', 'health':'healthScan', 'drivers':'inventory', 'windows-updates':'checkDrivers', 'windows-install':'updateAllDrivers', 'driver-backup':'driverBackup', 'scan':'scan', 'cleanup':'quarantine', 'restore':'restore', 'purge':'purge', 'startup':'startup', 'startup-disable':'disable', 'startup-restore':'restore', 'dns-flush':'dnsFlush', 'power-set':'power', 'power-profiles':'power', 'runtime.prepare':'w.download', 'runtime.install':'w.install', 'runtime.inventory':'w.runtimes', 'package.inspect':'w.inspect', 'package.apply':'w.apply', 'package.import':'w.import', 'focus.inventory':'w.pc', 'focus.start':'w.pc', 'focus.stop':'restore', 'restore-points':'w.pc', 'restore-point-create':'w.pc'}
        return self.t(keys.get(command, 'n.step')) + (f' ({command})' if command not in keys else '')

    def table(self, rows, columns, layout=None, check=False):
        tree = QTreeWidget()
        tree.setRootIsDecorated(False)
        tree.setColumnCount(len(columns))
        tree.setHeaderLabels([label for _, label in columns])
        tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        tree.setMinimumHeight(180)
        tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        for row in rows:
            item = QTreeWidgetItem(tree, [str(row.get(key, '')) for key, _ in columns])
            item.setData(0, Qt.UserRole, row)
            if check and row.get('eligible') is not False:
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, Qt.Unchecked)
            elif check:
                item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
        for index in range(len(columns)):
            tree.resizeColumnToContents(index)
        (layout or self.body).addWidget(tree)
        return tree

    def chosen(self, tree):
        return [tree.topLevelItem(i).data(0, Qt.UserRole) for i in range(tree.topLevelItemCount()) if tree.topLevelItem(i).checkState(0) == Qt.Checked and tree.topLevelItem(i).data(0, Qt.UserRole).get('eligible') is not False]

    def hero(self):
        box = QHBoxLayout()
        copy = QVBoxLayout()
        self.label(self.t('d.quickHelp'), layout=copy)
        self.label(self.t('n.steps'), layout=copy)
        box.addLayout(copy, 1)
        self.body.addLayout(box)

    def toggle_pause(self):
        self.aion.paused = not self.aion.paused
        self.aion_paused = self.aion.paused
        self.aion.update()
        personalize.sync(self)

    def page_home(self):
        has_next=self.settings.get('gamification',True) and not {'health','scan','drivers'}<=set(self.state.get('milestones',[]))
        self.button('scanFix', lambda: self.go('scanFix'), not has_next, name='home-scan')
        self.hero()
        from journey import render_return
        render_return(self)
        self.button('healthScan', lambda: self.run('health', callback=lambda r: self.store('health', r)), name='health-scan')
        self.button('cleanup', lambda: self.go('cleanup'))
        health = self.state.get('health')
        if health:
            rows = [{'name':self.t('system'), 'value':health.get('os', '')}, {'name':'CPU', 'value':health.get('cpu', '')}, {'name':'RAM', 'value':f'{health.get("ramFree", 0)/1024**3:.1f} / {health.get("ramTotal", 0)/1024**3:.1f} GB'}]
            for key, value in health.get('security', {}).items():
                rows.append(dict(name=key, value=self.t('unknown' if value is None else 'active' if value else 'inactive')))
            self.table(rows, [('name', self.t('n.step')), ('value', self.t('n.values'))])
        from care import render_home
        render_home(self)
        self.label(self.t('n.local_data'))

    def scan_options(self):
        from PySide6.QtWidgets import QWidget
        toggle=QCheckBox(self.t('d.scanOptions'));toggle.setObjectName('scan-options-toggle')
        toggle.setChecked(self.state.get('scanOptionsExpanded',False))
        self.body.addWidget(toggle)
        panel=QWidget();options=QVBoxLayout(panel);options.setContentsMargins(0,0,0,0)
        self.body.addWidget(panel);panel.setVisible(toggle.isChecked())
        toggle.toggled.connect(lambda value:(self.state.update(scanOptionsExpanded=value),panel.setVisible(value)))
        online = QCheckBox(self.t('d.online'))
        online.setObjectName('scan-online')
        online.setChecked(self.scan_online)
        online.toggled.connect(lambda value: setattr(self, 'scan_online', value))
        options.addWidget(online)
        self.label(self.t('d.onlineHelp'), layout=options)

    def page_scanFix(self):
        report = self.state.get('report')
        has_updates=report and any(f['status']=='update' and any(a['kind']=='update' for a in f['actions']) for f in report.get('findings',[]))
        self.button('d.again' if report else 'd.scan', lambda:self.scan(), not has_updates, name='start-scan')
        if not report:
            self.hero()
            self.scan_options()
            self.label(self.t('d.empty'))
            return
        findings = report.get('findings', [])
        updates = [f for f in findings if f['status'] == 'update' and any(a['kind'] == 'update' for a in f['actions'])]
        issues = [f for f in findings if f['status'] in ('issue', 'unknown')]
        self.label(' · '.join(f'{self.t("d."+status)}: {sum(f["status"]==status for f in findings)}' for status in ('issue','update','optional','unknown','info')))
        layout = self.group('d.nextStep')
        self.label(self.t('d.nextUpdates').replace('{count}',str(len(updates))) if updates else self.t('d.nextIssues' if issues else 'd.nextClear'), layout=layout)
        if updates:
            if issues:self.label(self.t('d.nextIssues'),layout=layout)
            self.button(f'{self.t("updateAllDrivers")} ({len(updates)})', lambda: self.install_offers(updates, report), True, layout, literal=True, name='update-all')
            self.label(self.t('d.updateAllHelp'), layout=layout)
        if not report.get('online'):
            self.button('d.scanUpdates', lambda: self.scan(True), layout=layout)
        group=layout.parentWidget()
        self.body.removeWidget(group)
        next_row=QHBoxLayout()
        next_row.addWidget(group,1)
        self.body.addLayout(next_row)
        from care import render_scan
        render_scan(self)
        self.scan_options()
        self.button('exportReport', lambda: self.export('report.export'))
        filter_box = QComboBox()
        for key in ('all','issue','update','optional','unknown','info'):
            filter_box.addItem(self.t('d.'+key),key)
        filter_box.setCurrentIndex(max(0,filter_box.findData(self.filter_status)))
        filter_box.setAccessibleName(self.t('n.filter'))
        filter_box.currentIndexChanged.connect(lambda _: self.set_filter(filter_box.currentData()))
        self.body.addWidget(filter_box)
        for finding in sorted(findings,key=lambda f:('issue','unknown','update','optional','info').index(f['status'])):
            if self.filter_status != 'all' and finding['status'] != self.filter_status:
                continue
            if finding['status'] == 'info' and self.filter_status == 'all':
                continue
            self.finding(finding, report)
        if self.filter_status == 'all':
            self.label(self.t('n.other') + ': ' + str(sum(f['status']=='info' for f in findings)) + ' · ' + self.t('n.filter'))
        self.label(self.t('n.scope'))

    def set_filter(self, value):
        self.filter_status = value
        self.render()

    def scan(self, online=None):
        if online is not None and isinstance(online,bool):
            self.scan_online = online
        self.run('diagnostics.scan',dict(online=self.scan_online),lambda r:self.store('report',r))

    def finding(self, finding, report):
        title=f'{finding["evidence"].get("name",self.t("d."+finding["category"]))} · {self.t("d."+finding["status"])}'
        box = QGroupBox();box.setProperty('section',True);box.setAccessibleName(title)
        layout = QVBoxLayout(box)
        self.label(title,heading=True,level=2,layout=layout)
        self.label(self.t('d.'+finding['reason']),layout=layout)
        self.details('n.values',json.dumps(finding['evidence'],ensure_ascii=False,indent=2),layout)
        for action in finding.get('actions',[]):
            kind, key = action['kind'], action['id']
            if kind=='update':
                self.button('d.installOne',lambda _,f=finding:self.install_offers([f],report),layout=layout)
            elif kind=='repair':
                label={'audio-start':'d.audioStart','dns-flush':'d.dnsFlush','device-rescan':'d.rescan'}.get(key,'d.repair')
                self.button(label,lambda _,f=finding,a=action:self.confirm(self.t('d.confirm'),self.t('d.admin'),[f['evidence'].get('name',f['id'])],lambda:self.run('diagnostics.repair',dict(reportId=report['id'],findingId=f['id'],actionId=a['id'],confirm=True),lambda r:self.repair_result(r))),layout=layout)
            elif kind=='navigate':
                self.button('d.goSystemTools' if key=='system-tools' else 'd.goRuntimes' if key=='runtimes' else 'd.goDrivers',lambda _,k=key:self.go('tools' if k=='system-tools' else 'workshop' if k=='runtimes' else 'drivers'),layout=layout)
            else:
                self.button('d.guide',lambda _,k=key:self.external(k),layout=layout)
        self.body.addWidget(box)

    def repair_result(self, result):
        self.state['report']=result['report']
        self.notice.setText(self.t('d.fixed' if result['status']=='fixed' else 'd.still' if result['status']=='still-present' else 'd.unverified'))
        self.render()

    def install_offers(self, offers, report=None):
        ids=[f['id'][7:] if report else f['id'] for f in offers]
        names=[f['evidence'].get('name',f['id']) if report else f['name'] for f in offers]
        payload=dict(ids=ids,confirm=True)
        if report:
            payload['reportId']=report['id']
        def result(value):
            self.state['updateResult']=value
            self.state.pop('report' if report else 'updates',None)
            self.render()
            self.show_result(value)
        self.confirm(self.t('driverInstallConfirm'),self.t('d.installImpact'),names,lambda:self.run('diagnostics.updates' if report else 'windows-install',payload,result))

    def show_result(self,result):
        items=result.get('items',[])
        detail='\n'.join(f'{i.get("name",i.get("id",""))}: {self.t("n.complete" if i.get("success") else "n.failed")} ({i.get("code","")})' for i in items)
        if result.get('reboot'):
            detail+='\n'+self.t('reboot')
        if detail:
            QMessageBox.information(self,self.t('d.updateResults'),detail)

    def page_hardware(self):
        from hardware import render
        render(self)

    def page_drivers(self):
        from driver_center import render
        render(self)

    def ignore_updates(self,rows):
        from driver_center import ignore
        ignore(self,rows)

    def page_cleanup(self):
        self.label(self.t('cleanupIntro'))
        from journey import render_return
        render_return(self)
        self.button('scan',lambda:self.run('scan',callback=lambda r:self.store('cleanup',r)),True,name='cleanup-scan')
        plan=self.state.get('cleanup')
        if not plan:
            return
        self.label(f'{plan.get("count",0)} {self.t("files")} · {plan.get("bytes",0)} bytes')
        self.table(plan.get('samples',[]),[('name',self.t('files')),('bytes','bytes')])
        self.details('n.values',json.dumps(plan,ensure_ascii=False,indent=2))
        groups=[]
        for key in ('temp','chrome','edge'):
            check=QCheckBox(self.t(key))
            check.setChecked(True)
            self.body.addWidget(check)
            groups.append((key,check))
        self.button('quarantine',lambda:self.confirm(self.t('confirm'),self.t('recoverText'),[k for k,c in groups if c.isChecked()],lambda:self.run('cleanup',dict(planId=plan.get('planId',plan.get('id')),groups=[k for k,c in groups if c.isChecked()]),lambda _:self.store('cleanup',None))),True,name='cleanup-apply')

    def page_startup(self):
        self.label(self.t('startupIntro'))
        self.button('refresh',lambda:self.run('startup',callback=lambda r:self.store('startup',r)),True)
        if 'startup' not in self.state:self.label(self.t('layout.startupEmpty'))
        elif not self.state['startup']:self.label(self.t('layout.startupNone'))
        tree=self.table(self.state.get('startup',[]),[('name',self.t('d.name')),('command',self.t('n.values'))],check=True)
        tree.setObjectName('startup-tree')
        hint=self.label(self.t('layout.chooseStartup'));hint.setObjectName('startup-selection-hint')
        disable=self.button('disable',lambda:self.disable_startup(self.chosen(tree)),enabled=False,name='startup-disable')
        def selected():
            count=len(self.chosen(tree));disable.setEnabled(not self.busy and count==1)
            hint.setPlainText(self.t('layout.oneStartup' if count>1 else 'layout.reviewStartup' if count==1 else 'layout.chooseStartup'))
        tree.itemChanged.connect(lambda *_:selected())
        self.button('startupOpen',lambda:self.external('startup'))

    def disable_startup(self,rows):
        if rows:
            row=rows[0]
            self.confirm(self.t('confirm'),self.t('startupIntro'),[row['name']],lambda:self.run('startup-disable',dict(id=row['id']),lambda _:self.store('startup',[r for r in self.state.get('startup',[]) if r['id']!=row['id']])))

    def page_tools(self):
        from care import render_tools
        render_tools(self)
        self.button('network',lambda:self.run('network',callback=lambda r:self.store('network',r)))
        self.button('dnsFlush',lambda:self.confirm(self.t('d.confirm'),self.t('d.dnsImpact'),[self.t('dnsFlush')],lambda:self.run('dns-flush')))
        self.button('power',lambda:self.run('power-profiles',callback=lambda r:self.store('power',r)))
        if self.state.get('network'):
            self.details('n.values',json.dumps(self.state['network'],ensure_ascii=False,indent=2))
        for profile in self.state.get('power',[]):
            self.button(profile['name']+(' ✓' if profile.get('active') else ''),lambda _,p=profile:self.confirm(self.t('confirm'),self.t('power'),[p['name']],lambda:self.run('power-set',dict(id=p['id']))),literal=True)
        for key in ('security','windows','sound','display','network-settings'):
            self.button(self.t({'security':'securityOpen','windows':'windowsUpdate','sound':'d.sound','display':'d.displayAction','network-settings':'d.networkAction'}[key]),lambda _,k=key:self.external(k),literal=True)

    def page_history(self):
        self.button('refresh',lambda:self.run('history',callback=lambda r:self.store('history',r)),True)
        self.button('exportBackup',lambda:self.export('backup.export'))
        from care import render_history
        render_history(self)
        history=self.state.get('history',{})
        for item in history.get('cleanup',[]):
            layout=self.group('cleanup')
            self.label(f'{item.get("at","")} · {item.get("bytes",0)} bytes · {item.get("status","")}',layout=layout)
            if item.get('status') not in ('restored','purged'):
                self.button('restore',lambda _,i=item:self.run('restore',dict(id=i['id']),lambda _:self.refresh_history()),layout=layout,name='restore-'+item['id'])
                self.button('purge',lambda _,i=item:self.confirm(self.t('purgeConfirm'),self.t('purgeText'),[i['id']],lambda:self.run('purge',dict(id=i['id'],confirm=True),lambda _:self.refresh_history())),layout=layout)
        for item in history.get('events',[]):
            layout=self.group('history')
            self.label(f'{self.action_name(item["type"])} · {item.get("at","")}',layout=layout)
            self.details('n.values',json.dumps(item,ensure_ascii=False,indent=2),layout)
            if item['type']=='startup-disable' and item.get('status') in ('complete','pending'):
                self.button('restore',lambda _,i=item:self.run('startup-restore',dict(id=i['id']),lambda _:self.refresh_history()),layout=layout)
            if item['type']=='power-set' and item.get('previous'):
                self.button('restore',lambda _,i=item:self.run('power-set',dict(id=i['previous']),lambda _:self.refresh_history()),layout=layout)
        if not history.get('events') and not history.get('cleanup'):
            self.label(self.t('emptyHistory'))

    def refresh_history(self):
        self.run('history',callback=lambda r:self.store('history',r),silent=True)

    def page_workshop(self):
        from workshop import render
        render(self)

    def reload_library(self):
        self.run('workshop.library',callback=lambda r:self.store('library',r),silent=True)

    def import_package(self):
        directory=QFileDialog.getExistingDirectory(self,self.t('w.import'))
        if directory:
            self.run('package.import',dict(directory=directory),lambda r:self.store('package',r))

    def apply_package(self,plan,rows):
        if rows:
            self.confirm(self.t('confirm'),self.t('n.automatic_backup'),[r['name'] for r in rows],lambda:self.run('package.apply',dict(planId=plan['id'],ids=[r['id'] for r in rows],confirm=True),lambda r:self.show_result(r)))

    def prepare_runtime(self,plan):
        self.confirm(self.t('w.install'),f'{plan.get("publisher","")} · {plan.get("bytes",0)} bytes\nSHA-256: {plan.get("sha256","")}',[plan.get('kind','')],lambda:self.run('runtime.install',dict(planId=plan['id'],confirm=True,acceptLicense=True)),license=True)

    def system_open(self,key):
        self.run('system.open',dict(id=key),silent=True)

    def external(self,key):
        self.bridge.call('external',dict(id=key),lambda r:self.open_reply(r))

    def open_folder(self,key):
        self.bridge.call('folder.open',dict(id=key),self.open_reply)

    def open_reply(self,reply):
        if not reply.get('ok'):
            self.error(reply.get('error','OPERATION_FAILED'))
            return
        data=reply.get('data') or {}
        if data.get('url'):
            QDesktopServices.openUrl(QUrl(data['url']))
        if data.get('folder'):
            QDesktopServices.openUrl(QUrl.fromLocalFile(data['folder']))

    def export(self,command):
        file,_=QFileDialog.getSaveFileName(self,self.t('exportBackup'),f'WinOptimizer-{VERSION}.json','JSON (*.json)')
        if not file:return
        def received(reply):
            if not reply.get('ok'):self.error(reply.get('error','OPERATION_FAILED'));return
            try:Path(file).write_text(json.dumps(reply['data'],ensure_ascii=False,indent=2),encoding='utf-8');self.notice.setText(self.t('n.report_saved'))
            except OSError:self.error('OPERATION_FAILED')
        self.bridge.call(command,callback=received)

    def save_setting(self,key,value,rerender=False):
        self.settings={**self.settings,key:value}
        self.save_serial+=1
        serial=self.save_serial
        def saved(reply):
            if serial!=self.save_serial:return
            if not reply.get('ok'):self.error(reply.get('error','OPERATION_FAILED'));return
            self.settings=reply['data']
            self.notice.setText(self.t('n.save'))
            self.appearance()
            if rerender:self.render()
        self.bridge.call('settings.save',self.settings,saved)

    def choice(self,form,key,options,label=None):
        combo=QComboBox()
        combo.setObjectName('setting-'+key)
        for value,name in options:combo.addItem(name,value)
        combo.setCurrentIndex(max(0,combo.findData(self.settings.get(key))))
        combo.setAccessibleName(label or self.t(key))
        combo.currentIndexChanged.connect(lambda _:self.save_setting(key,combo.currentData(),key=='language'))
        form.addRow(label or self.t(key),combo)
        return combo

    def numeric(self,form,key,label,minimum,maximum,step,default):
        row=QWidget();layout=QVBoxLayout(row);top=QHBoxLayout()
        slider=QSlider(Qt.Horizontal);slider.setRange(minimum,maximum);slider.setSingleStep(step);slider.setPageStep(step)
        spin=QSpinBox();spin.setRange(minimum,maximum);spin.setSingleStep(step);spin.setSuffix('%' if key in ('scale','textSize','mascotSize') else '')
        spin.setObjectName('setting-'+key);spin.setAccessibleName(label);slider.setAccessibleName(label)
        value=int(self.settings.get(key,default));slider.setValue(value);spin.setValue(value)
        slider.valueChanged.connect(spin.setValue);spin.valueChanged.connect(slider.setValue)
        def commit(value):
            snapped=max(minimum,min(maximum,round(value/step)*step))
            with QSignalBlocker(slider),QSignalBlocker(spin):
                slider.setValue(snapped);spin.setValue(snapped)
            self.save_setting(key,snapped)
        slider.sliderReleased.connect(lambda:commit(slider.value()))
        slider.valueChanged.connect(lambda value:commit(value) if slider.hasFocus() and not slider.isSliderDown() else None)
        spin.editingFinished.connect(lambda:commit(spin.value()))
        reset=QPushButton(self.t('n.default'));reset.clicked.connect(lambda:(spin.setValue(default),self.save_setting(key,default)))
        layout.addWidget(slider);top.addWidget(spin,1);top.addWidget(reset);layout.addLayout(top)
        if key=='scale':
            presets=QGridLayout()
            for index,val in enumerate((80,100,125,150,175,200)):
                b=QPushButton(f'{val}%');b.clicked.connect(lambda _,v=val:(spin.setValue(v),self.save_setting(key,v)));presets.addWidget(b,index//3,index%3)
            layout.addLayout(presets)
        form.addRow(label,row)

    def page_settings(self):
        self.label(self.t('previewSettings'))
        sections=QComboBox()
        sections.setObjectName('settings-section')
        sections.setAccessibleName(self.t('settings'))
        for key in ('general','appearance','accessibility','gameSettings','dataSettings','updates','about'):
            sections.addItem(self.t(key),key)
        sections.setCurrentIndex(max(0,sections.findData(self.settings_section)))
        sections.currentIndexChanged.connect(lambda _:self.set_settings_section(sections.currentData()))
        self.body.addWidget(sections)
        self.label(self.t(self.settings_section),heading=True,level=2)
        form=QFormLayout();form.setRowWrapPolicy(QFormLayout.WrapAllRows if self.width()<900 else QFormLayout.WrapLongRows);self.body.addLayout(form)
        section=self.settings_section
        if section=='general':
            self.choice(form,'language',[('tr','Türkçe'),('en','English')],self.t('n.language'))
            self.label(self.t('n.local_data'))
        elif section=='appearance':
            personalize.font_controls(self,form)
            self.choice(form,'theme',[(k,self.t('systemTheme' if k=='system' else k)) for k in ('light','dark','system','contrast')])
            personalize.note(self,form,'look.contrastHelp')
            personalize.accent_controls(self,form)
            self.numeric(form,'scale',self.t('scale'),80,200,5,100)
            self.choice(form,'density',[(k,self.t(k)) for k in ('comfortable','compact')])
            self.button('accessibility',lambda:self.set_settings_section('accessibility'))
            self.button('gameSettings',lambda:self.set_settings_section('gameSettings'))
        elif section=='accessibility':
            self.numeric(form,'textSize',self.t('textSize'),80,160,5,100)
            personalize.font_controls(self,form)
            for key,minv,maxv,step in [('lineHeight',1.2,2,.1),('letterSpacing',0,3,.1)]:
                spin=QDoubleSpinBox();spin.setRange(minv,maxv);spin.setSingleStep(step);spin.setValue(self.settings.get(key,minv));spin.setAccessibleName(self.t(key));spin.editingFinished.connect(lambda k=key,s=spin:self.save_setting(k,s.value(),k=='lineHeight'));form.addRow(self.t(key),spin)
        elif section=='gameSettings':
            for key in ('motion','sound','gamification','companion','followPointer','petting'):
                check=QCheckBox(self.t(key));check.setObjectName('setting-'+key);check.setChecked(self.settings.get(key,True));check.toggled.connect(lambda v,k=key:self.save_setting(k,v));form.addRow(check)
            self.numeric(form,'mascotSize',self.t('mascotSize'),75,150,5,100)
        elif section=='dataSettings':
            self.button('exportBackup',lambda:self.export('backup.export'))
            self.button('importBackup',self.import_backup)
            self.button('openData',lambda:self.open_folder('data'))
            self.label(self.t('backupHelp'))
        elif section=='about':
            self.label(self.t('n.current')+': '+VERSION)
            self.label(self.t('n.engine'))
            self.label(self.t('aboutText'))
            self.label(self.t('care.donor'))
            self.button('care.donorSource',lambda:self.external('sysmender'))
            self.button('source',lambda:self.external('github'))
        elif section=='updates':
            self.label(self.t('n.current')+': '+VERSION)
            self.choice(form,'channel',[(k,self.t(k)) for k in ('stable','beta')])
            if self.portable:self.label(self.t('portableHelp'))
            self.button('checkUpdates',lambda:self.run('updates.check',callback=lambda r:self.store('appUpdate',r)),True,name='check-app-update')
            update=self.state.get('appUpdate')
            if update:
                if update.get('available'):
                    self.label(self.t('updateAvailable')+': '+update['version'])
                    self.label(update.get('notes',{}).get(self.settings['language'],''))
                    if self.portable:self.button('portableDownload',lambda:self.bridge.call('updates.portable',callback=self.open_reply))
                    else:self.button('installUpdate',lambda:self.confirm(self.t('updateConfirm'),self.t('updateConfirmText'),[update['version']],lambda:self.run('updates.install',dict(confirm=True),self.install_app)),True,name='install-app-update')
                else:self.label(self.t('upToDate'))
            self.button('releasePage',lambda:self.external('releases'))

    def set_settings_section(self,section):
        self.settings_section=section
        self.render()

    def install_app(self,result):
        installer=result.get('installer')
        if installer:
            # A new executable at the same path must not reuse the old onefile payload.
            env={**os.environ,'PYINSTALLER_RESET_ENVIRONMENT':'1'}
            try:subprocess.Popen([installer,'/S','--updated','--force-run'],close_fds=True,env=env)
            except OSError:
                self.last_error='OPERATION_FAILED';self.error(self.last_error);return
            QTimer.singleShot(500,self.close)

    def import_backup(self):
        file,_=QFileDialog.getOpenFileName(self,self.t('importBackup'),'','JSON (*.json)')
        if file:
            try:
                if Path(file).stat().st_size>5*1024*1024:raise ValueError()
                data=json.loads(Path(file).read_text(encoding='utf-8-sig'))
            except (OSError,ValueError):self.error('BACKUP_INVALID');return
            self.run('backup.import',data,lambda r:(setattr(self,'settings',r),self.appearance(),self.render()))

    def resizeEvent(self,event):
        super().resizeEvent(event)
        usability.adapt(self)
        if self.ready and getattr(self,'aion',None):self.companion_header.adapt()
        if self.ready and not self.details_expanded:
            QTimer.singleShot(0,lambda:self.set_operation_details(self.settings.get('operationDetails',True)))

    def closeEvent(self,event):
        if self.busy:
            self.notice.setText(self.t('n.close_busy'))
            event.ignore()
            return
        if hasattr(self, 'poller'):
            self.poller.stop()
        self.bridge.close()
        event.accept()

def paths():
    executable=Path(sys.executable if getattr(sys,'frozen',False) else __file__)
    portable=executable.name.lower().endswith('-portable.exe') or '--portable' in sys.argv
    if '--data' in sys.argv and not getattr(sys,'frozen',False):
        return portable,Path(sys.argv[sys.argv.index('--data')+1]).resolve()
    local=Path(os.environ.get('LOCALAPPDATA',Path.home()/'.local/share'))
    return portable,(executable.parent/'Data'/'WinOptimizer Aion' if portable else local/'WinOptimizer Aion')

def main():
    os.environ.setdefault('QT_OPENGL','software')
    if sys.platform=='win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('dev.kaansavukduran.winoptimizer')
    app=QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(ROOT/'public/assets/aion.ico')))
    app.setApplicationName('WinOptimizer Aion')
    portable,data=paths()
    try:
        data.mkdir(parents=True,exist_ok=True)
        probe=data/'.write-test';probe.write_text('');probe.unlink()
    except OSError:
        QMessageBox.critical(None,'WinOptimizer Aion',NATIVE['tr']['read_only']+'\n'+NATIVE['en']['read_only']);return 1
    lock=QLockFile(str(data/'native-instance.lock'))
    if not lock.tryLock(0):
        QMessageBox.information(None,'WinOptimizer Aion','Uygulama zaten açık / The app is already open.');return 0
    node=ROOT/'vendor/node.exe' if getattr(sys,'frozen',False) else None
    bridge=Bridge(ROOT,data,portable,QLocale.system().name(),node)
    window=Window(bridge,data,portable)
    window.show()
    if '--smoke' in sys.argv:
        from smoke import start
        start(window,sys.argv[sys.argv.index('--smoke')+1])
    return app.exec()

if __name__=='__main__':
    raise SystemExit(main())
