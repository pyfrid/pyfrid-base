#    This file is part of PyFRID.
#
#    PyFRID is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    PyFRID is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyFRID.  If not, see <http://www.gnu.org/licenses/>.
#

from pyfrid.modules.system.vm.leplvm import BaseLeplVMModule

from pyfrid.modules.system.vm.leplvm import ARGSEPARATOR, SPLITTER, COMMA, COMMENT
from pyfrid.modules.system.vm.leplvm import LSBR, RSBR, LBR, RBR, EQOP, IDENT        
from pyfrid.modules.system.vm.leplvm import FLOATCONST, INTCONST, BOOLCONST, STRCONST 
from pyfrid.modules.system.vm.leplvm import BOOLCONSTLIST, STRCONSTLIST, INTCONSTLIST, FLOATCONSTLIST
from pyfrid.modules.system.vm.leplvm import CONSTVALUE, CONSTVALUELIST, CONSTVALUEDICT 
from pyfrid.modules.system.vm.leplvm import OBJECT, COMMAND, DEVICE, MODULE, SYSMOD