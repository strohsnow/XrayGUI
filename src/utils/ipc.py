import json

from PySide6.QtNetwork import QLocalServer, QLocalSocket


def pass_to_main(argv: list[str], socket_name: str) -> bool:
    socket = QLocalSocket()
    socket.connectToServer(socket_name)
    if socket.waitForConnected(50):
        payload = json.dumps(argv[1:]).encode("utf-8")
        socket.write(payload)
        socket.flush()
        socket.waitForBytesWritten(50)
        return True
    return False


def start_server(socket_name: str) -> QLocalServer:
    server = QLocalServer()
    if not server.listen(socket_name):
        QLocalServer.removeServer(socket_name)
        server.listen(socket_name)
    return server
