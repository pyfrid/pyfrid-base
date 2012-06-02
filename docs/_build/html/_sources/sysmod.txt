
System modules
==============

System module is a building block of your application. The main difference between normal modules and system modules is a type of module's parent.
The parent of system module is an application related management command, like *cmdline* for command line application or *webapp* for web application.
These management commands are responsible for chosing a proper configuration manager, creation of devices, modules and commands of your application
and other low level tasks. Having a reference to the application management command, a system module has access to configuration, other system modules,
managers of devices, commands and modules of your application. All system modules: Logger, Application, Virtual Machine and Authentication, presented
currently in PyFRID are described in the following subsections.   

Base System Module
------------------

System Module class and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pyfrid.core.sysmod
   :members:
   :inherited-members:

   
Application Module
------------------

Application module systematize devices, commands and modules of your application, except system modules of course.
It also plays a role of a sandbox for them, giving a limited access to the functionality of other system modules like authentication,
logger and virtual machine. It also contains useful generators to iterate over objects and methods which can be used in other modules
and commands during the runtime of application. 


Application Module class and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pyfrid.modules.system.app
   :members:


Virtual Machine Module
----------------------

Base Virtual Machine Module class and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pyfrid.modules.system.vm.core.vm
   :members:

Lepl Virtual Machine Module class and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
.. automodule:: pyfrid.modules.system.vm.leplvm
   :members:


Authentication Module
---------------------

Base Authentication Module class and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pyfrid.modules.system.auth.core.auth
   :members:

NoAuthentication Module class and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pyfrid.modules.system.auth.noauth
   :members:

Yaml Authentication Module class and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pyfrid.modules.system.auth.yamlauth
   :members:

   
Logger Module
-------------

Base Logger Module class and functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pyfrid.modules.system.logger
   :members:

   