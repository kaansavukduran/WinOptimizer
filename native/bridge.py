import json
from pathlib import Path
from PySide6.QtCore import QObject, QProcess, Signal, QProcessEnvironment

class Bridge(QObject):
    failed = Signal(str)
    def __init__(self, root, data, portable, locale, node=None):
        super().__init__()
        self.pending, self.sequence, self.buffer = {}, 0, b''
        self.unavailable, self.closing, self.has_started = False, False, False
        self.failure_code = 'BACKEND_UNAVAILABLE'
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.SeparateChannels)
        env = QProcessEnvironment.systemEnvironment()
        env.remove('ELECTRON_RUN_AS_NODE')
        self.process.setProcessEnvironment(env)
        self.process.readyReadStandardOutput.connect(self.read)
        self.process.started.connect(self.started)
        self.process.errorOccurred.connect(self.process_error)
        self.process.finished.connect(self.stopped)
        args = [str(Path(root) / 'desktop/native-bridge.cjs'), '--data', str(data), '--locale', locale]
        if portable:
            args.append('--portable')
        self.process.start(str(node or 'node'), args)

    def call(self, command, payload=None, callback=None):
        if self.unavailable or self.closing:
            if callback:
                callback(dict(ok=False, error=self.failure_code))
            return
        self.sequence += 1
        self.pending[self.sequence] = callback
        request = json.dumps(dict(id=self.sequence, command=command, payload=payload or {}), ensure_ascii=False)
        if self.process.write((request + '\n').encode('utf-8')) < 0:
            self.fail('BACKEND_DISCONNECTED' if self.has_started else 'BACKEND_UNAVAILABLE')

    def started(self):
        self.has_started = True

    def process_error(self, error):
        if error in (QProcess.FailedToStart, QProcess.Crashed, QProcess.ReadError, QProcess.WriteError):
            self.fail('BACKEND_DISCONNECTED' if self.has_started else 'BACKEND_UNAVAILABLE')

    def fail(self, code):
        if self.unavailable:
            return
        self.unavailable, self.failure_code = True, code
        callbacks, self.pending = self.pending, {}
        for callback in callbacks.values():
            if callback:
                callback(dict(ok=False, error=code))
        if not self.closing:
            self.failed.emit(code)

    def read(self):
        self.buffer += bytes(self.process.readAllStandardOutput())
        while b'\n' in self.buffer:
            line, self.buffer = self.buffer.split(b'\n', 1)
            if self.unavailable:
                continue
            try:
                reply = json.loads(line)
                if not isinstance(reply, dict) or type(reply.get('id')) is not int or type(reply.get('ok')) is not bool or reply['id'] not in self.pending:
                    raise ValueError('Invalid response envelope')
                if not reply['ok'] and (not isinstance(reply.get('error'), str) or not reply['error']):
                    raise ValueError('Invalid error code')
            except (ValueError, UnicodeError):
                self.fail('BACKEND_PROTOCOL_FAILED')
                continue
            # UI exceptions must not be reported as corrupt backend messages.
            callback = self.pending.pop(reply['id'])
            if callback:
                callback(reply)

    def stopped(self, *_):
        self.fail('BACKEND_DISCONNECTED' if self.has_started else 'BACKEND_UNAVAILABLE')

    def close(self):
        self.closing = True
        self.process.closeWriteChannel()
        if self.process.state() != QProcess.NotRunning and not self.process.waitForFinished(3000):
            self.process.kill()
            self.process.waitForFinished(1000)
        self.fail('BACKEND_DISCONNECTED' if self.has_started else 'BACKEND_UNAVAILABLE')
