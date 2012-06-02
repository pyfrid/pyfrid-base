#  Copyright 2012 Denis Korolkov
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from pyfrid.modules.system.vm.leplvm import BaseLeplVMModule

from pyfrid.modules.system.vm.leplvm import ARGSEPARATOR, SPLITTER, COMMA, COMMENT
from pyfrid.modules.system.vm.leplvm import LSBR, RSBR, LBR, RBR, EQOP, IDENT        
from pyfrid.modules.system.vm.leplvm import FLOATCONST, INTCONST, BOOLCONST, STRCONST 
from pyfrid.modules.system.vm.leplvm import BOOLCONSTLIST, STRCONSTLIST, INTCONSTLIST, FLOATCONSTLIST
from pyfrid.modules.system.vm.leplvm import CONSTVALUE, CONSTVALUELIST, CONSTVALUEDICT 
from pyfrid.modules.system.vm.leplvm import OBJECT, COMMAND, DEVICE, MODULE, SYSMOD