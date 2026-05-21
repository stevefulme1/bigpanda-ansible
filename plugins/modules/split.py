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
  - This module splits a BigPanda incident into multiple incidents.
module: split
options:
  incident_id:
    description: The ID of the incident to split.
    required: true
    type: str
  comment:
    description: A comment describing the split.
    required: false
    type: str
  api_token:
    description: The API token for authentication.
    required: true
    type: str
  environment_id:
    description: The environment ID.
    required: true
    type: str
  alert_ids:
    description: A list of alert IDs to split.
    required: true
    type: list
    elements: str
short_description: Split a BigPanda incident into multiple incidents.
version_added: 1.0.0
"""

EXAMPLES = """
- name: Split incidents
  bigpanda.incident.split:
    incident_id: "source_incident"
    comment: "Splitting the incident."
    api_token: "your_api_token"
    environment_id: "your_environment"
    alert_ids:
      - "alert1"
      - "alert2"
"""

RETURN = """
changed:
  description: Indicates if the incident was successfully split.
  type: bool
  returned: true/false
  sample: true
result:
  description: The response from the BigPanda server.
  type: str
  returned: BigPanda's Response
  sample: "Incident split successfully."
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
            environment_id=dict(type='str', required=True),
            incident_id=dict(type='str', required=True),
            api_token=dict(type='str', required=True, no_log=True),
            comment=dict(type='str', required=False),
            alert_ids=dict(type='list', required=True, elements='str')
        ),
        supports_check_mode=True
    )

    if not HAS_REQUESTS:
        module.fail_json(msg="The requests Python library is required")

    environment_id = module.params['environment_id']
    incident_id = module.params['incident_id']
    api_token = module.params['api_token']
    alert_ids = module.params['alert_ids']
    comment = module.params['comment']

    try:
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
        }
        data = {
            'comment': comment,
            'alerts': alert_ids,
        }

        response = requests.post(
            f'https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents/{incident_id}/split',
            headers=headers,
            json=data)

        response.raise_for_status()
        module.exit_json(changed=True, result=response.text)
    except HTTPError as e:
        # Log any HTTP errors
        module.fail_json(msg=f"An HTTP error occurred: {str(e)}")


if __name__ == '__main__':
    main()
