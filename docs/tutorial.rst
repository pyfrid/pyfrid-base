
Tutorial
========

PyFRID as a framework comes with a set of tools to make your life a bit easier.
These tools are split into two categories: administration tools and application related tools.

The administration tools are executed by the script :program:`pyfrid-admin command_name`
and the application related tools are called as :program:`python appname command_name`,
where *appname* and *command_name* are names of your application and a command which
you would like to execute.

Creating a project
------------------
Go to the directory where you would like to create your project and simply run::

   $ pyfrid-admin newproj your_app_name

Do not forget to change *your_app_name* to something real.
If your project was created succesfully you will see the following message::
   
   $ Project 'your_app_name' was successfully created

Starting application
--------------------

The default application contains the most important commands and few dummy devices.
It doesn't do anything useful, but it is certainly enough to play with and to get a feeling of
how it works. 
Outside the root directory of your project run::

   $ python your_app_name cmdline
   
You will see something like this::

    logger       INFO  Initialization...
    authentication       INFO  Initialization...
                vm       INFO  Initialization...
       application       INFO  Initialization...
            motor1       INFO  Initialization...
            motor2       INFO  Initialization...
           shutter       INFO  Initialization...
              init       INFO  Initialization...
            status       INFO  Initialization...
           whereis       INFO  Initialization...
             sleep       INFO  Initialization...
               get       INFO  Initialization...
               set       INFO  Initialization...
             macro       INFO  Initialization...
              move       INFO  Initialization...
         reference       INFO  Initialization...
            switch       INFO  Initialization...
   your_app_name>

   
The command line tool has standard completion capabilities. Simply press on *Tab* twice and you will see a list
of all possible commands::

   get        init       macro      move       reference  set        sleep      status     switch     whereis


If you have typed a command name, press *Tab* again and you will get completions
for the command parameters.

If you have installed package with web application you can run it by::

   $ python your_app_name webapp
   
This command will start the web server. The GUI can be accessed with your browser.


Creating new command
--------------------

To create new command::

   $ python your_app_name newcmd your_command_name


Creating new device
-------------------

To create new device::

   $ python your_app_name newcmd your_device_name


Creating new module
-------------------

To create new module::

   $ python your_app_name newcmd your_module_name


