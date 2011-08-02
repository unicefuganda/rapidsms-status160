Status160
=========
Status160 is an emergency response system designed to alleviate the demands of a calling tree in an emergency situation: staff members who are safe and able to send an SMS can respond to a status survey with 'YES' indicate that they needn't be contacted, allowing emergency reponders to devote time to those whose status is unknown.  Status160 can also send SMS alerts to wardens with charges who are unsafe/unknown.

Status160 provides a basic dashboard view for managing contacts.  A running example can be seen at status160.rapidsms.org.

Requirements
============
 - Python 2.6 (www.python.org/download/) : On linux machines, you can usually use your system's package manager to perform the installation
 - MySQL or PostgreSQL are recommended
 - All other python libraries will be installed as part of the setup and configuration process
 - Some sort of SMS Connectivity, via an HTTP gateway.  By default, Status160 comes configured to work with a two-way clickatell number (see http://www.clickatell.com/downloads/http/Clickatell_HTTP.pdf and http://www.clickatell.com/downloads/Clickatell_two-way_technical_guide.pdf).  Ideally, you want to obtain a local short code in your country of operation, or configure Status160 to use a GSM modem (see http://docs.rapidsms.org for more information on how to do this).

Installation
============
Before installation, be sure that your clickatell two-way callback points to::

     http://yourserver.com/status160/clickatell/

This is essential if you want to receive incoming messages.

It's highly recommended that you use a virtual environment for a Ureport project.  To set this up, create the folder where you want your Ureport project to live, and in a terminal, within this folder, type::

    ~/Projects/status160$ pip install virtualenv
    ~/Projects/status160$ virtualenv env
    ~/Projects/status160$ source env/bin/activate

Status160 can be installed from a terminal using::

   ~/Projects/status160$ pip install -e git+http://github.com/daveycrockett/rapidsms-status160#egg=status160

Configuration
=============
For linux, the provided status160-install.sh script can be run immediately after installation::

    ~/Projects/status160$ status160-install.sh

This will do some basic configuration to get your install up-and-running.  It makes some assumptions about the configuration of whatever database software you've installed, so if you're more confident with performing each step manually, here's a summary of what the script does:

 - Creates a project folder for Status160 (running status160-admin.py startproject status160-project)
 - Tweaks the settings.py file in your project to your parameters (settings.DATABASES, clickatell account information)
 - Creates the database tables (running manage.py syncdb)
 - Runs the server (running manage.py runserver)

After you've completed this configuration, you should be able to point your browser to http://localhost:8000/ and see your status160 install up and running!  To start uploading users, login as admin to create Staff and Staff Groups.
