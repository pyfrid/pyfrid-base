

from pyfrid.modules.system.auth import BaseNoAuthModule

class AuthModule(BaseNoAuthModule):
    alias="authentication"
        
    def status(self):
        return super(AuthModule, self).status()