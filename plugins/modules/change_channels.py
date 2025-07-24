#!/usr/bin/python3.11
"""
Ansible Module to perform a change of channels on target host

2025 Klaus Hildebrandt

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import (absolute_import, division, print_function, annotations)
__metaclass__ = type

DOCUMENTATION = '''
---
module: dist_upgrade
short_description: Perform channel exchange on host
description:
  - Perform channel change on host
author:
  - "Klaus Hildebrandt"
'''
import logging
from ansible.module_utils.basic import AnsibleModule
from datetime import datetime, timezone

from ..module_utils.uyuni import UyuniAPIClient

def main():
    """
    Main functions
    """
    argument_spec = dict(
        uyuni_host=dict(type='str', required=True),
        uyuni_user=dict(type='str', required=True),
        uyuni_password=dict(type='str', required=True, no_log=True),
        uyuni_port=dict(default=443, type='int'),
        uyuni_verify_ssl=dict(default=True, type='bool'),
        name=dict(type='str', required=True),
        #target_channels=dict(type='list', required=True, elements='str'),  ## labels of channels
        target_channels=dict(type='dict', required=True, options=dict(base     = dict(type='str', required=True),                  ## label of base channel
                                                                      children = dict(type='list', required=True, elements='str'), ## labels of child channels
                                                                     ),
                            ),
                         )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    result = dict(
                  changed=False,
                  original_message='',
                  msg=''
                 )

    if module.check_mode:
         module.exit_json(**result)

    api_instance = UyuniAPIClient(logging.ERROR,
                                  module.params.get('uyuni_host'),
                                  module.params.get('uyuni_user'),
                                  module.params.get('uyuni_password'),
                                  module.params.get('uyuni_port'),
                                  verify=module.params.get('uyuni_verify_ssl'),
                                  use_datetime=True,
                                 )

    systemID = api_instance.get_host_id(module.params.get('name'))
    actionID = api_instance.execute_api_call("system.scheduleChangeChannels", systemID, 
                                                                              module.params['target_channels']['base'],
                                                                              module.params['target_channels']['children'],
                                                                              datetime.now(timezone.utc)
                                            )
    resWait = api_instance.wait_for_action(actionID, systemID, interval=3)

    result['changed'] = True
    
    if resWait[0]['failed_count'] > 0:
        result['msg'] = "ChangeChannels failed"
        result['original_message'] = resWait[0]['result_msg']
        module.fail_json(**result)
    else :
        module.exit_json(**result)

if __name__ == '__main__':
    main()
