import pimp
import os
from PyQt4 import QtGui

__PLUGIN_NAME__ = "InterceptPopup"
__AUTHOR__ = "hugsy"

class InterceptWindow(QtGui.QWidget):

    def __init__(self, rid, uri, data):
        super(InterceptWindow, self).__init__()
        self.rid = rid
        self.uri = uri
        self.title = "Intercepting request %d" % rid
        self.data = data
        self.setWindowProperty()
        self.setWindowLayout()
        self.setConnections()
        self.show()
        return

    def setWindowProperty(self):
        self.setGeometry(1500, 500, 500, 248)
        self.setWindowTitle(self.title)
        return

    def setWindowLayout(self):
        self.bounceButton    = QtGui.QPushButton("Bounce")
        self.saveTxtButton   = QtGui.QPushButton("Save As Text")
        self.savePyButton    = QtGui.QPushButton("Save As Python")
        self.cancelButton    = QtGui.QPushButton("Cancel")
        self.editField = QtGui.QTextEdit()
        self.editField.insertPlainText(self.data)
        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.savePyButton)
        hbox.addWidget(self.saveTxtButton)
        hbox.addWidget(self.cancelButton)
        hbox.addWidget(self.bounceButton)
        vbox = QtGui.QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(self.editField)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        return

    def setConnections(self):
        self.bounceButton.clicked.connect(self.updateText)
        self.cancelButton.clicked.connect(QtGui.QApplication.quit)
        self.saveTxtButton.clicked.connect(self.writeTxtFile)
        self.savePyButton.clicked.connect(self.writePyFile)
        return

    def writeTxtFile(self):
        filename = QtGui.QFileDialog().getOpenFileName(self,"Save As",os.getenv("HOME"))
        if len(filename) == 0:
            return
        with open(filename, "w") as f:
            f.write(self.data)
        return

    def writePyFile(self):
        filename = QtGui.QFileDialog().getOpenFileName(self, "Save As",os.getenv("HOME"))
        if len(filename) == 0: return
        with open(filename, "w") as f:
            f.write("""#!/usr/bin/env python2
#
# Replay script for {0:s}
#

import socket, ssl

HOST = ''
PORT = ''

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
if "{3:s}".startswith("https://"):
    s = ssl.wrap_socket(s,server_hostname="%s" % HOST)

s.connect((HOST, PORT))
s.sendall('''{2:s}''')
data = s.recv(1024)
print (data)
s.close()

#
# Automatically generated by {1:s}
#
""".format(self.title, __PLUGIN_NAME__, self.data, self.uri))
        return

    def updateText(self):
        self.data = self.editField.toPlainText()
        QtGui.QApplication.quit()
        return

def intercept(rid, text, uri):
    app = QtGui.QApplication([""])
    win = InterceptWindow(rid, uri, text)
    app.exec_()
    return str(win.data)

def proxenet_request_hook(request_id, request, uri):
    data = intercept(request_id, request.replace(pimp.CRLF, "\x0a"), uri)
    data = data.replace("\x0a", pimp.CRLF)
    return data

def proxenet_response_hook(response_id, response, uri):
    return response


if __name__ == "__main__":
    uri = "foo"
    req = "GET / HTTP/1.1\r\nHost: foo\r\nX-Header: Powered by proxenet\r\n\r\n"
    rid = 10

    print ("BEFORE:\n%s" % req)
    print ("AFTER:\n%s" % proxenet_request_hook(rid, req, uri))
