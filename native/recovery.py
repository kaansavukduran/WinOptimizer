"""Local error guidance. Only explicitly listed read operations can be retried."""
import re
from PySide6.QtWidgets import QApplication, QGroupBox, QVBoxLayout

BACKEND_ERRORS = frozenset(('BACKEND_UNAVAILABLE', 'BACKEND_DISCONNECTED', 'BACKEND_PROTOCOL_FAILED'))
READ_OPERATIONS = frozenset(('health', 'diagnostics.scan', 'hardware', 'drivers',
    'windows-updates', 'scan', 'startup', 'network', 'power-profiles', 'focus.inventory',
    'offline.inventory', 'ghosts', 'restore-points', 'runtime.inventory',
    'workshop.library', 'updates.check', 'history', 'care.snapshot', 'package.inspect'))

WORDS = {
 'tr': dict(title='Ne oldu, şimdi ne yapmalıyım?', cancelled='Tarama iptal edildi. Önceki sonuçların bu pencerede duruyor. Hazır olduğunda taramayı yeniden başlatabilirsin.',
    read='Bu kontrol tamamlanamadı. Önceki sonuçların bu pencerede duruyor. Yeniden dene yalnız bu kontrolü baştan çalıştırır.',
    review='İşlemin sonucunu işlem ayrıntılarından kontrol et. İlgili ekrana dönüp güncel sonuçları incele; gerekiyorsa işlemi yeniden seç ve onayla.',
    stale='Tarama veya seçim artık geçerli değil. İlgili ekrana dönüp yeniden tara; ardından güncel sonuçlardan seçim yap.',
    admin='Windows yönetici izni verilmedi. İlgili ekrana dönüp işlemi tekrar seçebilirsin; Windows izin isteğini onaylaman gerekir.',
    backend='İşlem motoruyla bağlantı yok. Yeni işlem başlatılamıyor. Bu penceredeki raporları inceleyebilir, ardından uygulamayı kapatıp yeniden açabilirsin.',
    uncertain='Başlatılan işlemin tamamlanıp tamamlanmadığı doğrulanamadı. Windows işlemi devam ediyor olabilir. Yeniden uygulamadan önce işlem ayrıntılarını ve Windows durumunu kontrol et.',
    retry='Bu kontrolü yeniden dene', origin='İlgili ekrana dön', details='İşlem ayrıntılarını aç', copy='Hata bilgisini kopyala', dismiss='Bildirimi kapat', copied='Hata bilgisi panoya kopyalandı. Dosya yolları ve rapor içeriği eklenmedi.', action='İlgili ekran', code='Hata kodu', close='Uygulamayı kapat'),
 'en': dict(title='What happened, and what can I do?', cancelled='The scan was cancelled. Previous results remain in this window. You can start the scan again when ready.',
    read='This check could not finish. Previous results remain in this window. Try again restarts only this check.',
    review='Check the operation details for its outcome. Return to the relevant screen and review current results; select and confirm the operation again if needed.',
    stale='The scan or selection is no longer valid. Return to the relevant screen and scan again, then choose from the current results.',
    admin='Windows administrator permission was not granted. Return to the relevant screen and select the operation again; you will need to approve the Windows permission request.',
    backend='The operation engine is disconnected. New operations cannot start. You can review reports in this window, then close and reopen the app.',
    uncertain='The operation outcome could not be verified. A Windows operation may still be running. Check operation details and Windows status before applying it again.',
    retry='Try this check again', origin='Return to the relevant screen', details='Open operation details', copy='Copy error information', dismiss='Dismiss notice', copied='Error information copied. File paths and report contents were excluded.', action='Relevant screen', code='Error code', close='Close the app')
}

def guidance(failure, language, disconnected=False):
    words = WORDS[language]
    request, code = failure.get('request'), failure['code']
    read_only = request is not None and request['command'] in READ_OPERATIONS
    if disconnected or code in BACKEND_ERRORS:
        message = words['backend']
        if request and not read_only:
            message += '\n' + words['uncertain']
    elif code == 'SCAN_CANCELLED':
        message = words['cancelled']
    elif code in ('SCAN_EXPIRED', 'INVALID_SELECTION'):
        message = words['stale']
    elif code == 'ADMIN_CANCELLED':
        message = words['admin']
    else:
        message = words['read' if read_only else 'review']
    return message, read_only and not disconnected and code not in BACKEND_ERRORS

def render(window):
    failure = window.failure
    if not failure:
        return
    words = WORDS[window.settings['language']]
    message, retry = guidance(failure, window.settings['language'], window.backend_lost)
    panel = QGroupBox()
    panel.setObjectName('operation-recovery')
    layout = QVBoxLayout(panel)
    window.label(words['title'], heading=True, layout=layout)
    request = failure.get('request')
    page = request['page'] if request else window.page
    location = window.t(page)
    if request:
        action = window.action_name(request['command'])
        if action != location:
            location += ' · ' + action
    window.label(words['action'] + ': ' + location, layout=layout)
    window.label(message, layout=layout)
    # Only application error codes enter copied diagnostics, never exception paths/payloads.
    code = failure['code'] if re.fullmatch(r'[A-Z][A-Z0-9_]{0,80}', failure['code']) else 'OPERATION_FAILED'
    window.label(words['code'] + ': ' + code, layout=layout)

    def origin():
        if window.busy:
            return
        window.page = page
        if request:
            window.settings_section = request['settings_section']
            window.driver_section = request.get('driver_section',window.driver_section)
            window.workshop_section = request.get('workshop_section',window.workshop_section)
        window.failure = None
        window.render()  # go(history/workshop) would start a request merely by navigating.

    def again():
        if window.busy or window.backend_lost:
            return
        origin()
        window.run(request['command'], request['payload'], request['callback'], request['silent'])

    def details():
        window.set_operation_details(True, persist=not window.backend_lost)

    def copy():
        from app import VERSION
        QApplication.clipboard().setText(f'WinOptimizer Aion {VERSION}\n{words["action"]}: {location}\n{words["code"]}: {code}\n{message}')
        window.notice.setText(words['copied'])

    if retry:
        window.button(words['retry'], again, True, layout, literal=True, name='recovery-retry')
    if window.ready:
        window.button(words['origin'], origin, layout=layout, literal=True, name='recovery-origin')
    window.button(words['details'], details, layout=layout, literal=True, name='recovery-details')
    window.button(words['copy'], copy, layout=layout, literal=True, name='recovery-copy')
    if window.ready:
        def dismiss():
            window.failure = None
            window.render()
        window.button(words['dismiss'], dismiss, layout=layout, literal=True, name='recovery-dismiss')
    else:
        window.button(words['close'], window.close, layout=layout, literal=True, name='recovery-close')
    window.body.addWidget(panel)
