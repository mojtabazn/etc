##############################################################
#  Copyright (c) 2022 VMware, Inc.  All rights reserved.
##############################################################

#
#  initscript.py --
#
#       This module provides a common interface for installing, configuring and
#       managing services across a variety of init systems.  Right now we
#       support insserv, chkconfig, and update-rc.d and (rudimentary) systemd.
#

#       Service is not installed.
#         |                  ^
#         |                  |
#  PrepareService()   UnprepareService()
#         |                  |
#         v                  |
#    Service files are installed but
#     init system is not configured.
#         |                  ^
#         |                  |
# ConfigureService() UnconfigureService()
#         |                  |
#         v                  |
#        Init system is ready to
#        control service state.
#         |                  ^
#         |                  |
#   StartService()     StopService()
#         |                  |
#         v                  |
#          Service is running.
#
#
#
# PrepareService should be called from a component's InitializeInstall, which
# is _before_ the component's contents are installed.  PrepareService may
# inform the installer of additional service-specific file(s) and symlink(s) to
# be installed; The installer will take care of copying and creating files as
# described.
#
# ConfigureService should be called from a component's PostInstall.  The
# component's contents have been installed onto the filesystem.
# ConfigureService may perform final configuration and make the init system
# aware of the new service.
#
# UnconfigureService should be called from a component's PreUninstall.  The
# component's contents are still present on the filesystem.  UnconfigureService
# may inform the init system that the service will be removed.
#
# UnprepareService should be called from a component's PostUninstall.  The
# component's contents will no longer be present on the filesystem -- whatever
# the installer created during component installation will automatically be
# removed during uninstallation.  UnprepareService may inform the init system
# that the service has been removed.
#
# StopService and StartService may be called on a configured service in order
# to ask the init system to control the service's running state.
#

def _ScriptFile(initType, serviceName):
   """Determine the install location for a service script file for the given
      init system."""
   initDest = DEST/'scripts/init' if initType == 'systemd' else INITSCRIPTDIR
   return initDest/serviceName

def PrepareService(serviceName, initScriptFile, systemdUnitFile):
   """Inform the installer of additional file/symlink installations as they
      pertain to this service under the given init system."""
   (initType, initProgram) = InitConfigProgram()
   scriptFile = _ScriptFile(initType, serviceName)
   inst.AddTarget('File', initScriptFile, scriptFile)
   inst.SetPermission(scriptFile, BINARY)
   if initType == 'systemd':
      # Install the unit file too.
      systemdSystemUnitDir = _SystemdSystemUnitDir()
      if systemdSystemUnitDir:
         unitFileName = '%s.service' % serviceName
         unitFile = path(systemdSystemUnitDir)/unitFileName
         inst.AddTarget('File', systemdUnitFile, unitFile)

def ConfigureService(serviceName, description, lsbStartDep, lsbStopDep, lsbStartBefore,
                     lsbStopAfter, chkcfgStartLevel, chkcfgStopLevel):
   """
   Configure a service using the program appropriate for the current system.
   On a systemd host, most of the arguments are ignored; The unit file will
   provide equivalent information.

   ********                        READ ME ...  IMPORTANT!
   ********
   ******** This function expects the component using it to have the initinfo scripts in
   ******** initinfo/initinfo.*.  They shouldn't be installed, they should just be included
   ******** in the component.  Without them, it will fail.
   ********

   @param serviceName: The service name, matches the script name
   @param description: Text description of the service.  Single-line only
   @param lsbStartDep: Space separated list of services that must be started *before* this service.
   @param lsbStopDep: Space separated list of services that must be stopped *after* this service.
   @param lsbStartBefore: Space separated list of reverse deps.  This package must start before these.
   @param lsbStopAfter: Space separated list of reverse deps.  This package must stop after these.
   @param chkcfgStartLevel: The start number for chkconfig or update-rc.d scripts
   @param chkcfgStopLevel: The stop number for chkconfig or update-rc.d scripts
   """
   (initType, initProgram) = InitConfigProgram()

   scriptFile = _ScriptFile(initType, serviceName)
   if not scriptFile.exists():
      # TODO: Raise a dialog informing the user that we are unable to add init script links.
      # TODO: This can take the place of Workstation's current message for Gentoo and Arch
      # TODO: systems.
      return

   if not initType:
      # We can't use a program to do it for us, lay down the links ourselves.
      if not INITDIR:
         # TODO: Raise a dialog informing the user that we are unable to add init script links.
         # TODO: This can take the place of Workstation's current message for Gentoo and Arch
         # TODO: systems.
         log.Warn('INITDIR has not been set.  No rc?.d style dirs '
                    'to populate.')
         return

      pattern = 'rc%(runlevel)d.d/%(letter)s%(priority)02d%(name)s'

      for runlevel in (2, 3, 5):
         # Build symlinks for this runlevel
         startLink = path(INITDIR/(pattern % {'runlevel': runlevel, 'letter': 'S',
                                              'priority': chkcfgStartLevel, 'name': serviceName}))
         stopLink = path(INITDIR/(pattern % {'runlevel': runlevel, 'letter': 'K',
                                             'priority': chkcfgStopLevel, 'name': serviceName}))
         try:
            scriptFile.symlink(startLink)
         except OSError as e:
            pass # Okay if it already exists
         try:
            scriptFile.symlink(stopLink)
         except OSError as e:
            pass # Okay if it already exists

         # Register files with the installer.  It will clean them up on uninstall.
         inst.RegisterFile(startLink)
         inst.RegisterFile(stopLink)

   script = scriptFile.text()

   if initType == 'insserv':
      # Add the insserv style header and add our service
      initheader = inst.GetFileText('initinfo/initinfo.lsb')
      initheader = re.sub('@@SERVICE_NAME@@', serviceName, initheader)
      initheader = re.sub('@@LSB_SERVICE_START_DEP@@', lsbStartDep, initheader)
      initheader = re.sub('@@LSB_SERVICE_STOP_DEP@@', lsbStopDep, initheader)
      initheader = re.sub('@@LSB_SERVICE_START_BEFORE_DEP@@', lsbStartBefore, initheader)
      initheader = re.sub('@@LSB_SERVICE_STOP_AFTER_DEP@@', lsbStopAfter, initheader)
      initheader = re.sub('@@SERVICE_DESCRIPTION@@', description, initheader)
      txt = re.sub('# VMWARE_INIT_INFO', initheader, script, re.DOTALL)
      scriptFile.write_text(txt)
      inst.RunCommand('/bin/sh', '-c', '%s -f %s >/dev/null 2>&1' % (initProgram, serviceName), ignoreErrors=True)

   if initType == 'chkconfig':
      # Add the chkconfig style header and add our service
      initheader = inst.GetFileText('initinfo/initinfo.chkconfig')
      initheader = re.sub('@@CHKCFG_START_LEVEL@@', str(chkcfgStartLevel), initheader)
      initheader = re.sub('@@CHKCFG_STOP_LEVEL@@', str(chkcfgStopLevel), initheader)
      initheader = re.sub('@@SERVICE_DESCRIPTION@@', description, initheader)
      txt = re.sub('# VMWARE_INIT_INFO', initheader, script, re.DOTALL)
      scriptFile.write_text(txt)
      inst.RunCommand(initProgram, '--add', serviceName, ignoreErrors=True)

   if initType == 'update-rc.d':
      # Add the insserv style header and add our service
      initheader = inst.GetFileText('initinfo/initinfo.updaterc')
      initheader = re.sub('@@SERVICE_NAME@@', serviceName, initheader)
      initheader = re.sub('@@LSB_SERVICE_START_DEP@@', lsbStartDep, initheader)
      initheader = re.sub('@@LSB_SERVICE_STOP_DEP@@', lsbStopDep, initheader)
      initheader = re.sub('@@LSB_SERVICE_START_BEFORE_DEP@@', lsbStartBefore, initheader)
      initheader = re.sub('@@LSB_SERVICE_STOP_AFTER_DEP@@', lsbStopAfter, initheader)
      initheader = re.sub('@@SERVICE_DESCRIPTION@@', description, initheader)
      txt = re.sub('# VMWARE_INIT_INFO', initheader, script, re.DOTALL)
      scriptFile.write_text(txt)
      inst.RunCommand(initProgram, serviceName,
                      'start', chkcfgStartLevel, '2', '3', '4', '.',
                      'stop', chkcfgStopLevel, '0', '6', '.', ignoreErrors=True)

   if initType == 'systemd':
      # The init script does not need any init info section.  Delete it.
      txt = re.sub('# VMWARE_INIT_INFO', '', script, re.DOTALL)
      scriptFile.write_text(txt)

      systemdSystemUnitDir = _SystemdSystemUnitDir()
      if systemdSystemUnitDir:
         # Fill in the systemd unit file.
         unitFileName = '%s.service' % serviceName
         unitFile = path(systemdSystemUnitDir)/unitFileName
         unit = unitFile.text()
         unit = re.sub('@@INITSCRIPTDIR@@', str(INITSCRIPTDIR), unit)
         unit = re.sub('@@INITSCRIPT@@', str(scriptFile), unit)
         unitFile.write_text(unit)
         inst.RunCommand(initProgram, 'enable', '%s.service' % (serviceName))

   log.Info('Installed Service: %s' % serviceName)

def UnconfigureService(serviceName):
   """Deactivate the service, in a manner suitable for the init system."""
   (initType, initProgram) = InitConfigProgram()
   if not initType:
      # The links have been registered with the installer.  It will remove them on
      # uninstall.
      pass

   if initType == 'insserv':
      inst.RunCommand('/bin/sh', '-c', '%s -f -r %s >/dev/null 2>&1' % (initProgram, serviceName), ignoreErrors=True)
   if initType == 'chkconfig':
      inst.RunCommand(initProgram, '--del', serviceName, ignoreErrors=True)
   if initType == 'update-rc.d':
      inst.RunCommand(initProgram, '-f', serviceName, 'remove', ignoreErrors=True)
   if initType == 'systemd':
      inst.RunCommand(initProgram, 'disable', '%s.service' % (serviceName))

   log.Info('Uninstalled Service: %s' % serviceName)

def UnprepareService(serviceName):
   """Handle the removal of a service, in a manner suitable for the init
      system."""
   (initType, initProgram) = InitConfigProgram()
   if initType == 'systemd':
      inst.RunCommand(initProgram, 'daemon-reload', ignoreErrors=True)

def _StartStopService(serviceName, action, ignoreErrors):
   if ENV.get('VMWARE_SKIP_SERVICES'):
      log.Info('Skipping service %s.' % (action))
      return True
   (initType, initProgram) = InitConfigProgram()
   if initType == 'systemd':
      inst.RunCommand(initProgram, action, '%s.service' % serviceName, ignoreErrors=ignoreErrors)
      return True
   if INITSCRIPTDIR:
      script = INITSCRIPTDIR/serviceName
      if script.exists():
         return inst.RunCommand(script, action, ignoreErrors=ignoreErrors).retCode == 0
   log.Info('No method to %s service "%s".' % (action, serviceName))
   return False

def StartService(serviceName, ignoreErrors=True):
   """Ask the init system to start the given service."""
   return _StartStopService(serviceName, 'start', ignoreErrors)

def StopService(serviceName, ignoreErrors=True):
   """Ask the init system to stop the given service."""
   return _StartStopService(serviceName, 'stop', ignoreErrors)

def InitConfigProgram():
   """
   Scan the system to try and guess the program that sets up the init script links.
   On RHEL, it's chkconfig/systemd, on SuSE it's insserv, and on Ubuntu it's
   update-rc.d.

   NOTE: Don't use insserv on Ubuntu per bug 776485.  Ubuntu so very wisely ships
         it but expects developers not to use it.
   """

   if INITDIR:
      # First, check for update-rc.d b/c we want to use it instead
      # of insserv on Ubuntu and Debian systems.
      if path('/usr/sbin/update-rc.d').isexe():
         return ('update-rc.d', '/usr/sbin/update-rc.d')
      elif path('/sbin/update-rc.d').isexe():
         return ('update-rc.d', '/sbin/update-rc.d')
      elif (_which('update-rc.d')):
         return ('update-rc.d', _which('update-rc.d'))

      if path('/sbin/insserv').isexe():
         return ('insserv', '/sbin/insserv')
      elif _which('insserv'):
         return ('insserv', _which('insserv'))

      if path('/sbin/chkconfig').isexe():
         return ('chkconfig', '/sbin/chkconfig')
      elif (_which('chkconfig')):
         return ('chkconfig', _which('chkconfig'))

   if path('/usr/bin/systemctl').isexe():
      return ('systemd', '/usr/bin/systemctl')
   elif (_which('systemctl')):
      return ('systemd', _which('systemctl'))

   return (None, None)

def _SystemdSystemUnitDir():
   """Identify the directory in which systemd unit files should be stored."""
   # systemdsystemunitdir (e.g. /lib/systemd/system) is supposed to be for the
   # distro's use.
   #
   # systemdsystemconfdir (e.g. /etc/systemd/system) is supposed to be for the
   # system administrator's use.
   #
   # We are not really either of those... but systemdsystemunitdir seems the
   # better choice.
   pc = inst.RunCommand('pkg-config', 'systemd', '--variable=systemdsystemunitdir', ignoreErrors=True)
   if pc.retCode == 0:
      return pc.stdout.strip()

   for candidate in ['/lib/systemd/system', '/usr/lib/systemd/system']:
      if path(candidate).exists():
         return candidate

   return None

def _which(program):
   """
   Gets the PATH environment variable and checks for program
   in order.

   @param program: Executable to search for
   @returns: Full path if found and executable, None otherwise
   """
   # XXX: Borrowed from util/shell.py.  This should be broken into a
   # utility file to be used by both components and the main code.
   systemPath = ENV['PATH']
   paths = systemPath.split(':')
   for p in paths:
      fullPath = path(p)/program
      if fullPath.isexe():
         return str(fullPath) # Return a string, not a path object

   return None
