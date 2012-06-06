
Tutorial
========

PyFRID comes with a set of tools to make your life a bit easier.
These tools are split into two categories: administration tools and application related tools.

The administration tools are executed by the script :program:`pyfrid-admin command_name [options]`
and the application related tools are called as :program:`python appname command_name [options]`,
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
In the same directory where you have executed previous command run::

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
   
This command will start the web server and you will be able to access your application via Web browser.

In the following sections we will consider how to add new commands, devices and modules to your application.


Creating new command
--------------------

Pyfrid has a special management tool which is called *newcmd*. This tool does few things: it creates  a default configuration 
for your new command from the template and source python file with a default implementation of the command class. 

For example we would like to create a new command with name *pause*, which will pause running script for a given amount of seconds.
Simply run::

   $ python your_app_name newcmd pause
   
Change your current directory to::

   $ cd your_app_name/config
   
In the end of *commands.yml* file you will find a default configuration for the command *pause*::

   ---
   alias: pause
   name: pause
   active: True

where "---" is a separator between configurations for commands presented in your application,
*alias* is a special internal name of this command which is used by PyFRID as identificator of this command,
*name* is a name which user will use to call this command and
*active* is a flag for the command activation or deactivation (needs restart of application)  
   
Now let's have a look on source code of the newly created command, change the current directory to::

      $ cd your_app_name/commands
      
and open the file *pause.py* with your favorite editor::

      from pyfrid.core import BaseCommand
      
      class PauseCommand(BaseCommand):
      
          alias="pause"
          
          descr="Type here a description..."
          
          def grammar(self):
              return super(PauseCommand,self).grammar()
              
          def execute(self,*args,**kwargs):
              return super(PauseCommand,self).execute(*args,**kwargs)
              
          def validate(self,*args,**kwargs):
              return super(PauseCommand,self).validate(*args,**kwargs)
              
          def runtime(self,*args,**kwargs):
              return super(PauseCommand,self).runtime(*args,**kwargs)

The *PauseCommand* class inherites attributes and behavior from pre-existing base classes *BaseCommand* which is a part of PyFRID.
*alias* is the most important attribute of any class in application. It plays a role of identificator of a command, device or module.
Alias must be chosen only once, especially for a command, because it can be used in the application code. In the next section you will
see how commands aliases are used to define a functionality of devices.  

Method *grammar* returns a tuple *([arg1, arg2], minrep, maxrep)*, where *arg1* and *arg2* are types of a command arguments, *minrep* and
*maxrep* are minimum and maximum number of repetitions of arguments, repectively. All parameters of the tuple can be *None*, this is  default
value returned by the *grammar* method in *BaseCommand* class.
 
Our new *pause* command will accept one parameter of type float and the code of *grammar* method become::

        def grammar(self):
            from pyfrid.modules.system.vm.leplvm import FLOATCONST
            return (FLOATCONST, 1, 1)
            
where *FLOATCONST* is a grammar rule imported from the *virtual machine* module.
Other grammars and their descriptions you will find there too.

The next important method of a command is *execute*. One expects the *pause* command to inform  user that it is going to sleep 
for some time, then their must be a code for "sleeping" and in the end the command will inform  user that sleeping is finished and it wakes up::

         def execute(self,val):
           self.info("Going to sleep for {0} sec...".format(val))
           start=time.time()
           while time.time()-start<val and not self.stopped: time.sleep(0.02)
           self.info("Waking up...")  

Instead of standard *sleep* method from the *time* module, it is wise to use a while loop with short time pauses, because there is no simple way to interrupt
the standard "sleeping".

The *validate* method is used to make additional check of the parameters. For example, one can implement a check for the time limits.
This method must return *True* or *False* depending on the result of validation.

The *runtime* method returns an estimated running time of the command. In the case of the *pause* command the running time is simply the *time* argument::

         def runtime(self, tm, **kwargs):
           return tm
        
 
Creating new device
-------------------
The steps of creation of a new device are the same as for a command.
To create a new device with name *motor* simply type::

   $ python your_app_name newdev motor
   
The *newdev* management tool will create a new configuration in the *device.yml* file and new source file in the folder *devices*.
Below is the code for the new device::

   from pyfrid.core import BaseDevice

   class MotorDevice(BaseDevice):
   
       alias="motor"
       
       descr="Type here a description..."
       
       def position(self):
           return super(MotorDevice,self).position()
           
       def status(self):
           return super(MotorDevice,self).status()
   
The *position*  and *status* methods return a current position and a current status of the created device, respectively. 
By default these methods return *None* value. A status of device is a tuple with the next structure::
       
       def status(self):
           return (
               ("item1", value1, "units1"),
               ("item2", value2, "units2"),
           )

where status items can be any hardware or software values related to your device. For example, a motor status can contain *Moving* parameter with True or False values.
It also can be *End switch* - "On" or "Off", if exists, *Hardware Error* flag and so on.

By default our new *motor* device doesn't have any functionality, i.e. it is unknown for commands presented in PyFRID. Normally motors are moveable devices and PyFRID has
a special command *move* wich has alias of the same name. Move command accepts any device and its position as an argument. The validation method of this command will check
whether this command is moveable and will return False with error if it is not.

In order to make our motor moveable we add the following method to its class::

      def do_move(self, pos):
          harware_move_function(pos)
          curpos=read_current_pos_from_harware()
          return curpos
          
The name of this method consists of two parts *do_* and a command alias, *move* in our case. This method must return
a current position of device read from hardware.  



Creating new module
-------------------

To create new module::

   $ python your_app_name newmod your_module_name


