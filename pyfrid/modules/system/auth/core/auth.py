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

import abc
from types import StringType, ListType, FunctionType
from pyfrid.core.sysmod import BaseSystemModule
from pyfrid.core.signal import Signal
from pyfrid.core.descriptor import use_module

class AccessError(Exception): pass

class User(object):
    
    def __init__(self, login, password, groups=[], name="", organization="", email="", extra={}):
        if not groups: groups=[]
        self._login=login
        self._password=password
        self._name=name
        self._email=email
        self._organization=organization
        self._groups=groups
        self._extra=extra
                
    @property
    def groups(self):
        return self._groups[:]

    @property
    def login(self):
        return self._login

    @property
    def password(self):
        return self._password
    
    @property    
    def extra(self):
        return self._extra.copy()
    
    @property    
    def email(self):
        return self._email
    
    @property    
    def name(self):
        return self._name
    
    @property    
    def organization(self):
        return self._organization
    
    def __eq__(self,user):
        if user!=None and self.login==user.login:
            return True
        return False 

       
class BaseAuthModule(BaseSystemModule):
    """
    This is base class of authentication module. This module has functions for login and logout of a user, validating access of a user to
    objects presented in application. It also contains abstract methods for user creation and deleting.
    By default the authentication module has several useful signals:
    
       *  before_login_signal  
       *  after_login_signal   
       *  before_logout_signal  
       *  after_logout_signal

    """
    
    #: user groups and their weights. Groups with smaller are more powerful.
    groups={
                "ROOT"   :0,
                "ADVUSER":10,
                "USER"   :20,
                "GUEST"  :30
           }
    
    def __init__(self,*args,**kwargs):
        super(BaseAuthModule,self).__init__(*args,**kwargs)
        self._user_stack=list()
        self.before_login_signal=Signal(self)
        self.after_login_signal=Signal(self)
        self.before_logout_signal=Signal(self)
        self.after_logout_signal=Signal(self)
        
        self.after_login_signal.connect(self.logger_module.set_current_user)
        self.after_logout_signal.connect(self.logger_module.set_current_user)
    
    @property
    def current_user(self):
        """Returns a *user* object from top of the stack (i.e. current user) or None if there is no user logged in.""" 
        if self._user_stack:
            return self._user_stack[-1]
        return None
    
    @property
    def current_login(self):
        """Returns login of a currently logged in user or empty string"""
        if self._user_stack:
            return self._user_stack[-1].login
        return ''
            
    def login(self, login, password):
        """
        This function first validates login and password and creates *User* object, which corresponds to them.
        If validation was successful and there is no current user in application, this user become the current one.
        If there is another user currently signed in and his group weight is smaller (he has more rights), login fails.
        If the current user has less rights then one which is trying to login, then new user is added to the top of the
        stack and become the current user. This function return true or False depending on the result of the login process.""" 
        user=self.validate_user(login,password)
        if user==None: return False
        if self.current_user==user: return True
        self.before_login_signal(self.current_user)
        if self.current_user!=None: 
            curr_role=min([self.groups[val] for val in self.current_user.groups])
            user_role=min([self.groups[val] for val in user.groups])
            if user_role>=curr_role: return False
        self._user_stack.append(user)
        self.after_login_signal(self.current_user)
        return True
    
    def logout(self,login,password):
        """Performs a logout of a current user from application after validation of *login* and *password*."""
        if self.current_user==None: return True
        user=self.validate_user(login, password)
        if user == None: return False
        self.before_logout_signal(self.current_user)
        self._user_stack.pop()
        self.after_logout_signal(self.current_user)
        return True
    
    def validate_access(self, getter, permission="", exc=False):
        """This function checks whether a current user has access to an object. The argument *getter* can be an object
        which has method *get_permission_groups* or a function which accepts *permission* as an argument and returns a list
        of user groups corresponding to *permission*."""
        if self.current_user==None: return False    
        if type(permission)==StringType:
            groups=[]
            if type(getter)==FunctionType:
                groups=getter(permission)
            else:
                groups=getter.get_permission_groups(permission)
            if not groups: return True
            if any([gr in self.current_user.groups for gr in groups]):
                return True
            return False
        elif type(permission)==ListType:
            return all([self.validate_access(getter, p) for p in permission])
        else:
            raise TypeError("Wrong permission type. It must be a list of strings or a string")
        return False
    
    @abc.abstractmethod
    def validate_user(self, login, password):
        """Abstract method which checks *login* and *password* and returns a User object which corresponds to them."""
        return None
    
    def status(self):
        """Status handler with some information about a current user."""
        return (("User",self.current_user.login,""),
                ("Name",self.current_user.name,""),
                ("Organization",self.current_user.organization,""),
                ("Email",self.current_user.email,""),)
    
    @abc.abstractmethod
    def add_user(self, login, password, groups, name, email, organization):
        """
        Abstract method which adds user. The information about users is kept
        in a different way depending on the type of authentication module.
        """
        pass
    
    @abc.abstractmethod
    def del_user(self, login):
        """
        Abstract method which deletes user.
        """
        pass
    
    @abc.abstractmethod
    def user_exists(self, login):
        """Returns True if user with login *login* exists or False."""
        pass
    
    @abc.abstractproperty
    def noauth(self):
        """Returns True if authentication module doesn't perform any login or logout."""
        return False
    
    