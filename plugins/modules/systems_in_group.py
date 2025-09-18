from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = '''
---
module: systems_in_group
short_description: manage system presence/absense of systems in group
description:
  - manage system presence/absense of systems in group
author:
  - "Klaus Hildebrandt"
'''

import ssl
from contextlib import contextmanager
from xmlrpc.client import ServerProxy
from operator import itemgetter
from ..module_utils.uyuni import UyuniAPIClient
import typing
import logging

def toDict(data : typing.List[typing.Dict], mainMember: str) -> typing.Dict[str, typing.Dict] :
    result = dict([  (x[mainMember], x) for x in data  ])
    return result


def run_module():
    module_args = dict( **UyuniAPIClient.argument_spec(),
                        systems = dict(type='list', elements=str, required=True, aliases=['minions']),
                        group_name   = dict(type='str', required=True),
                        state   = dict(type='str', required=True, choices=['present', 'absent']),
                    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        msg=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    ##create connection to uyni/SuMa
    api_instance = UyuniAPIClient(logging.ERROR,
                                  module.params.get('uyuni_host'),
                                  module.params.get('uyuni_user'),
                                  module.params.get('uyuni_password'),
                                  module.params.get('uyuni_port'),
                                  verify=module.params.get('uyuni_verify_ssl'),
                                  use_datetime=True,
                                 )
    
    currentSystemsInGroup = toDict(api_instance.execute_api_call('systemgroup.listSystems', module.params.get('group_name')), 'minion_id')
    if module.params.get('state') == 'present' :
        systems2add = set(module.params.get('systems')).difference(currentSystemsInGroup.keys())
        
        if len(systems2add) > 0 :
            allSystems = toDict(api_instance.get_all_hosts(), 'name')
        
            #  https://documentation.suse.com/suma/5.0/api/suse-manager/api/systemgroup.html#apidoc-systemgroup-addOrRemoveSystems-loggedInUser-systemGroupName-serverIds-add
            api_instance.execute_api_call('systemgroup.addOrRemoveSystems', module.params.get('group_name'), [allSystems[x]['id'] for x in systems2add], True)
            
            result['changed'] = True
            result['msg'] = f"systems {','.join(systems2add)} added to group={module.params.get('group_name')}"

            module.exit_json(**result)
    else: ## state must be absent!
        systems2remove = set(module.params.get('systems')).intersection(currentSystemsInGroup.keys())
        if len(systems2remove) > 0 :
            api_instance.execute_api_call('systemgroup.addOrRemoveSystems', module.params.get('group_name'), [currentSystemsInGroup[x]['id'] for x in systems2remove], False)
            
            result['changed'] = True
            result['msg'] = f"systems {','.join(systems2remove)} removed from group={module.params.get('group_name')}"

            module.exit_json(**result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()