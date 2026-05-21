# BigPanda Integration with Ansible Automation Platform

## Overview

This integration enables automated incident response and bi-directional sync between BigPanda and Ansible Automation Platform (AAP).

| Detail | Value |
|--------|-------|
| Supported AAP versions | 2.5, 2.6, 2.7 |
| Collection | `bigpanda.incident` |
| Integration type | Webhook via EDA Gateway (2.6+) or direct (2.5) |
| Authentication | EDA Gateway (2.6+) or Org Bearer Token (2.5) |
| Galaxy / Automation Hub | [bigpanda.incident](https://console.redhat.com/ansible/automation-hub) |

---

## Architecture

### AAP 2.6+ (Recommended)

In AAP 2.6 and later, BigPanda webhooks flow through the **EDA Gateway**, which handles authentication, TLS termination, and event routing. The source plugin never sees credentials.

```
BigPanda Alert
    │
    ▼
EDA Gateway  ←── Authentication + TLS handled here
    │
    ▼
External Event Stream
    │
    ▼
bigpanda.incident.bigpanda_webhook  ←── Filters + normalizes events
    │
    ▼
Rulebook Engine  ←── Evaluates conditions, triggers actions
    │
    ▼
AAP Controller  ←── Launches job templates / playbooks
    │
    ▼
bigpanda.incident modules  ←── Resolve, comment, tag, merge, split
    │
    ▼
BigPanda API (api.bigpanda.io/resources/v2.0)
```

### AAP 2.5 (Legacy)

In AAP 2.5, BigPanda sends webhooks directly to an EDA Controller endpoint using the generic `ansible.eda.webhook` source. Authentication uses an Org Bearer Token passed via custom headers.

---

## Key Features

- **Bi-directional sync** — Constant updates on automation state. Actions in BigPanda trigger Ansible playbooks; actions in Ansible update BigPanda incidents.
- **Cross-system resolution** — Resolving in either BigPanda or Ansible resolves incidents/alerts in both systems.
- **Incident tag updates** — Real-time tag value updates from Ansible playbooks back to BigPanda.
- **Comment tracking** — Comments appended to BigPanda incidents to track automation progress.
- **Event-driven automation** — Automatic remediation triggered by alert status changes via EDA.
- **Status filtering** — Filter incoming events by BigPanda alert status (critical, warning, ok) before rulebook evaluation.

---

## Installation

### Prerequisites

- Ansible Automation Platform 2.6+ (recommended) or 2.5
- Python 3.12 or higher
- `ansible-core` >= 2.16.0
- A BigPanda account with API access
- For AAP 2.6+: EDA Gateway configured and accessible

### Install the Collection

From Automation Hub (AAP customers):

```bash
ansible-galaxy collection install bigpanda.incident
```

From source:

```bash
git clone https://github.com/bigpandaio/bigpanda-ansible.git
cd bigpanda-ansible
ansible-galaxy collection build --force
ansible-galaxy collection install bigpanda-incident-*.tar.gz -p ./collections -f
```

---

## Setup: AAP 2.6+ with EDA Gateway

### Step 1: Create an External Event Stream

1. In the EDA Controller UI, navigate to **Event Streams** > **Create Event Stream**
2. Set the **Name** (e.g., "BigPanda Alerts")
3. Select the **Credential Type** appropriate for your webhook authentication
4. Note the generated **Gateway URL**:
   ```
   https://<eda-gateway>/api/eda/v1/external_event_stream/<stream-id>/post/
   ```

### Step 2: Configure BigPanda Webhook

1. In BigPanda, navigate to **Integrations** > **Outbound** > **Webhook**
2. Set the **Webhook URL** to the EDA Gateway URL from Step 1
3. Configure authentication as required by your Gateway credential setup
4. Select the event types to forward:
   - `incident#new`
   - `incident#updated`
   - `incident#closed`
   - `incident#reopen`
   - `incident#commented`
   - `incident-tag#upserted`

### Step 3: Create a Rulebook Activation

Create a rulebook that uses the `bigpanda.incident.bigpanda_webhook` source:

```yaml
---
- name: BigPanda Alert Automation
  hosts: all
  sources:
    - bigpanda.incident.bigpanda_webhook:
        event_filter:
          - critical
          - warning
  rules:
    - name: Auto-remediate critical alerts
      condition: event.payload.status == "critical"
      action:
        run_job_template:
          name: "Remediate BigPanda Alert"
          organization: "Default"
          job_args:
            extra_vars:
              incident_id: "{{ event.payload.incident_id }}"
              alert_status: "{{ event.payload.status }}"
              environment_id: "{{ event.payload.environment_id }}"

    - name: Log resolved alerts
      condition: event.payload.status == "ok"
      action:
        debug:
          msg: "Alert {{ event.payload.alert_id | default('unknown') }} resolved"
```

Activate this rulebook in the EDA Controller:

1. Navigate to **Rulebook Activations** > **Create Activation**
2. Select the rulebook and the Decision Environment
3. Link the External Event Stream created in Step 1
4. Enable the activation

### Step 4: Create Action Playbooks

Create playbooks that the rulebook triggers to interact with BigPanda:

```yaml
---
# remediate_and_resolve.yml
- name: Remediate and resolve BigPanda incident
  hosts: localhost
  connection: local
  vars:
    bigpanda_env_id: "{{ environment_id }}"
    bigpanda_token: "{{ bigpanda_api_token }}"  # From AAP credential
  tasks:
    - name: Run remediation steps
      # ... your remediation tasks here ...

    - name: Add comment to BigPanda incident
      bigpanda.incident.comment:
        environment_id: "{{ bigpanda_env_id }}"
        incident_id: "{{ incident_id }}"
        comment: "Automated remediation completed by AAP"
        api_token: "{{ bigpanda_token }}"

    - name: Resolve the incident
      bigpanda.incident.resolve:
        environment_id: "{{ bigpanda_env_id }}"
        incident_id: "{{ incident_id }}"
        resolution_comment: "Resolved via automated remediation"
        api_token: "{{ bigpanda_token }}"
```

> **Important:** Store the BigPanda API token as an AAP Controller credential, not in the playbook. Reference it via `extra_vars` or a custom credential type.

---

## Setup: AAP 2.5 (Legacy)

For AAP 2.5, use the generic `ansible.eda.webhook` source since the EDA Gateway is not available:

```yaml
---
- name: BigPanda Webhook (AAP 2.5)
  hosts: all
  sources:
    - ansible.eda.webhook:
        host: 0.0.0.0
        port: 5000
  rules:
    - name: BigPanda alert received
      condition: event.payload.status is defined
      action:
        run_job_template:
          name: "Remediate BigPanda Alert"
          organization: "Default"
```

Configure BigPanda to send webhooks directly to `http://<eda-controller>:5000/` with custom headers for authentication:

| Header | Value |
|--------|-------|
| `x-bp-config-ansibleURL` | URL of the EDA Controller |
| `x-bp-config-ansibleApiToken` | AAP API token |
| `x-bp-config-ansibleVersion` | `2.5` |

---

## Credential Management

### AAP 2.6+ (Gateway-Managed)

Authentication is handled entirely by the EDA Gateway. To configure:

1. In EDA Controller, create a **Credential** with the webhook secret or token
2. Attach the credential to the **External Event Stream**
3. The Gateway validates incoming webhooks before forwarding to the source plugin
4. BigPanda API tokens for action modules are stored as **AAP Controller Credentials**

**Do not** pass API tokens as source plugin parameters or hardcode them in rulebooks.

### AAP 2.5 (Custom Headers)

In AAP 2.5, authentication uses BigPanda custom headers. See the Custom Headers section below.

---

## Action Modules Reference

All action modules call the BigPanda Incidents V2 API (`https://api.bigpanda.io/resources/v2.0/`).

### bigpanda.incident.resolve

Resolve a BigPanda incident.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `environment_id` | Yes | str | BigPanda environment ID |
| `incident_id` | Yes | str | ID of the incident to resolve |
| `resolution_comment` | No | str | Resolution message |
| `api_token` | Yes | str | BigPanda API token (use AAP credential) |

```yaml
- name: Resolve incident
  bigpanda.incident.resolve:
    environment_id: "{{ bigpanda_env_id }}"
    incident_id: "{{ incident_id }}"
    resolution_comment: "Resolved via automated remediation"
    api_token: "{{ bigpanda_api_token }}"
```

### bigpanda.incident.resolve_alert

Batch-resolve one or more BigPanda alerts.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `environment_id` | Yes | str | BigPanda environment ID |
| `alert_ids` | Yes | list | List of alert IDs to resolve |
| `comments` | No | list | Resolution comments per alert |
| `api_token` | Yes | str | BigPanda API token |

```yaml
- name: Resolve specific alerts
  bigpanda.incident.resolve_alert:
    environment_id: "{{ bigpanda_env_id }}"
    alert_ids:
      - "alert-001"
      - "alert-002"
    api_token: "{{ bigpanda_api_token }}"
```

### bigpanda.incident.comment

Add a comment to a BigPanda incident.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `environment_id` | Yes | str | BigPanda environment ID |
| `incident_id` | Yes | str | ID of the incident |
| `comment` | Yes | str | Comment text |
| `api_token` | Yes | str | BigPanda API token |

```yaml
- name: Add automation comment
  bigpanda.incident.comment:
    environment_id: "{{ bigpanda_env_id }}"
    incident_id: "{{ incident_id }}"
    comment: "Playbook execution completed successfully"
    api_token: "{{ bigpanda_api_token }}"
```

### bigpanda.incident.add_tag

Add or update a tag on a BigPanda incident.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `environment_id` | Yes | str | BigPanda environment ID |
| `incident_id` | Yes | str | ID of the incident |
| `tag_id` | Yes | str | Tag identifier |
| `tag_value` | Yes | str | Tag value |
| `api_token` | Yes | str | BigPanda API token |

```yaml
- name: Tag incident with remediation status
  bigpanda.incident.add_tag:
    environment_id: "{{ bigpanda_env_id }}"
    incident_id: "{{ incident_id }}"
    tag_id: "remediation_status"
    tag_value: "completed"
    api_token: "{{ bigpanda_api_token }}"
```

### bigpanda.incident.assign

Assign a BigPanda incident to a team or user.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `environment_id` | Yes | str | BigPanda environment ID |
| `incident_id` | Yes | str | ID of the incident |
| `assignee` | Yes | str | User or team to assign to |
| `api_token` | Yes | str | BigPanda API token |

```yaml
- name: Assign to on-call team
  bigpanda.incident.assign:
    environment_id: "{{ bigpanda_env_id }}"
    incident_id: "{{ incident_id }}"
    assignee: "oncall-sre"
    api_token: "{{ bigpanda_api_token }}"
```

### bigpanda.incident.merge

Merge multiple BigPanda incidents.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `environment_id` | Yes | str | BigPanda environment ID |
| `incident_id` | Yes | str | Target incident ID |
| `source_incident_ids` | Yes | list | Incident IDs to merge into the target |
| `comment` | No | str | Merge comment |
| `api_token` | Yes | str | BigPanda API token |

```yaml
- name: Merge related incidents
  bigpanda.incident.merge:
    environment_id: "{{ bigpanda_env_id }}"
    incident_id: "{{ primary_incident_id }}"
    source_incident_ids:
      - "{{ related_incident_1 }}"
      - "{{ related_incident_2 }}"
    comment: "Auto-merged by correlation rule"
    api_token: "{{ bigpanda_api_token }}"
```

### bigpanda.incident.split

Split alerts from a BigPanda incident into a new incident.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `environment_id` | Yes | str | BigPanda environment ID |
| `incident_id` | Yes | str | Source incident ID |
| `alert_ids` | Yes | list | Alert IDs to split out |
| `comment` | No | str | Split comment |
| `api_token` | Yes | str | BigPanda API token |

```yaml
- name: Split unrelated alert
  bigpanda.incident.split:
    environment_id: "{{ bigpanda_env_id }}"
    incident_id: "{{ incident_id }}"
    alert_ids:
      - "{{ unrelated_alert_id }}"
    comment: "Split: different root cause"
    api_token: "{{ bigpanda_api_token }}"
```

---

## EDA Event Source Reference

### bigpanda.incident.bigpanda_webhook

Processes BigPanda webhook payloads delivered through the EDA Gateway event stream.

| Parameter | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `event_filter` | No | list | [] | Filter by BigPanda alert status values |

> **Note:** Authentication is handled by the EDA Gateway. Do not pass credentials to the source plugin.

#### Event Payload

Events emitted by the source contain:

```json
{
  "payload": {
    "status": "critical",
    "incident_id": "inc-12345",
    "alert_id": "alert-67890",
    "environment_id": "env-001",
    "event_type": "incident#new",
    "...": "full BigPanda webhook payload"
  },
  "meta": {
    "source": "bigpanda_webhook"
  }
}
```

#### Supported BigPanda Event Types

| Event Type | Description |
|------------|-------------|
| `incident#new` | New incident created |
| `incident#updated` | Incident updated (status, severity, or alerts changed) |
| `incident#closed` | Incident closed/resolved |
| `incident#reopen` | Previously closed incident reopened |
| `incident#commented` | Comment added to incident |
| `incident#snoozed` | Incident snoozed |
| `incident#become-flapping` | Incident entered flapping state |
| `incident-tag#upserted` | Incident tag added or updated |
| `incident#ticket-sync` | Ticket sync update (sent every 2.5 minutes by default) |

---

## Custom Headers (AAP 2.5 / Legacy)

Custom headers are used in AAP 2.5 deployments where the EDA Gateway is not available. In AAP 2.6+, these are replaced by the Gateway's credential system.

### OAuth 2.0 Headers

| Header | Description |
|--------|-------------|
| `x-bp-config-oauthUrl` | OAuth provider URL |
| `x-bp-config-oauthClientId` | OAuth client ID |
| `x-bp-config-oauthClientSecret` | OAuth client secret |
| `x-bp-config-oauthGrantType` | OAuth grant type |
| `x-bp-config-oauthPassword` | (Optional) Password for password grant type |
| `x-bp-config-oauthUser` | (Optional) OAuth user |
| `x-bp-config-oauthScope` | (Optional) OAuth scope |

### Integration Headers

| Header | Required | Description |
|--------|----------|-------------|
| `x-bp-config-ansibleURL` | Yes | URL of the Automation Controller or EDA Controller |
| `x-bp-config-ansibleApiToken` | Yes | AAP API token |
| `x-bp-config-ansibleVersion` | Yes (>2.4) | AAP version (e.g., `2.5`) |
| `x-bp-config-automateIndividualAlerts` | Yes (AAP) | When true, sends per-alert requests |
| `x-bp-config-alertTemplateIdTagname` | Yes (AAP) | Alert tag for template routing |
| `x-bp-config-defaultTemplateId` | No | Default job template ID |
| `x-bp-config-ansibleOverrideURL` | No | Override URL for pre-processing |

---

## Decision and Execution Environments

### Decision Environment (EDA)

The Decision Environment runs the rulebook engine. It must include:

- `bigpanda.incident` collection
- Python 3.12+
- `ansible-core` >= 2.16.0

### Execution Environment (AAP Controller)

The Execution Environment runs action playbooks. It must include:

- `bigpanda.incident` collection
- `requests` Python library
- Python 3.12+
- `ansible-core` >= 2.16.0

---

## Uninstall

### Step 1: Disable Event Stream (AAP 2.6+)

1. In EDA Controller, navigate to **Rulebook Activations**
2. Disable or delete the BigPanda activation
3. Delete the External Event Stream

### Step 2: Remove BigPanda Webhook

1. In BigPanda, navigate to **Integrations** > **Outbound**
2. Delete the webhook integration pointing to AAP

### Step 3: Remove AutoShare Rules

Disable or remove any AutoShare rules configured for the Ansible integration.

> **Note:** Uninstalling does not remove historical data from either BigPanda or AAP. Remove data manually from each system as needed.

---

## Troubleshooting

### Events not reaching rulebooks (AAP 2.6+)

1. Verify the External Event Stream is active in EDA Controller
2. Check the Gateway URL matches the BigPanda webhook configuration
3. Verify Gateway credentials are valid
4. Check EDA Controller logs: `journalctl -u eda-server -f`

### Action modules failing

1. Verify the BigPanda API token is valid and has sufficient permissions
2. Check the `environment_id` matches your BigPanda environment
3. Test connectivity: `curl -H "Authorization: Bearer <token>" https://api.bigpanda.io/resources/v2.0/environments/<env_id>/incidents`

### Modules not found

1. Verify the collection is installed: `ansible-galaxy collection list | grep bigpanda`
2. Check the Execution Environment includes `bigpanda.incident`
3. Verify Python `requests` library is installed in the EE

---

## Version Compatibility Matrix

| AAP Version | Collection Version | Python | Integration Method |
|-------------|-------------------|--------|-------------------|
| 2.7 | 1.3.0+ | 3.12+ | EDA Gateway |
| 2.6 | 1.3.0+ | 3.12+ | EDA Gateway |
| 2.5 | 1.2.x | 3.9+ | Direct webhook + custom headers |
| ≤2.4 | 1.1.x | 3.8+ | Direct webhook + custom headers |
