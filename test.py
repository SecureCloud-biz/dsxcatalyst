from __future__ import print_function
from configobj import ConfigObj
import subprocess

global config
config = ConfigObj('appcatalyst.conf')


def runcmd(cmd):

    proc = subprocess.Popen(config['VMRUN'] + config['VMTYPE'] + cmd, shell=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout = proc.stdout.readlines()
    stderr = proc.stderr.readlines()
    returncode = proc.returncode
    if len(stdout) > 0:
        print('stdout: ' + ''.join(str(l) for l in stdout))
    if len(stdout) > 0:
        print('stderr: ' + ''.join(str(l) for l in stderr))
    return


def main():
    dict = {}
    for key in dict.iterkeys():
        print(key)
    # runcmd('start /Users/i049299/vmimages/osx1011/osx1011.vmx')
    # runcmd('stop /Users/i049299/vmimages/osx1011/osx1011.vmx soft')


if __name__ == '__main__':
    main()
