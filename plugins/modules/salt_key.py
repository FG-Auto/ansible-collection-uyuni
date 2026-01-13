from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = '''
---
module: controls salt key in UYUNI (currently remove only)
short_description: Perform remove of salt_key 
author:
  - "Klaus Hildebrandt"
'''
import logging
#from operator import itemgetter
from ..module_utils.uyuni import UyuniAPIClient

def run_module():
    # define available arguments/parameters a user can pass to the module
    
    module_args = dict( **UyuniAPIClient.argument_spec(),
                        minion = dict(type='str', required=True),
                        state =  dict(type='str', required=True, choices=['absent']),
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
    minionID = module.params.get('minion')

    keys = sum(map(lambda x: api_instance.execute_api_call(f'saltkey.{x}'), ['acceptedList', 'rejectedList', 'deniedList', 'pendingList'] ), [])
    
    if minionID in keys :
        api_instance.execute_api_call('system.delete', minionID)
        result['changed'] = True
    else:
        result['changed'] = False

    module.exit_json(**result)

def main():
    run_module()


if __name__ == '__main__':
    main()