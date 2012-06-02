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
#
from pyfrid.management.core.registry import CommandRegistry, RegistryError
from pyfrid.management.core.command import BaseCommand

project_registry=CommandRegistry()

class ProjectCommandMeta(type):
    
    def __init__(cls, name, bases, d):
        try:
            project_registry.register(cls)
        except RegistryError, err:
            raise RegistryError("Exception while registering class '{0}': {1}".format(cls.__class__.__name__,err))
        return type.__init__(cls, name, bases, d)
    
class BaseProjectCommand(BaseCommand):
    __metaclass__=ProjectCommandMeta