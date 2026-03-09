"""
Copyright 2012, 2015 VMware, Inc.  All rights reserved. -- VMware Confidential

VProbes component installer.

   Targets:

   - LIBDIR/vmware/lib/libvmware-vprobe.so
   - LIBDIR/vmware/bin/emmett
   - LIBDIR/vmware/bin/vmware-vprobe (symlink -> LIBDIR/vmware/bin/appLoader)
   - /usr/bin/vmware-vprobe          (copy of wrapper-generic.vmis.sh)
"""

DEST = LIBDIR/'vmware'

class VProbes(Installer):

   def InitializeInstall(self, old, new, upgrade):

      self.AddTarget('File', 'lib/bin/*', DEST/'bin')
      self.AddTarget('File', 'lib/lib/*', DEST/'lib')
      self.AddTarget('File', 'bin/*',     BINDIR)

      self.SetPermission(DEST/'*', BINARY)
      self.SetPermission(BINDIR/'*', BINARY)

      # Symlink to AppLoader.
      self.AddTarget('Link', DEST/'bin/appLoader', DEST/'bin/vmware-vprobe')
