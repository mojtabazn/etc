#
# Copyright 2009,2018 VMware, Inc.  All rights reserved. -- VMware Confidential
#

"""
VMware Tools ISO Component.

This is the VMIS template component file for the winPre2k Tools ISO, where
winPre2k will be replaced by the name of the specific iso (ie: linux,
windows, freebsd...)
"""
DEST = LIBDIR/'vmware/isoimages'

class ToolsISOwinPre2k(Installer):
   def InitializeInstall(self, old, new, upgrade):
      self.AddTarget('File', 'winPre2k.iso', DEST/'winPre2k.iso')
