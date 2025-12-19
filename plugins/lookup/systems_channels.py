# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: file
  author: Klaus Hildebrandt <klaus.hildebrandt@edeka.de>
  version_added: "0.1"  # for collections, use the collection version, not the Ansible version
  short_description: retuern base and child channels assigned to given system (labels only)
  description:
      - This lookup returns base and child channels assigned to given system
  options:
    _terms:
      description: system name
      required: True
    uyuni_host:
      description:
            - Sample option that could modify plugin behavior.
            - This one can be set directly ``option1='x'`` or in ansible.cfg, but can also use vars or environment.
      type: string
    uyuni_user:

    uyuni_password:

  notes:
    - if read in variable context, the file can be interpreted as YAML if the content is valid to the parser.
    - this lookup does not understand globbing --- use the fileglob lookup instead.
"""
#from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

import logging

from ..module_utils.uyuni import UyuniAPIClient

display = Display()

class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
      ret = [] ## must be a list
      #display.warning("type(terms): %s" % str(type(terms)))
      api_instance = UyuniAPIClient(logging.ERROR, str(kwargs['uyuni_host']), str(kwargs['uyuni_user']), str(kwargs['uyuni_password']), use_datetime=True)
      for term in terms:
          #display.warning("term: %s" % term)
          systemID = api_instance.get_host_id(term)
          
          #ret.append(api_instance.execute_api_call('system.listInstalledPackages', systemID))
          ret.append( {
                        "base" : api_instance.execute_api_call('system.getSubscribedBaseChannel', systemID)['label'],
                        "children" : [ x['label'] for x in api_instance.execute_api_call('system.listSubscribedChildChannels', systemID) ]
                      }
                    )
      return ret