"""
Copyright 2010-2019 VMware, Inc.  All rights reserved. -- VMware Confidential

VMware Network Editor UI component installer.
"""

DEST = LIBDIR/'vmware'

class NetworkEditorUI(Installer):
   """
   This class contains the installer logic for the Network Editor UI component.
   """
   def InitializeInstall(self, old, new, upgrade):
      self.AddTarget('File', 'bin/*', BINDIR)
      self.AddTarget('File', 'share/icons/*', DATADIR/'icons')
      self.SetPermission(BINDIR/'*', BINARY)

      if self.GetConfig('installShortcuts', component='vmware-installer') != 'no':
         self.AddTarget('File', 'share/applications/*', DATADIR/'applications')
         self.AddTarget('Link', DATADIR/'applications/vmware-netcfg.desktop',
                        PREFIX/'local/share/applications/vmware-netcfg.desktop')

   def PostInstall(self, old, new, upgrade):
      if self.GetConfig('installShortcuts', component='vmware-installer') != 'no':
         launcher = DATADIR/'applications/vmware-netcfg.desktop'
         binary = BINDIR/'vmware-netcfg'
         self.RunCommand('sed', '-e', 's,@@BINARY@@,%s,g' % binary, '-i', launcher)

      updateModule = self.LoadInclude('update')
      updateModule.UpdateIconCache(self, DATADIR)
      updateModule.UpdateMIME(self, DATADIR)
