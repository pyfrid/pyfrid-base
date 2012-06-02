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

from pyfrid.modules.system.auth.core.auth import BaseAuthModule, User

class BaseNoAuthModule(BaseAuthModule):
    """
    This is authentication module which doesn't perform any login and logout and all access validations will return True.
    Use it if you don't need any authentication control in your application.
    """
    
    def validate_user(self,login,password):
        """Returns empty user."""
        return User("","")
    
    def validate_access(self,*args, **kwargs):
        """Always returns True"""
        return True
    
    def add_user(self, login, password, groups, name, email, organization):
        """Raises NotImplementedError."""
        raise NotImplementedError("No valid authentication module in the system")
    
    def del_user(self, login):
        """Raises NotImplementedError."""
        raise NotImplementedError("No valid authentication module in the system")
    
    def user_exists(self, login):
        """Raises NotImplementedError."""
        raise NotImplementedError("No valid authentication module in the system")
    
    def status(self):
        return None
    
    @property
    def noauth(self):
        """Returns True"""
        return True