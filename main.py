#!/usr/bin/python3
# -*- coding: utf-8 -*-
import threading
import time
import logging
import control

import jenkins

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.DEBUG)

if __name__ == '__main__':

    # initialize component lists
    serverList = jenkins.ServerList("servers.json")
    outputList = jenkins.OutputList("outputs.json")
    jenkins.JobList("jobs.json", serverList, outputList)

    try:
        while threading.active_count() > 1:
            time.sleep(20)

    except (KeyboardInterrupt, SystemExit):
        logging.info("shutting down")
        control.ControlServer.getInstance().shutdown()
        for output in outputList.all():
            output.shutdown()
        for server in serverList.all():
            server.ws.stop()
