# python 3 headers, required if submitting to Ansible
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: file
  author: Klaus Hildebrandt <klaus.hildebrandt@edeka.de>
  version_added: "0.1"  # for collections, use the collection version, not the Ansible version
  short_description: calls given function (1st terms parameter) with all given parameters without any transformation
  description:
       

  options:
    _terms:
      description: first parameter ist the api call. others are parameters for the call
      required: True
    uyuni_host:
      description:
            - Sample option that could modify plugin behavior.
            - This one can be set directly ``option1='x'`` or in ansible.cfg, but can also use vars or environment.
      type: string
      ini:
        - section: file_lookup
          key: option1
    uyuni_user:
    uyuni_password:
    uyuni_verify_ssl:

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
      #display.warning("type(terms): %s" % str(type(terms)))
      named_params = dict(use_datetime=True)
      if 'uyuni_verify_ssl' in kwargs:
         named_params['uyuni_verify_ssl'] = kwargs['uyuni_verify_ssl']

      api_instance = UyuniAPIClient(logging.ERROR, str(kwargs['uyuni_host']), str(kwargs['uyuni_user']), str(kwargs['uyuni_password']), **named_params)
      api_call = terms[0]
      api_call_parameters = api_call[1:]
          #display.warning("term: %s" % term)
      ret = [ api_instance.execute_api_call(terms[0], *api_call_parameters) 
            ]

      return ret