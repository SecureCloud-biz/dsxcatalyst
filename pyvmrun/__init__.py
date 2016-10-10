"""
The MIT License (MIT)

Copyright (c) 2016 Dave Parsons

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import os
import subprocess
from _winreg import *


def file_must_exist(type, file):
    if not os.path.isfile(file):
        raise ValueError("{0} at path {1} does not exist".format(type, file))


def file_must_not_exist(type, file):
    if os.path.isfile(file):
        raise ValueError("{0} at path {1} already exists".format(type, file))


def get_abspath(path):
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    return path


class VMRunException(Exception):
    pass


class VMRunCLI(object):

    def __init__(self, vmrun_path=None):
        if not vmrun_path:
            reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
            key = OpenKey(reg, r'SOFTWARE\Wow6432Node\VMware, Inc.\VMware Workstation')
            vmrun = QueryValueEx(key, 'InstallPath')[0]
            vmrun += 'vmrun.exe'
        else:
            vmrun = vmrun_path

        if not os.path.isfile(vmrun):
            raise ValueError("vmrun tool not found at path {0}".format(vmrun))

        self.tool_path = vmrun

    def __vmrun(self, command):
        base = [self.tool_path, '-T', 'ws']
        base.extend(command)

        proc = subprocess.Popen(base, stdout=subprocess.PIPE)
        stdout = proc.stdout.readlines()

        if len(stdout) and stdout[0].startswith('Error'):
            raise VMRunException(stdout[0])

        return stdout

    def list(self):
        output = self.__vmrun(['list'])

        # Expected output:
        # Total running VMs: N
        # [optional absolute path to VMX 1]
        # [optional absolute path to VMX 2]
        # [optional absolute path to VMX n]
        data = dict()
        data['count'] = int(output[0].split(':')[1].strip())
        data['machines'] = [vmx.strip() for vmx in output[1:]]

        return data

    def start(self, vmx, gui=True):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        gui_value = ('nogui', 'gui')[gui]
        self.__vmrun(['start', vmx, gui_value])

    def stop(self, vmx, soft=True):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        soft_value = ('hard', 'soft')[soft]
        self.__vmrun(['stop', vmx, soft_value])

    def reset(self, vmx, soft=True):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        soft_value = ('hard', 'soft')[soft]
        self.__vmrun(['reset', vmx, soft_value])

    def suspend(self, vmx, soft=True):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        soft_value = ('hard', 'soft')[soft]
        self.__vmrun(['suspend', vmx, soft_value])

    def pause(self, vmx):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['pause', vmx])

    def unpause(self, vmx):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['unpause', vmx])

    def delete(self, vmx):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['deleteVM', vmx])

    def list_snapshots(self, vmx):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        output = self.__vmrun(['listSnapshots', vmx])
        snapshots = [s.strip() for s in output[1:]] 
        data = {'count': len(snapshots), 'snapshots': snapshots}

        return data

    def snapshot(self, vmx, name):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['snapshot', vmx, name])

    def revert_to_snapshot(self, vmx, name):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['revertToSnapshot', vmx, name])

    def delete_snapshot(self, vmx, name):
        vmx = get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['deleteSnapshot', vmx, name])

    def clone(self, vmx, destvmx, type, snapshot=None, clonename=None):
        vmx= get_abspath(vmx)

        file_must_exist('VMX', vmx)

        self.__vmrun(['clone', vmx, destvmx, type, snapshot, clonename])


class VM(object):
    """
    A virtual machine.
    """
    def __init__(self, vmx):
        self.vmx = get_abspath(vmx)
        file_must_exist('VMX', self.vmx)
        self.vmrun = VMRunCLI()

    def start(self, gui=True):
        return self.vmrun.start(self.vmx, gui)

    def stop(self, soft=True):
        return self.vmrun.stop(self.vmx, soft)

    def reset(self, soft=True):
        return self.vmrun.reset(self.vmx, soft)

    def suspend(self, soft=True):
        return self.vmrun.suspend(self.vmx, soft)

    def pause(self):
        return self.vmrun.pause(self.vmx)

    def unpause(self):
        return self.vmrun.unpause(self.vmx)

    def delete(self):
        return self.vmrun.delete(self.vmx)

    def list_snapshots(self):
        return self.vmrun.list_snapshots(self.vmx)

    def snapshot(self, name):
        return self.vmrun.snapshot(self.vmx, name)

    def revert_to_snapshot(self, name):
        return self.vmrun.revert_to_snapshot(self.vmx, name)

    def delete_snapshot(self, name):
        return self.vmrun.delete_snapshot(self.vmx, name)


# Default access
vmrun = VMRunCLI()
