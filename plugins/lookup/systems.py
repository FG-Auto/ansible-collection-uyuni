# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: file
  author: Klaus Hildebrandt <klaus.hildebrandt@edeka.de>
  version_added: "0.1"  # for collections, use the collection version, not the Ansible version
  short_description: return present systems on SuSEManager/UYINI-Server
  description:
      - This lookup returns present systems on SuSEManager/UYINI-Server
  options:
    _terms:
      - any dummy placeholder must be given
    uyuni_host:
      description:
            - Sample option that could modify plugin behavior.
            - This one can be set directly ``option1='x'`` or in ansible.cfg, but can also use vars or environment.
      type: string
    uyuni_user:

    uyuni_password:

    datetime_fmt:
      description: 
        - how datetime objects should be converted to string. use fromats from python datetime strftime. default='%Y-%m-%dT%H:%M:%S'
      type: string

  notes:
    - if read in variable context, the file can be interpreted as YAML if the content is valid to the parser.
    - this lookup does not understand globbing --- use the fileglob lookup instead.
"""
#from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
from datetime import datetime
import typing
import logging

from ..module_utils.uyuni import UyuniAPIClient

display = Display()

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        ret = []
        #display.warning("type(terms): %s" % str(type(terms)))
        api_instance = UyuniAPIClient(logging.ERROR, str(kwargs['uyuni_host']), str(kwargs['uyuni_user']), str(kwargs['uyuni_password']), use_datetime=True)
        result = api_instance.execute_api_call('system.listSystems')
        
        dt_fmt = kwargs.get('datetime_fmt', '%Y-%m-%dT%H:%M:%S')

        def transformMinionEntry(minionEntry : typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
            ## remove id attrubute to hide internals
            ## convert timestamps to isotime strings
            return dict([ (k, v.strftime(dt_fmt) if isinstance(v, datetime) else v) for k , v in minionEntry.items() if k not in ['id']] )

        result = list(map(transformMinionEntry, result))
        
        return result
