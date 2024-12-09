from googleapiclient.discovery import build
from oauth2client.client import GoogleCredentials
from base64 import b64decode
import functions_framework
import json

def get_state(value) -> str:
    mapping = {
        "on": "ALWAYS",
        "off": "NEVER"
    }

    try:
        return mapping[value]
    except KeyError:
        raise ValueError("Valid values: on, off")


@functions_framework.cloud_event
def change_state(cloud_event):
    credentials = GoogleCredentials.get_application_default()
    sql_service = build('sqladmin', 'v1beta4', credentials=credentials)
    payload = json.loads(b64decode(cloud_event.data['message']['data']).decode('utf-8'))

    req_body = {
        "settings": {
            "activationPolicy": "POLICY",
            "settingsVersion": 0,
            "tier": "TIER"
        }
    }

    if not payload or 'instance' not in payload or 'project' not in payload:
        from flask import abort
        return abort(500)

    project = payload['project']
    
    for instance in payload['instance']:
        instance_name = instance['name']
        state = get_state(instance['state'])

        print(f"Processing instance {instance_name}")
        try:
          sql_instance = sql_service.instances().get(
            project = project,
            instance = instance_name
          )
          sql_instance_params = sql_instance.execute()
        except Exception as e:
            print(RuntimeError(f"Error to get instance params. Reason: {e}"))
            continue
        finally:
          sql_service.close()

        if sql_instance_params['settings']['activationPolicy'] == state:
            print(f"Instance {instance_name} is already {instance['state']}")
            continue

        req_body['settings']['activationPolicy'] = state
        req_body['settings']['settingsVersion'] = int(sql_instance_params['settings']['settingsVersion'])
        req_body['settings']['tier'] = sql_instance_params['settings']['tier']

        try:
            req = sql_service.instances().patch(
                project = project,
                instance = instance_name,
                body = req_body
            )
            print(f"Changing state of {instance_name} to {instance['state']}")
            req.execute()
        except Exception as e:
            print(RuntimeError(f"Failed to change state to {instance['state']}. Reason: {e}"))
            continue
        finally:
            sql_service.close()
