#!/usr/bin/python3.11
"""
Ansible Module to perform a full dist upgarde of host

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
short_description: Perform distribution upgarde of host
description:
  - Perform distribution upgrade (=update channels + 'zypper dup') of host
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
        target_channels=dict(type='list', required=True, elements='str'),  ## labels of channels
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    result = dict(
                  changed=False,
                  original_message='',
                  message=''
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
    actionID = api_instance.execute_api_call("system.scheduleDistUpgrade", systemID, 
                                                                           module.params.get('target_channels'),
                                                                           False, ## <- dryRun
                                                                           True,  ## <- allowVendorChange
                                                                           datetime.now(timezone.utc)

                                            )
    resWait = api_instance.wait_for_action(actionID, systemID)

    result['changed'] = True
    
    if resWait[0]['failed_count'] > 0:
        result['message'] = "distUpgrade failed"
        result['original_message'] = resWait[0]['result_msg']
    else :
        module.exit_json(**result)

if __name__ == '__main__':
    main()
