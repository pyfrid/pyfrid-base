

from pyfrid.modules.system.app import BaseApplicationModule

class ApplicationModule(BaseApplicationModule):
    alias="application"
        
    def status(self):
        return super(ApplicationModule, self).status()   