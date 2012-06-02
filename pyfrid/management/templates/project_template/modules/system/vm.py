

from pyfrid.modules.system.vm import BaseLeplVMModule

class LeplVMModule(BaseLeplVMModule):
    alias="virtual_machine"
        
    def status(self):
        return super(LeplVMModule, self).status()