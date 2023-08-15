#
# Copyright 2009,2018 VMware, Inc.  All rights reserved. -- VMware Confidential
#

"""
VMware Tools ISO Component.

This is the VMIS template component file for the linuxPreGlibc25 Tools ISO, where
linuxPreGlibc25 will be replaced by the name of the specific iso (ie: linux,
windows, freebsd...)
"""
DEST = LIBDIR/'vmware/isoimages'

class ToolsISOlinuxPreGlibc25(Installer):
   def InitializeInstall(self, old, new, upgrade):
      self.AddTarget('File', 'linuxPreGlibc25.iso', DEST/'linuxPreGlibc25.iso')
