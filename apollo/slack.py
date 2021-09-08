import json
import requests

from apollo.config import VARS

webhook_url = VARS['webhook_url']

def add_header(status: str, run_id: int, job_name: str, environment: str, trigger: str, duration: str) -> dict:

    if status == 'success':
        color = '#2CB081'
        msg = status
    elif status == 'error':
        color = '#A30101'
        msg = 'failed'
    
    slack_header = {
        "attachments": [
		{
			"fallback": f"Job \"{job_name}\" {msg}",
            "color": f"{color}",
			"blocks": [
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": f"*Run #{run_id} {msg} on Job \"{job_name}\"*"
					}
				},
				{
					"type": "section",
					"fields": [
						{
							"type": "mrkdwn",
							"text": f"*Environment:*\n{environment}"
						},
						{
							"type": "mrkdwn",
							"text": f"*Trigger:*\n{trigger}"
						},
                        {
							"type": "mrkdwn",
							"text": f"*Duration:*\n{duration}"
						}
					]
				},
				{
					"type": "actions",
					"block_id": "actionblock789",
					"elements": [
						{
							"type": "button",
							"text": {
								"type": "plain_text",
								"text": "Open run in dbt Cloud"
							},
							"style": "primary",
							"url": f"https://***.com/dbt/runs/{run_id}"
						}
					]
				}
			]
		}
	]}
    return slack_header

def add_attachment(status: str, text_string: str) -> dict:

    if status == 'success':
        color = '#2CB081'
    elif status == 'error':
        color = '#A30101'
    elif status == 'skipped':
        color = '#D1D1D1'

    attachment = {
			"color": f"{color}",
			"blocks": [
				{
					"type": "section",
					"text": {
						"type": "mrkdwn",
						"text": f"{text_string}"
					}
				}
			]
		}
    return attachment

def post_message(slack_message: str) -> None:
    response = requests.post(webhook_url, data=json.dumps(slack_message), headers={'Content-Type': 'application/json'})
    if response.status_code != 200:
        raise ValueError(f"Request to slack returned a {response.status_code} error, the response is:\n{response.text}")
