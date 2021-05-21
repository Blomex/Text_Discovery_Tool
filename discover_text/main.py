import os
from google.cloud import storage, vision
from google.cloud import datastore, pubsub_v1
import tempfile
import io
storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()
import json

def discover_text(data, context):
    file_name = data["name"]
    bucket_name = data["bucket"]
    metadata = data["metadata"]
    email = metadata.get("email")
    _, temp_local_filename = tempfile.mkstemp()
    blob = storage_client.bucket(bucket_name).get_blob(file_name)

    image = vision.Image(source=vision.ImageSource(gcs_image_uri=f"gs://{bucket_name}/{file_name}"))
    response = vision_client.text_detection(image=image)
    annotations = response.text_annotations
    text = ""
    if len(annotations) > 0:
        text += annotations[0].description

    ds = datastore.Client()
    entity = datastore.Entity(key=ds.key('text_from_images'))
    entity.update({
        'email': email,
        'file_name': file_name,
        'text_found': text,
    })
    ds.put(entity)

def publish_pubsub(file_name):
    topic_name = "new_image"
    publisher = pubsub_v1.PublisherClient()
    message = file_name
    print(f"Publishing message to {topic_name}")
    PROJECT_ID = os.getenv('PROJECT_ID')
    topic_path = publisher.topic_path(PROJECT_ID, topic_name)

    message_json = json.dumps({
        'data': {'message': message}
    })
    try:
        publish_result = publisher.publish(topic_path, data=message_json.encode('utf-8'))
        publish_result.result()
    except Exception as e:
        print(e)
        return e, 500

