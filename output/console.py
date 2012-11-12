'''
Created on Nov 12, 2012

@author: jketterl
'''

from output import Output
import logging

class Console(Output):
    def setState(self, state):
        logging.info("setting state: %s" % state)