from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.module_utils.basic import AnsibleModule


DOCUMENTATION = '''
---
module: remove (may be do other things) salt key from uyuni-server/SuMa
short_description: Perform removing of salt-key 
author:
  - "Klaus Hildebrandt"
'''
import logging
#from operator import itemgetter
from ..module_utils.uyuni import UyuniAPIClient

def run_module():
    # define available arguments/parameters a user can pass to the module
    
    module_args = dict( **UyuniAPIClient.argument_spec(),
                        key =   dict(type='str', required=True),
                        state = dict(type='str', required=True, choices=['absent']),
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
    presentKeys = set(sum([api_instance.execute_api_call(f'saltkey.{listName}') for listName in ['deniedList', 'acceptedList'] ], start=[]))

    if module.params.get('state') == 'absent' and module.params.get('key') in presentKeys:
        api_instance.execute_api_call('saltkey.delete', module.params.get('key'))
        result['changed'] = True
        module.exit_json(**result)
     
    module.exit_json(**result)

def main():
    run_module()


if __name__ == '__main__':
    main()