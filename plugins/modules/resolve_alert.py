#!/usr/bin/python
# Copyright 2023 BigPanda
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
author:
  - Juan Cardozo (@JuanDCardozo)
description:
  - This module resolves a BigPanda alert by providing the alert ID and an optional resolution message.
module: resolve_alert
options:
  alert_ids:
    description: A list of alert IDs to resolve.
    required: true
    type: list
    elements: str
  comments:
    description: A list of resolution comments for the alerts.
    required: false
    type: list
    elements: str
  api_token:
    description: The API token for authentication.
    required: true
    type: str
  environment_id:
    description: The ID of the environment.
    required: true
    type: str
short_description: Resolve a BigPanda alert.
version_added: 1.0.0
"""

EXAMPLES = """
- name: Resolve an alert
  bigpanda.incident.resolve_alert:
    alert_ids:
      - "54321"
    comments:
      - "Alert resolved."
    api_token: "your_api_token"
    environment_id: "your_environment_id"
"""

RETURN = """
changed:
  description: Indicates if the alert resolution was successful.
  type: bool
  returned: true/false
  sample: true
result:
  description: The response from the BigPanda server.
  type: str
  returned: BigPanda's Response
  sample: "Alert resolved successfully."
"""

from ansible.module_utils.basic import AnsibleModule
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def main():
    """
    The main function to execute the module.
    """
    module = AnsibleModule(
        argument_spec=dict(
            environment_id=dict(type='str', required=True),
            api_token=dict(type='str', required=True, no_log=True),
            alert_ids=dict(type='list', required=True, elements='str'),
            comments=dict(type='list', required=False, elements='str'),
        ),
        supports_check_mode=True
    )

    if not HAS_REQUESTS:
        module.fail_json(msg="The requests Python library is required")

    environment_id = module.params['environment_id']
    api_token = module.params['api_token']
    alert_ids = module.params['alert_ids']
    comments = module.params['comments']

    try:
        module.debug("Batch Resolve Alerts")

        # Prepare the JSON data
        data = {
            "ids": alert_ids,
        }

        if comments:
            data['comments'] = comments

        # Set the request headers
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
        }

        # Send the POST request using the requests library
        response = requests.post(
            f'https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/batch-resolve/alerts',
            headers=headers,
            json=data)

        response.raise_for_status()
        module.exit_json(changed=True, result=response.text)
    except HTTPError as e:
        # Log any HTTP errors
        module.fail_json(msg=f"An HTTP error occurred: {str(e)}")


if __name__ == '__main__':
    main()
