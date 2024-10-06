"""
Copyright 2007 VMware, Inc.  All rights reserved. -- VMware Confidential

VIX Core component installer.
"""
DEST = LIBDIR/'vmware-vix'
SETTINGS = { 'vmware.fullpath': BINDIR/'vmware',
             'vix.libdir': DEST, }
CONF = DEST/'setup/vmware-config'

class VIXCore(Installer):
   def InitializeInstall(self, old, new, upgrade):
      self.AddTarget('File', 'doc/*', DOCDIR/'vmware-vix')
      self.AddTarget('File', 'include/*', INCLUDEDIR/'vmware-vix')
      self.AddTarget('File', 'lib/*', DEST)
      self.AddTarget('File', 'api/*', DEST/'api')
      self.AddTarget('File', 'man/*', MANDIR/'man3')
      self.AddTarget('Link', DEST/'libvixAllProducts.so', LIBDIR/'libvixAllProducts.so')
      self.AddTarget('File', 'bin/*', BINDIR)
      self.AddTarget('File', 'open_source_licenses.txt', DEST/'open_source_licenses.txt')
      self.AddTarget('File', 'vixwrapper-config.txt', DEST/'vixwrapper-config.txt')
      self.AddTarget('File', 'vix-perl.tar.nogz', DEST/'vix-perl.tar.gz')

      self.SetPermission(CONF, BINARY)
      self.SetPermission(BINDIR/'*', BINARY)

   def PostInstall(self, old, new, upgrade):
      for key, val in list(SETTINGS.items()):
         self.RunCommand(CONF, '-s', key, val)

   def PreUninstall(self, old, new, upgrade):
      # XXX: VIX may have been removed out from underneath us if
      # running under the Workstation install, so don't fail if so.
      for key in list(SETTINGS.keys()):
         CONF.exists() and self.RunCommand(CONF, '-d', key)

