from bottle import route, run, template, get, delete, post, patch, request
from configobj import ConfigObj


if sys.version_info < (2, 7):
    sys.stderr.write('You need Python 2.7 or later\n')
    sys.exit(1)


@get('/api')
def api():
    return 'Donk API'


@get('/api/vms')
def get_vms():
    # tags
    # 200 or error
    return ''


@post('/api/vms')
def post_vms():
    return ''


@get('/api/vms/<id>')
def get_vms_id(id):
    return ''


@delete('/api/vms/<id>')
def del_vms_id(id):
    return ''


@get('/api/vms/power/<id>')
def get_vms_power_id(id):
    return ''


@patch('/api/vms/power/<id>')
def patch_vms_power_id(id):
    return ''


@get('/api/vms/<id>/folders')
def get_vms_folders_id(id):
    return ''


@patch('/api/vms/<id>/folders')
def patch_vms_id_folders(id):
    return ''


@post('/api/vms/<id>/folders')
def post_vms_id_folders_id(id):
    return ''


@get('/api/vms/<id>/folders/<folderid>')
def get_vms_id_folders_id(id, folderid):
    return ''


@patch('/api/vms/<id>/folders/<folderid>')
def patch_vms_id_folders_id(id, folderid):
    return ''


@delete('/api/vms/<id>/folders/<folderid>')
def delete_vms_id_folders_id(id, folderid):
    return ''


@get('/api/vms/<id>/getipaddress')
def get_vms_getipaddress(id):
    return ''

def main():
    # Read the config.ini file and validate parameters
    scriptpath = getstringpath()
    configfile = joinpath(scriptpath, 'config.ini')
    if not isfile(configfile):
        print 'PCM0001E: config.ini not found'
        sys.exit(1)

    config = ConfigObj(configfile)
    run(host='localhost', port=8080)

if __name__ == '__main__':
    main()