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
  - This module updates a BigPanda incident tag by providing the tag ID, tag value, incident ID, and an API token.
module: add_tag
options:
  tag_id:
    description: The ID of the tag to update.
    required: true
    type: str
  tag_value:
    description: The new value for the tag.
    required: true
    type: str
  incident_id:
    description: The ID of the incident to update.
    required: true
    type: str
  api_token:
    description: The API token for authentication.
    required: true
    type: str
  environment_id:
    description: The ID of the environment.
    required: true
    type: str
short_description: Update a BigPanda incident tag.
version_added: 1.0.0
"""

EXAMPLES = """
- name: Update an incident tag
  bigpanda.incident.add_tag:
    tag_id: "tag123"
    tag_value: "NewTagValue"
    incident_id: "incident456"
    api_token: "your_api_token"
    environment_id: "your_environment_id"
"""

RETURN = """
changed:
  description: Indicates if the tag update was successful.
  type: bool
  returned: true/false
  sample: true
result:
  description: The response from the BigPanda server.
  type: str
  returned: BigPanda's Response
  sample: "Tag updated successfully."
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bigpanda.incident.plugins.module_utils.bigpanda_common import (
    require_requests,
    bigpanda_request,
)


def main():

    module = AnsibleModule(
        argument_spec=dict(
            tag_id=dict(type='str', required=True),
            tag_value=dict(type='str', required=True),
            incident_id=dict(type='str', required=True),
            api_token=dict(type='str', required=True, no_log=True),
            environment_id=dict(type='str', required=True),
        ),
        supports_check_mode=True
    )

    tag_id = module.params['tag_id']
    tag_value = module.params['tag_value']
    incident_id = module.params['incident_id']
    api_token = module.params['api_token']
    environment_id = module.params['environment_id']

    try:
        module.debug("Update Incident Tag")

        # Set the request headers
        headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
        }

        # Prepare the JSON data to be sent with the request
        json_data = {
            "tag_value": tag_value
        }
        module.debug(json_data)
        # Send the POST request to update the incident tag
        response = requests.post(
            f'https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents/{incident_id}/tags/{tag_id}',
            headers=headers,
            json=json_data)

        response.raise_for_status()
        module.exit_json(changed=True, result=response.text)
    except Exception as e:
        # Log any HTTP errors
        module.fail_json(msg=f"An HTTP error occurred: {str(e)}")


if __name__ == '__main__':
    main()
