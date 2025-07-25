from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = '''
---
module: bootstrap
short_description: Perform bootstraping on minion via ssh (with password or private key)
description:
  -  Perform bootstraping on minion via ssh
author:
  - "Klaus Hildebrandt"
'''

import ssl
from contextlib import contextmanager
from xmlrpc.client import ServerProxy
#from operator import itemgetter
from ..module_utils.uyuni import UyuniAPIClient

@contextmanager
def SuMaConnection(sumaHost, sumaUser, sumaPwd):
    client = ServerProxy(f"https://{sumaHost}/rpc/api", context=ssl._create_unverified_context())
    key = client.auth.login(sumaUser, sumaPwd)
    try :
        yield (client, key)
    finally :
        client.auth.logout(key)

def run_module():
    # define available arguments/parameters a user can pass to the module
    
    module_args = dict( **UyuniAPIClient.argument_spec(),
                        minion =   dict(type='str', required=True),
                        minionUser = dict(type='str', required=False, default='root'),
                        minionPort = dict(type='int', required=False, default=22),
                        ## exact one of minionPwd/minionPrivKey must be given
                        minionPwd = dict(type='str', required=False, default=None, no_log=True),
                        minionPrivKey = dict(type='str', required=False, description="un-encrypted private key", default=None),
                        activationKey = dict(type='str', required=True),
                        force         = dict(type='bool', required=False, default=False),
                    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[('minionPwd', 'minionPrivKey')],
        required_one_of =  [('minionPwd', 'minionPrivKey')],
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    ##create connection to uyni/SuMa
    with SuMaConnection(sumaHost=module.params['uyuni_host'], sumaUser=module.params['uyuni_user'], sumaPwd=module.params['uyuni_password']) as (client, key):
        ## check if minion already registred
        allMinions = dict([ (x['name'], x) for x in client.system.listSystems(key)])
        if module.params['minion'] in allMinions:
            if module.params['force']:
                client.system.deleteSystem(key, allMinions[module.params['minion']]['id'], 'FORCE_DELETE')
            else:
                # todo: warning??
                # module.fail_json(msg=f"minion={module.params['minion']} is already registred", **result)
                result['changed'] = False
                result['message'] = f"minion={module.params['minion']} is already registred"
                module.exit_json(**result)
        
        ## bootstrap
        if module.params['minionPwd'] is not None:
            client.system.bootstrap(key, module.params['minion'], module.params['minionPort'], module.params['minionUser'], module.params['minionPwd'], module.params['activationKey'], False) #last param is sshSalt => true/false
        else:
            client.system.bootstrapWithPrivateSshKey(key, module.params['minion'], module.params['minionPort'], module.params['minionUser'], module.params['minionPrivKey'], '', module.params['activationKey'], False) #last param is sshSalt => true/false

        result['changed'] = True

        module.exit_json(**result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()