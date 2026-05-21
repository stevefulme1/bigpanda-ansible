#!/usr/bin/python
# Copyright 2023 BigPanda
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

DOCUMENTATION = """
author:
  - Juan Cardozo (@JuanDCardozo)
description:
  - This module resolves a BigPanda incident by providing the incident ID and an optional resolution message.
module: resolve
options:
  incident_id:
    description: The ID of the incident to resolve.
    required: true
    type: str
  resolution_comment:
    description: The resolution message for the incident.
    required: false
    type: str
  api_token:
    description: The API token for authentication.
    required: true
    type: str
  environment_id:
    description: The ID of the environment.
    required: true
    type: str
short_description: Resolve a BigPanda incident.
version_added: 1.0.0
"""

EXAMPLES = """
- name: Resolve an incident
  bigpanda.incident.resolve:
    incident_id: "12345"
    resolution_comment: "Incident resolved."
    api_token: "your_api_token"
    environment_id: "your_environment_id"
"""

RETURN = """
changed:
  description: Indicates if the incident resolution was successful.
  type: bool
  returned: true/false
  sample: true
result:
  description: The response from the BigPanda server.
  type: str
  returned: BigPanda's Response
  sample: "Incident resolved successfully."
"""

from ansible.module_utils.basic import AnsibleModule
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            resolution_comment=dict(type='str', required=False),
            environment_id=dict(type='str', required=True),
            incident_id=dict(type='str', required=True),
            api_token=dict(type='str', required=True, no_log=True),
        ),
        supports_check_mode=True
    )

    if not HAS_REQUESTS:
        module.fail_json(msg="The requests Python library is required")

    resolution_comment = module.params['resolution_comment']
    environment_id = module.params['environment_id']
    incident_id = module.params['incident_id']
    api_token = module.params['api_token']

    module.debug("Resolve Incident")

    # Set the request headers
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }

    # Prepare the JSON data to be sent with the request
    json_data = {
        'comments': resolution_comment
    }

    try:
        response = requests.post(
            f'https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents/{incident_id}/resolve',
            headers=headers,
            json=json_data)

        response.raise_for_status()
        module.exit_json(changed=True, result=response.text)
    except HTTPError as e:
        # Log any HTTP errors
        module.fail_json(msg=f"An HTTP error occurred: {str(e)}")


if __name__ == '__main__':
    main()
