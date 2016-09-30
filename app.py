from __future__ import print_function
import json
import os
import subprocess
import sys
from bottle import route, run, template, get, delete, post, patch, request, response, static_file
from configobj import ConfigObj

__author__ = 'Dave Parsons'
__version__ = '1.0.0'
__license__ = 'MIT'

if sys.version_info < (2, 7):
    sys.stderr.write('You need Python 2.7 or later\n')
    sys.exit(1)


def getstringpath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def isfile(filename):
    return os.path.isfile(filename)


def isfolder(foldername):
    return os.path.isdir(foldername)


def isVMX(id):
    if isfile(names[id]):
        code = 200
        output = ''
    else:
        code = 500
        output = '{"code": 500, "message": "lstat : no such file or directory"}'
    return code, output


def joinpath(folder, file):
    return os.path.join(folder, file)


def runcmd(cmd):

    # vmrun does not return any exit codes and all errors are in stdout!
    proc = subprocess.Popen(config['VMRUN'] + config['VMTYPE'] + cmd, shell=True, stdout=subprocess.PIPE)
    stdout = proc.stdout.readlines()

    if any("Error" in s for s in stdout):
        code = 500
    else:
        code = 200

    if len(stdout) > 0:
        output = ''.join(str(l) for l in stdout)
    else:
        output = ''

    return code, output


@get('/api')
def api():

    # Return the config details (appcatalyst.conf)
    return config


@get('/api/vms')
def get_vms():

    # Return the names dict keys in non-JSON text form:
    # ["photon1", "photons2", ...]
    # Ignore the "tags" parameters as not used in AppCatalyst previews
    output = "["
    for key in names.iterkeys():
        output = output + '"' + key + '",'
    output = output[:-1] + ']'
    response.body = output
    response.content_type = 'text/plain; charset=utf-8'
    response.status = 200
    return response


@post('/api/vms')
def post_vms():

    # Create a new cloned VM from default or specified source
    body = json.load(request.body)

    if 'id' in body:
        destvmx = joinpath(joinpath(config['DEFAULT_VM_PATH'], body["id"]), body["id"] + '.vmx')
    else:
        response.body = '{"code": 500, "message": "EOF"}'
        response.body = 500

    if 'parentId' in body:
        srcvmx = joinpath(joinpath(config['DEFAULT_VM_PATH'], body["parentId"]), body["parentId"] + '.vmx')
    else:
        srcvmx = config['DEFAULT_PARENT_VM_PATH']

    print('clone ' + srcvmx + ' ' + destvmx + ' full')

    # Run the command
    code, output = runcmd('clone ' + srcvmx + ' ' + destvmx + ' full')

    # Check reposnse code from the vmrun procedure & return to caller
    if code == 200:
        if 'parentId' in body:
            response.body = '{"id": "' + body["id"] + '", "parentId": "' + body["parentId"] + '", "name": "", "tag": "", "sourceReference": ""}'
        else:
            response.body = '{"id": "' + body["id"] + '", "parentId": "", "name": "", "tag": "", "sourceReference": ""}'
        response.code = code
    elif code == 500:
        response.body = '{"code": 500, "message": "' + message + '"}'
        response.code = code
    else:
        pass

    response.content_type = 'application/json; charset=utf-8'
    return response


@get('/api/vms/<id>')
def get_vms_id(id):

    # Check id is valid
    code, message = isVMX(id)
    if code == 200:
        if vms:
            for key, value in vms.iteritems():
                if id == key:
                    output =  '{"id": "' + key + '", "name": "' + vms[key]['displayname'] + '", "tag": ""}'
                response.status = 200
        else:
            output = '{}'
            response.status = 500
        response.body = output
    elif code == 500:
        response.status = code
        response.body = message
    else:
        pass

    response.content_type = 'application/json; charset=utf-8'
    return response


@delete('/api/vms/<id>')
def del_vms_id(id):

    # Check id is valid
    code, message = isVMX(id)
    if code == 200:

        # Delete the VM from inventory
        runcmd('deleteVM ' + names[id])
        if code == 200:
            response.code = 204
        elif code == 500:
            response.body = '{"code": 500, "message": "' + message + '"}'
            response.code == code
        else:
            pass

    elif code == 500:
        response.status = code
        response.body = message

    else:
        pass

    response.content_type = 'application/json; charset=utf-8'
    return response


@get('/api/vms/power/<id>')
def get_vms_power_id(id):

    # Check id is valid
    code, message = isVMX(id)
    if code == 200:
        # List the running VMs and see if id is one of them
        code, message = runcmd('list')
        if code == 200:
            if id in message:
                response.body = '{"code": 200, "message": "powered on"}'
            else:
                response.body = '{"code": 200, "message": "powered off"}'
            response.code = code
        elif code == 500:
            response.body = '{"code": 500, "message": "' + message + '"}'
            response.code == code

        else:
            pass

    elif code == 500:
        response.status = code
        response.body = message

    else:
        pass

    response.content_type = 'application/json; charset=utf-8'
    return response


@patch('/api/vms/power/<id>')
def patch_vms_power_id(id):

    # Power operations for the VM
    body = request.body.read()
    if body == 'on':
        powerop = 'start'
        powersubop = ''
        json = '{"code": 200, "message": "The VM is powered on."}'
    elif body == 'off':
        powerop = 'stop'
        powersubop = 'hard'
        json = '{"code": 200, "message": "The VM is powered off."}'
    elif body == 'shutdown':
        powerop = 'stop'
        powersubop = 'soft'
        json = '{"code": 200, "message": "The VM is shut down."}'
    elif body == 'suspend':
        powerop = 'suspend'
        powersubop = ''
        json = '{"code": 200, "message": "The VM is suspended."}'
    elif body == 'pause':
        powerop = 'pause'
        powersubop = ''
        json = '{"code": 200, "message": "The VM is paused."}'
    elif body == 'unpause':
        powerop = 'unpause'
        powersubop = ''
        json = '{"code": 200, "message": "The VM is unpaused."}'
    else:
        json = '{"code": 500, "message": "The op name is not supported."}'

    # Check id is valid
    if code == 200:

        # Run the command
        code, output = runcmd(powerop + ' ' + names[id] + ' ' + powersubop)

        # Check reposnse code from the vmrun procedure & return to caller
        if code == 200:
            response.body = json
        elif code == 500:
            response.body = '{"code": 500, "message": "VIX Error: The virtual machine needs to be powered on, code: 3006, ' \
                            'operation: vm.' + powerop + '"}'
        else:
            pass

    elif code == 500:
        response.body = message
    else:
        pass

    response.content_type = 'application/json; charset=utf-8'
    response.status = code
    return response


@get('/api/vms/<id>/folders')
def get_vms_folders_id(id):
    # TO DO: Implement function
    # Check id is valid
    code, message = isVMX(id)
    if code == 200:
        # Not sure how o get shared folders here!!!
        pass
    elif code == 500:
        response.status = code
        response.body = message
    else:
        pass
    return response


@patch('/api/vms/<id>/folders')
def patch_vms_id_folders(id):
    # TO DO: Implement function
    # Check id is valid
    code, message = isVMX(id)
    if code == 200:
        pass
    elif code == 500:
        response.status = code
        response.body = message
    else:
        pass
    return response


@post('/api/vms/<id>/folders')
def post_vms_id_folders_id(id):
    # TO DO: Implement function
    # Check id is valid
    code, message = isVMX(id)
    if code == 200:
        # Enable/disable shared folders
        # enableSharedFolders
        # disableSharedFolder
        pass
    elif code == 500:
        response.status = code
        response.body = message
    else:
        pass
    return response


@get('/api/vms/<id>/folders/<folderid>')
def get_vms_id_folders_id(id, folderid):
    # TO DO: Implement function
    # Check id is valid
    code, message = isVMX(id)
    if code == 200:
        pass
    elif code == 500:
        response.status = code
        response.body = message
    else:
        pass
    return response


@patch('/api/vms/<id>/folders/<folderid>')
def patch_vms_id_folders_id(id, folderid):
    # TO DO: Implement function
    # Check id is valid
    code, message = isVMX(id)
    if code == 200:
        pass
    elif code == 500:
        response.status = code
        response.body = message
    else:
        pass
    return response


@delete('/api/vms/<id>/folders/<folderid>')
def delete_vms_id_folders_id(id, folderid):
    # TO DO: Implement function
    # Check id is valid
    code, message = isVMX(id)
    if code == 200:
        pass
    elif code == 500:
        response.status = code
        response.body = message
    else:
        pass
    return response


@get('/api/vms/<id>/ipaddress')
def get_vms_getipaddress(id):

    # Check id is valid
    code, output = isVMX(id)
    if code == 200:

        # Run the command
        code, output = runcmd('getGuestIPAddress ' + names[id] + ' wait')

        # Check reposnse code from the vmrun procedure & return to caller
        if code == 200:
            response.body = '{"code": 200, "message": "' + output + '"}'
        elif code == 500:
            response.body = '{"code": 500, "message": ' + output + '"}'
        else:
            pass

    elif code == 500:
        response.body = message
    else:
        pass

    response.content_type = 'application/json; charset=utf-8'
    response.status = code
    return response


@get('/json/<filepath:path>')
def server_static(filepath):
    # Return the original swagger.json as used by Vagrant plugin
    return static_file(filepath, root='./json')


def main():
    # Read the appcatalyst.conf file and validate parameters
    scriptpath = getstringpath()
    configfile = joinpath(scriptpath, 'appcatalyst.conf')
    if not isfile(configfile):
        print('appcatalyst.conf not found')
        sys.exit(1)
    global config
    config = ConfigObj(configfile)
    global default_vm_path
    default_vm_path = config['DEFAULT_VM_PATH'];

    # Get the VMs from the default folder
    global names
    global vms
    names = {}
    vms = {}

    # TO DO: Need more robust code here to trap invalid folders/files
    # Walk top-level folders only - no nested folders allowed
    for dirs in os.walk(default_vm_path).next()[1]:
        vmfolder = joinpath(default_vm_path, dirs)
        # Find VMX file it the currently folder
        for file in os.listdir(vmfolder):
            if file.endswith('.vmx'):
                # Found VMX file so add to the 2 dicts:
                # names - folder name --> vmx file path
                # vms   - folder name --> vmx file contents
                vmxfile = (joinpath(vmfolder, file))
                names[dirs] = vmxfile
                vmx = ConfigObj(vmxfile)
                vms[dirs] = vmx
    print(names)

    # Start development server on all IPs and using configured port
    run(host = '0.0.0.0', port = config['PORT'])


if __name__ == '__main__':
    main()