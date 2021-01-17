"""
Created on Nov 12, 2012

@author: jketterl
"""

from output import Output
import logging


class Console(Output):
    def setState(self, projectId, state):
        logging.info("setting state for project id {pid} to: {state}".format(pid=projectId, state=state))
