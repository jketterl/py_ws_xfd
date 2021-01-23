#!/usr/bin/python3
# -*- coding: utf-8 -*-
import threading
import time
import logging
import signal

import control
import jenkins

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)


class SignalException(Exception):
    pass


def handle_signal(sig, frame):
    raise SignalException("Caught signal {0}".format(sig))


if __name__ == '__main__':

    for sig in [signal.SIGINT, signal.SIGTERM]:
        signal.signal(sig, handle_signal)

    # initialize component lists
    serverList = jenkins.ServerList("servers.json")
    outputList = jenkins.OutputList("outputs.json")
    jenkins.JobList("jobs.json", serverList, outputList)

    try:
        while threading.active_count() > 1:
            time.sleep(20)

    except SignalException:
        logging.info("shutting down")
        control.ControlServer.getInstance().shutdown()
        for output in outputList.all():
            output.shutdown()
        for server in serverList.all():
            server.ws.stop()
