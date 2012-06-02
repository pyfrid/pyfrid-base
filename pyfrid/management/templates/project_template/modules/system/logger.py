

from pyfrid.modules.system import BaseLoggerModule

class LoggerModule(BaseLoggerModule):
    alias="logger"
        
    def status(self):
        return super(LoggerModule, self).status()