Introduction
============

This is the documentation for PyFRID, Python Framework for an Instrument Development.  
PyFRID is a tool for creating versatile flexible applications for an instrument from simple
laboratory setup, to something more complex like neutron or X-ray diffractometer.
That is, if you have a bunch of motors, sensors, detectors or any other hardware and would like
to manipulate them, to program their behavior, to test them and represent information from them in a convinient way,
PyFRID will give you these capabilities and will organize your hardware under a command line application
or a web-based Graphical User Interface.

.. figure:: /images/web.png
   :scale: 30 %
   :alt: map to buried treasure
   :align: right
   
   Web interface of application created with PyFRID
   
Pyfrid is a modular framework. The building blocks of PyFRID are devices, commands and modules. 

The central part of PyFRID is a simple script language. The script language consists of commands,
which give control over the components like devices and modules.
The control level can be limited by the Authentication system module and customizable
permissions for all operations and objects. The PyFRID"s virtual machine system module, based on LEPL_, 
will take care of syntax error check, validation, runtime calculation and running of script or command.
The parsing, validation and runtime calculation are done before the actual execution of a script,
making sure that your script will not stop during the night because of a mistake and you will not loose time.
  

Prerequisites
-------------

PyFRID needs **Python 2.6** or **Python 2.7** to run, it also dependent on LEPL_ and PyYAML_.
YAML format is used by default for the configuration, logging and data format. These packages are installed automatically,
if you have not installed them before.

.. _LEPL: http://www.acooke.org/lepl
.. _PyYAML: http://pyyaml.org/ 


Usage
-----

See :doc:`tutorial` for an introduction.  It also contains links to more
advanced sections in this manual for the topics it discusses.
