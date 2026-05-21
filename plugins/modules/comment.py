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
  - This module adds a comment to a BigPanda incident by providing the incident ID and the comment text.
module: comment
options:
  incident_id:
    description: The ID of the incident to add a comment to.
    required: true
    type: str
  comment:
    description: The text of the comment.
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
short_description: Add a comment to a BigPanda incident.
version_added: 1.0.0
"""

EXAMPLES = """
- name: Add a comment to an incident
  bigpanda.incident.comment:
    incident_id: "12345"
    comment: "This is a test comment."
    api_token: "your_api_token"
    environment_id: "your_environment_id"
"""

RETURN = """
changed:
  description: Indicates if the comment addition was successful.
  type: bool
  returned: true/false
  sample: true
result:
  description: The response from the BigPanda server.
  type: str
  returned: BigPanda's Response
  sample: "Comment added successfully."
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
            comment=dict(type='str', required=True),
            environment_id=dict(type='str', required=True),
            incident_id=dict(type='str', required=True),
            api_token=dict(type='str', required=True, no_log=True),
        ),
        supports_check_mode=True
    )

    if not HAS_REQUESTS:
        module.fail_json(msg="The requests Python library is required")

    comment = module.params['comment']
    environment_id = module.params['environment_id']
    incident_id = module.params['incident_id']
    api_token = module.params['api_token']

    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json',
    }

    json_data = {
        'comment': comment
    }

    try:
        response = requests.post(
            f'https://api.bigpanda.io/resources/v2.0/environments/{environment_id}/incidents/{incident_id}/comments',
            headers=headers,
            json=json_data,
        )

        response.raise_for_status()
        module.exit_json(changed=True, result=response.text)
    except HTTPError as e:
        # Log any HTTP errors
        module.fail_json(msg=f"An HTTP error occurred: {str(e)}")


if __name__ == '__main__':
    main()
