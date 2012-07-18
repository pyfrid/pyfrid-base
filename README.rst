PyFRID - Python Framework for Instrument Development
----------------------------------------------------

**PyFRID** is a tool for creating flexible applications for an instrument from simple
laboratory setups to more complex instruments like neutron or X-ray diffractometers.
If you have a bunch of motors, sensors, detectors, etc. and would like to manipulate
them, to program their behavior, to test them and represent information in a convenient way,
PyFRID will give you these capabilities and will organize your hardware under a command line
or web-based application.

Applications created with PyFRID have modular structure with building blocks like devices,
commands and modules. The central part of an application is a simple script language.
The script language consists of commands, which give control over the components like devices
and modules. The control level can be limited by the Authentication system module and by
customizable permissions for all operations and objects. The PyFRID's virtual machine system
module, based on LEPL, will take care of syntax error checking, validation, runtime calculations
and running of scripts. The parsing, validation and runtime calculations are done before 
the actual execution of a script, making sure that your script will not stop during the
night because of a mistake and you will not loose your measurement time.