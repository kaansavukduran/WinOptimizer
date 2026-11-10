import json
from pathlib import Path
from PySide6.QtCore import QObject, QProcess, Signal, QProcessEnvironment

class Bridge(QObject):
    failed = Signal(str)
    def __init__(self, root, data, portable, locale, node=None):
        super().__init__()
        self.pending, self.sequence, self.buffer = {}, 0, b''
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.SeparateChannels)
        env = QProcessEnvironment.systemEnvironment()
        env.remove('ELECTRON_RUN_AS_NODE')
        self.process.setProcessEnvironment(env)
        self.process.readyReadStandardOutput.connect(self.read)
        self.process.errorOccurred.connect(lambda _: self.failed.emit('BACKEND_UNAVAILABLE'))
        self.process.finished.connect(self.stopped)
        args = [str(Path(root) / 'desktop/native-bridge.cjs'), '--data', str(data), '--locale', locale]
        if portable:
            args.append('--portable')
        self.process.start(str(node or 'node'), args)

    def call(self, command, payload=None, callback=None):
        self.sequence += 1
        self.pending[self.sequence] = callback
        request = json.dumps(dict(id=self.sequence, command=command, payload=payload or {}), ensure_ascii=False)
        self.process.write((request + '\n').encode('utf-8'))

    def read(self):
        self.buffer += bytes(self.process.readAllStandardOutput())
        while b'\n' in self.buffer:
            line, self.buffer = self.buffer.split(b'\n', 1)
            try:
                reply = json.loads(line)
                callback = self.pending.pop(reply['id'], None)
                if callback:
                    callback(reply)
            except (ValueError, KeyError):
                self.failed.emit('BACKEND_PROTOCOL_FAILED')

    def stopped(self, *_):
        callbacks, self.pending = self.pending, {}
        for callback in callbacks.values():
            if callback:
                callback(dict(ok=False, error='BACKEND_UNAVAILABLE'))

    def close(self):
        self.process.closeWriteChannel()
        if not self.process.waitForFinished(3000):
            self.process.kill()
            self.process.waitForFinished(1000)
