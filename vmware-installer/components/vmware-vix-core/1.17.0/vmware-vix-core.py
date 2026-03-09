"""
Copyright (c) 2007-2025 Broadcom. All Rights Reserved.
Broadcom Confidential. The term "Broadcom" refers to Broadcom Inc.
and/or its subsidiaries.

VIX Core component installer.
"""

DEST = LIBDIR/'vmware-vix'
DESTVMWARE = LIBDIR/'vmware/'
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
      """ 
      - We will not copy binaries staged via vix to BINDIR directly. This is required
        because symlink to apploader cannot be created if binary already exists in BINDIR.
      - Copy binaries inside vmware/bin directory first and then create required symlinks
        for each one of them.
      - right now 3 binaries comes from vix-core: vmrun, vmcli and dictTool.
      """
      self.AddTarget('File', 'bin/*', DESTVMWARE/'bin')
      self.AddTarget('File', 'open_source_licenses.txt', DEST/'open_source_licenses.txt')
      self.AddTarget('File', 'vixwrapper-config.txt', DEST/'vixwrapper-config.txt')
      self.AddTarget('File', 'vix-perl.tar.nogz', DEST/'vix-perl.tar.gz')

      self.SetPermission(CONF, BINARY)
      self.SetPermission(DESTVMWARE/'*', BINARY)
      # Create symlink for vmrun and vmcli
      self.AddTarget('Link', DESTVMWARE/'bin/appLoader', BINDIR/'vmrun')
      self.AddTarget('Link', DESTVMWARE/'bin/vmcli', BINDIR/'vmcli')

   def PostInstall(self, old, new, upgrade):
      for key, val in list(SETTINGS.items()):
         self.RunCommand(CONF, '-s', key, val)

   def PreUninstall(self, old, new, upgrade):
      # XXX: VIX may have been removed out from underneath us if
      # running under the Workstation install, so don't fail if so.
      for key in list(SETTINGS.keys()):
         CONF.exists() and self.RunCommand(CONF, '-d', key)

