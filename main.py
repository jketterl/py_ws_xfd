# -*- coding: utf-8 -*-
from ws4py.client.threadedclient import WebSocketClient

class JenkinsClient(WebSocketClient):
    def opened(self):
	print "Connection opened"

    def closed(self, code, reason):
        print "Closed down", code, reason

    def received_message(self, m):
        print "=> %d %s" % (len(m), str(m))

if __name__ == '__main__':
    try:
        ws = JenkinsClient('ws://dev-build.pocci.cxo.name:8000/jenkins', protocols=['http-only', 'chat'])
        ws.daemon = False
        ws.connect()
    except KeyboardInterrupt:
        ws.close()
