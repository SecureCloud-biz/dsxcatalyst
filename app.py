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

from __future__ import print_function
import json
import os
import platform
import subprocess
import sys
from bottle import route, run, template, get, delete, post, patch, request, response, static_file, error
from configobj import ConfigObj

__author__ = 'Dave Parsons'
__version__ = '1.0.0'
__license__ = 'MIT'

VIX_SHAREDFOLDER_WRITE_ACCESS = 4

if sys.version_info < (2, 7):
    sys.stderr.write('You need Python 2.7 or later\n')
    sys.exit(1)


def getstringpath():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


def isfile(filename):
    return os.path.isfile(filename)


def isfolder(foldername):
    return os.path.isdir(foldername)


def joinpath(folder, file):
    return os.path.join(folder, file)


def runcmd(cmd, strip=True):

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

    if strip:
        output = output.replace('\n', '').replace('\r', '')
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
    elif 'sourceReference' in body:
        srcvmx = body['sourceReference']
    else:
        srcvmx = config['DEFAULT_PARENT_VM_PATH']

    # Run the command
    code, output = runcmd('clone ' + srcvmx + ' ' + destvmx + ' full')

    # Check response code from the vmrun procedure & return to caller
    if code == 200:
        if 'parentId' in body:
            response.body = '{"id": "' + body["id"] + \
                            '", "parentId": "' + body["parentId"] + '", "name": "", "tag": "", "sourceReference": ""}'
        elif 'sourceReference' in body:
            response.body = '{"id": "' + body["id"] + \
                            '", "parentId": "", "name": "", "tag": "", "sourceReference": "' + \
                            body['sourceReference'] + '"}'
        else:
            response.body = '{"id": "' + body["id"] + \
                            '", "parentId": "", "name": "", "tag": "", "sourceReference": ""}'

        names[body['id']] = destvmx
        vmx = ConfigObj(destvmx)
        vms[body['id']] = vmx
        with open('vmInventory', 'w') as f:
            json.dump(names, f)
        response.status = code
    elif code == 500:
        response.body = '{"code": 500, "message": "' + message + '"}'
        response.status = code
    else:
        pass

    response.content_type = 'application/json; charset=utf-8'
    return response


@get('/api/vms/<id>')
def get_vms_id(id):

    # Check id is valid
    # TODO: What if VM is not present?
    if vms:
        for key, value in vms.iteritems():
            if id == key:
                output =  '{"id": "' + key + '", "name": "' + vms[key]['displayname'] + '", "tag": ""}'
            response.status = 200
    else:
        output = '{}'
        response.status = 500

    response.body = output
    response.content_type = 'application/json; charset=utf-8'
    return response


@delete('/api/vms/<id>')
def del_vms_id(id):

    # Delete the VM from inventory
    code, output = runcmd('stop ' + names[id] + ' hard')
    code, output = runcmd('deleteVM ' + names[id])
    if code == 200:
        response.status = 204
    elif code == 500:
        response.body = '{"code": 500, "message": "' + output + '"}'
        response.status == code
    else:
        pass

    # Remove the relevant dict entries
    if id in names:
        del names[id]
        del vms[id]

    with open('vmInventory', 'w') as f:
        json.dump(names, f)

    response.content_type = 'application/json; charset=utf-8'
    return response


@get('/api/vms/power/<id>')
def get_vms_power_id(id):

    # List the running VMs and see if id is one of them
    code, message = runcmd('list')
    if code == 200:
        if id in message:
            response.body = '{"code": 200, "message": "powered on"}'
        else:
            response.body = '{"code": 200, "message": "powered off"}'
        response.status = code
    elif code == 500:
        response.body = '{"code": 500, "message": "' + message + '"}'
        response.status == code
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
        powersubop = 'nogui'
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

    # Run the command
    code, output = runcmd(powerop + ' ' + names[id] + ' ' + powersubop)

    # Check response code from the vmrun procedure & return to caller
    if code == 200:
        response.body = json
    elif code == 500:
        response.body = '{"code": 500, "message": "VIX Error: The virtual machine needs to be powered on, code: 3006, ' \
                        'operation: vm.' + powerop + '"}'
    else:
        pass

    response.content_type = 'application/json; charset=utf-8'
    response.status = code
    return response


@get('/api/vms/<id>/folders')
def get_vms_folders_id(id):
    # Retrieve shared folders
    code, output  = runcmd('readVariable ' + names[id] + ' runtimeConfig sharedFolder.maxNum')

    # Check response code from the vmrun procedure & return to caller
    if code == 200:
        # Iterate through guestName variables
        body = "["
        if output:
            j = int(output)
            for i in range(0, j):
                code, output = runcmd('readVariable ' + names[id] + ' runtimeConfig sharedFolder' + str(i) + '.guestName')
                body = body + output + ','
        if len(body) > 1:
            body = body[:-1]
        body = body + ']'
        response.body = body
        response.content_type = 'text/plain; charset=utf-8'
    elif code == 500:
        response.body = '{"code": 500, "message": ' + output + '"}'
        response.content_type = 'application/json; charset=utf-8'
    else:
        pass

    response.status = 200
    return response


@patch('/api/vms/<id>/folders')
def patch_vms_id_folders(id):

    # Toggle shared folders on/off
    body = request.body.read()
    if body == 'true':
        folderop = 'enableSharedFolders '
    elif body == 'false':
        folderop = 'disableSharedFolders '
    else:
        json = '{"code": 500, "message": "The op name is not supported."}'

    # Run the command
    code, output = runcmd(folderop + names[id])

    # Check response code from the vmrun procedure & return to caller
    if code == 200:
        response.body = '{"code": 200, "message": "' + body + '"}'
    elif code == 500:
        response.body = '{"code": 500, "message": ' + message + '"}'
    else:
        pass

    response.content_type = 'application/json; charset=utf-8'
    response.status = code
    return response


@post('/api/vms/<id>/folders')
def post_vms_id_folders_id(id):
    # Add a new shared folder
    body = json.load(request.body)
    if {'guestPath', 'hostPath', 'flags'} == set(body):

        # Run the command
        code, output = runcmd('addSharedFolder ' + names[id] + ' ' + body['guestPath'] + ' ' + body['hostPath'])

        # Check response code from the vmrun procedure & return to caller
        if code == 200:
            response.body = '{"guestPath": "' + body['guestPath'] + '", "hostPath": "' + body['hostPath'] + '", "flags": 4}'
        elif code == 500:
            response.body = '{"code": 500, "message": ' + output + '"}'
        else:
            pass
        response.status = code
    else:
        response.body = '{"code": 500, "message": "EOF"}'
        response.status = 500

    response.content_type = 'application/json; charset=utf-8'
    return response


@get('/api/vms/<id>/folders/<folderid>')
def get_vms_id_folders_id(id, folderid):
    # Retrieve shared folders
    code, output  = runcmd('readVariable ' + names[id] + ' runtimeConfig sharedFolder.maxNum')

    # Check response code from the vmrun procedure & return to caller
    if code == 200:
        # Iterate through guestName variables
        if output:
            for i in range(0, j):
                code, guestPath = runcmd('readVariable ' + names[id] + ' runtimeConfig sharedFolder' + str(i) + '.guestName')
                if guestPath == folderid:
                    code, hostPath = runcmd('readVariable ' + names[id] + ' runtimeConfig sharedFolder' + str(i) + '.hostPath')
                    response.body = '{"guestPath": "' + folderid + '", "hostPath": "' + hostPath + '", "flags": 4}'
    elif code == 500:
        response.body = '{"code": 500, "message": ' + message + '"}'
    else:
        pass

    response.content_type = 'application/json; charset=utf-8'
    response.status = 200
    return response


@patch('/api/vms/<id>/folders/<folderid>')
def patch_vms_id_folders_id(id, folderid):
    # Modify a shared folder
    body = json.load(request.body)
    if {'guestPath', 'hostPath', 'flags'} == set(body):

        # Run the command
        code, output = runcmd('setSharedFolderState ' + names[id] + ' ' + body['guestPath']
                              + ' ' + body['hostPath'] + ' writeable')

        # Check response code from the vmrun procedure & return to caller
        if code == 200:
            response.body = '{"guestPath": "' + body['guestPath'] + '", "hostPath": "' + body['hostPath'] + '", "flags": 4}'
        elif code == 500:
            response.body = '{"code": 500, "message": ' + message + '"}'
        else:
            pass
        response.status = code
    else:
        response.body = '{"code": 500, "message": "EOF"}'
        response.status = 500

    response.content_type = 'application/json; charset=utf-8'
    return response



@delete('/api/vms/<id>/folders/<folderid>')
def delete_vms_id_folders_id(id, folderid):
    # Delete a shared folder

    # Run the command
    code, output = runcmd('removeSharedFolder ' + names[id] + ' ' + folderid)

    # Check response code from the vmrun procedure & return to caller
    if code == 200:
        code = 204
    elif code == 500:
        response.body = '{"code": 500, "message": ' + message + '"}'
    else:
        pass

    response.status = code
    response.content_type = 'application/json; charset=utf-8'
    return response


@get('/api/vms/<id>/ipaddress')
def get_vms_getipaddress(id):

    # Run the command
    code, output = runcmd('getGuestIPAddress ' + names[id] + ' -wait')

    # Check response code from the vmrun procedure & return to caller
    if code == 200:
        response.body = '{"code": 200, "message": "' + output + '"}'
    elif code == 500:
        response.body = '{"code": 500, "message": ' + output + '"}'
    else:
        pass

    response.content_type = 'application/json; charset=utf-8'
    response.status = code
    return response


@get('/json/<filepath:path>')
def server_static(filepath):
    # Return the original swagger.json as used by Vagrant plugin
    return static_file(filepath, root='./json')


@error(500)
def error500(error):
    # Pass back any 500 Internal Server Errors in JSON and not HTML format
    response.status = 500
    response.body = '{"code": 500, "message": "' + error.traceback.splitlines()[-1] + '"}'
    response.content_type = 'application/json; charset=utf-8'
    return response


def main():

    # Read the appcatalyst.conf file and validate parameters
    scriptpath = getstringpath()
    configfile = joinpath(scriptpath, 'appcatalyst.conf')
    if not isfile(configfile):
        print('AppCatalyst - appcatalyst.conf not found')
        sys.exit(1)
    global config
    config = ConfigObj(configfile)
    global default_vm_path
    default_vm_path = config['DEFAULT_VM_PATH'];

    # Get the VMs from the inventory
    global names
    global vms
    names = {}
    vms = {}

    with open('vmInventory', 'r') as f:
        names = json.load(f)

    # Found VMX file so ensure the 2 dicts:
    # names - folder name --> vmx file path
    # vms   - folder name --> vmx file contents
    print('AppCatalyst - discovered vms:')
    for name, vmxfile in names.items():
        print(name, vmxfile)
        if isfile(vmxfile):
            # Read and add guest VMX file to dict
            vmx = ConfigObj(vmxfile)
            vms[vmxfile] = vmx
            # for k, v in vmx.items():
            #     print(k + ' = "'+ v + '"')
        else:
            # Remove any missing guests
            del names[id]

    # Start development server on all IPs and using configured port
    try:
        run(host='0.0.0.0', port=config['PORT'], debug=True)
    finally:
        with open('vmInventory', 'w') as f:
            json.dump(names, f)


if __name__ == '__main__':
    main()