"""
Copyright 2010,2020,2022 VMware, Inc.  All rights reserved. -- VMware Confidential

VMware USB Arbitrator component installer.
"""

import os
from vmis.util.path import path

DEST = LIBDIR/'vmware'

class USBArbitrator(Installer):
   """
   This class contains the installer logic for the USB Arbitrator component.
   """
   def InitializeInstall(self, old, new, upgrade):
      inits = self.LoadInclude('initscript')
      self.AddTarget('File', 'bin/*', DEST/'bin')
      self.SetPermission(DEST/'bin/*', BINARY)

      # Register the init script and link to the appropriate runlevels
      inits.PrepareService('vmware-USBArbitrator', 'etc/init.d/vmware-USBArbitrator', 'systemd/vmware-USBArbitrator.service')

   def PreUninstall(self, old, new, upgrade):
      # Stop and unconfigure the USB Arbitrator service
      inits = self.LoadInclude('initscript')
      # Set "SYSTEMCTL_SKIP_REDIRECT" to skip systemctl when doing
      # start/stop action, such as RHEL 8 which systemctl will bring
      # trouble for USB Arbitrator service start/stop.
      os.environ['SYSTEMCTL_SKIP_REDIRECT'] = "1"
      if not inits.StopService('vmware-USBArbitrator', ignoreErrors=True):
         log.Warn('Unable to stop USB Arbitrator service.')
      # Unset "SYSTEMCTL_SKIP_REDIRECT".
      del os.environ['SYSTEMCTL_SKIP_REDIRECT']

      inits.UnconfigureService('vmware-USBArbitrator')

      self.pycFile = None
      if upgrade:
         # It means that this is installed vmis and will be uninstalled,
         # the installing Python runtime is version-higher than or equals
         # to ours, remember the .pyc file location to make sure it will
         # be removed in the phase PostUninstall.
         pycFile = getattr(inits, '__cached__', '')
         if not pycFile:
            pyFile = getattr(inits, '__file__', '')
            if pyFile:
               pycFile = self.CompilePythonFile(pyFile)
         if pycFile:
            self.pycFile = path(pycFile)


   def PostUninstall(self, old, new, upgrade):
      # If there is a backup LIBDIR/'vmware/lib/vmware-usbarbitrator.old'
      # then restore it, otherwise, remove it.
      orig = BINDIR/'vmware-usbarbitrator'
      backup = LIBDIR/'vmware/lib/vmware-usbarbitrator.old'
      try:
         orig.remove()
      except OSError:
         # Pass if it is already gone
         pass
      if backup.exists():
         backup.copyfile(str(orig))
         orig.chmod(0o755)
         backup.remove()

      if self.pycFile and self.pycFile.exists():
         # Remove the initscript.pyc file if it is still existing.
         self.pycFile.unlink(ignore_errors=True)

      inits = self.LoadInclude('initscript')
      inits.UnprepareService('vmware-USBArbitrator')

   def PostInstall(self, old, new, upgrade):
      # If an arbitrator already exists and it's not a symlink, back
      # it up and create a symlink to our new ones.  This must be
      # done for co-installs with WS 7.x
      arb = BINDIR/'vmware-usbarbitrator'
      if arb.exists():
         if not arb.islink():
            # Make the destination directory if it doesn't already exist
            dest = path(LIBDIR/'vmware/lib')
            if not dest.exists():
               dest.makedirs()
            # Backup the program (Don't use a path, explicitly convert to a string)
            arb.copyfile(str(LIBDIR/'vmware/lib/vmware-usbarbitrator.old'))
            arb.remove()
         else:
            # Remove the old link
            arb.remove()

      # Now that our space in the BINDIR is clear, install the symlink.
      path(LIBDIR/'vmware/bin/vmware-usbarbitrator').symlink(str(arb))

      inits = self.LoadInclude('initscript')
      inits.ConfigureService('vmware-USBArbitrator',
                             'This services starts and stops the USB Arbitrator.',
                             'localfs', # Start
                             'localfs', # Stop
                             '',
                             '',
                             50,
                             8)

      # (Re)start the USB Arbitrator service

      # Set "SYSTEMCTL_SKIP_REDIRECT" to skip systemctl when doing
      # start/stop action, such as RHEL 8 which systemctl will bring
      # trouble for USB Arbitrator service start/stop.
      os.environ['SYSTEMCTL_SKIP_REDIRECT'] = "1"
      if not inits.StopService('vmware-USBArbitrator', ignoreErrors=True):
         log.Warn('Unable to stop current USB Arbitrator service.  Not fatal.')
      if not inits.StartService('vmware-USBArbitrator', ignoreErrors=True):
            log.Error('Unable to start USB Arbitrator service.')
      # Unset "SYSTEMCTL_SKIP_REDIRECT".
      del os.environ['SYSTEMCTL_SKIP_REDIRECT']
