# fullstack-nanodegree-vm

## Getting Started

### for Mac or Linux 
regular terminal program on your computer
### for Windows
you need to use Git Bash terminal for this Project,if you don't have ,[click here to install](https://git-scm.com/downloads)
### next steps for all
1. install VirtualBox ,[You can download it from here.](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1) Install the platform package for your operating system. You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it; Vagrant will do that.
2. download Vagrant from [here](https://www.vagrantup.com/downloads.html). Install the version for your operating system.
3. download thiscd  project as zip file from github or use git clone. Inside this project is the VM configuration. In case you download it as zip file, Unzip the file. This will give you a directory called fullstack-nanodegree-vm. Also if you git cloned it. 
4. Open a terminal or git bash. Under the fullstack-nanodegree-vm directory find the vagrant directory and change to this location. After run the command
```
vagrant up
```
This will cause Vagrant to download a Linux operating system image and install it. This may take quite a while.when vagrant up is finished running,you can run 
```
vagrant ssh
```
to log in to your newly installed linux VM.

5. To execute the restaurant application first we need to fill the data into the local database, so first
```
cd /vagrant/restaurantwithflask
```
to change into the vagrant directory and use the command 
```
python database_setup.py
```
```
python lotsofmenus.py
```
the 2 commands above will create a new database , tables and fill them with data.

6. run the python programm with this command
```
 python project.py
```
this will start a server on your virtual machine ,you can access it with your broswer (on your normal physical machine).
