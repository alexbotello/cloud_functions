import os
import json
import datetime
from google.cloud import tasks_v2 # requires google-cloud-tasks==2.0.0
from google.protobuf import timestamp_pb2


def queue_task(request):
    """Given an HTTP endpoint and a payload this function will queue
    a POST request task using a Cloud Tasks queue
    """
    project = os.environ.get("PROJECT_ID")
    queue = os.environ.get("QUEUE_NAME")
    location = os.environ.get("QUEUE_REGION_LOCATION")

    request_json = request.get_json()

    # the http endpoint the task will send to
    url = request_json.get('url')
    # the post data that should be forwarded to the http endpoint
    payload = request_json.get('payload')
    # the time in seconds to delay task execution
    in_seconds = request_json.get('in_seconds')
    # the unique name of the task we are queueing
    task_name = request_json.get('task_name')

    # The service account email** required for authentication
    service_account_email = request_json.get("service_account_email")

    # Create a client.
    client = tasks_v2.CloudTasksClient()

    # Construct the fully qualified queue name.
    parent = client.queue_path(project, location, queue)

    # Construct the request body.
    task = {
        "http_request": {  # Specify the type of request.
            "http_method": tasks_v2.HttpMethod.POST,
            "url": url,
            "oidc_token": {"service_account_email": service_account_email},
        }
    }
    if payload is not None:
        if isinstance(payload, dict):
            # Convert dict to JSON string
            payload = json.dumps(payload)
            # specify http content-type to application/json
            task["http_request"]["headers"] = {"Content-type": "application/json"}

        # The API expects a payload of type bytes.
        converted_payload = payload.encode()

        # Add the payload to the request.
        task["http_request"]["body"] = converted_payload

    if in_seconds is not None:
        # Convert "seconds from now" into an rfc3339 datetime string.
        d = datetime.datetime.utcnow() + datetime.timedelta(seconds=in_seconds)

        # Create Timestamp protobuf.
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(d)

        # Add the timestamp to the tasks.
        task["schedule_time"] = timestamp

    if task_name is not None:
        # Add the name to tasks.
        task["name"] = task_name

    try:
        # Use the client to build and send the task.
        response = client.create_task(request={"parent": parent, "task": task})
        return f"Created task {response.name}", 200
    except Exception as e:
        print(e)
        return e, 500
    
