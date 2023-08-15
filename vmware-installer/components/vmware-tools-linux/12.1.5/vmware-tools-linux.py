#
# Copyright 2009,2018 VMware, Inc.  All rights reserved. -- VMware Confidential
#

"""
VMware Tools ISO Component.

This is the VMIS template component file for the linux Tools ISO, where
linux will be replaced by the name of the specific iso (ie: linux,
windows, freebsd...)
"""
DEST = LIBDIR/'vmware/isoimages'

class ToolsISOlinux(Installer):
   def InitializeInstall(self, old, new, upgrade):
      self.AddTarget('File', 'linux.iso', DEST/'linux.iso')
