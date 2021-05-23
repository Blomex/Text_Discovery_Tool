import os
from google.cloud import storage, vision
from google.cloud import datastore, pubsub_v1
import tempfile
import io
storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()
import json


def discover_text(data: dict, context):
    """
    Background Cloud Function to be triggered by Cloud Storage.
    Function discovers text in the image using vision API.
    :param data: The dictionary with following fields:
                    name - name of the file, from which we want to discover text
                    bucket - name of the bucket, where file is located
                    metadata - dictionary with metadata, has field 'email' - email of uploader.
    :param context: Metadata of triggering event
    :return:
    """
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
    entityIter = iter(ds.query(kind="text_from_images").add_filter("hash", "=", file_name).fetch())
    try:
        entity = entityIter.__next__()
        entity.update({
            'text_found': text,
        })
        ds.put(entity)
        print(f"entity {entity} sucesfully updated")
    except google.api_core.exceptions.FailedPrecondition:
        print("couldn't add discovered text to entity: no such entity found")
    publish_pubsub(file_name, text, email)

def publish_pubsub(file_name, text, email):
    topic_name = "new_image"
    publisher = pubsub_v1.PublisherClient()
    message = text

    print(f"Publishing message to {topic_name}")
    PROJECT_ID = os.getenv('PROJECT_ID')
    topic_path = publisher.topic_path(PROJECT_ID, topic_name)

    message_json = json.dumps({
        'data': {
            'file_name': file_name,
            'message': message,
            'email': email
        }
    })
    try:
        publish_result = publisher.publish(topic_path, data=message_json.encode('utf-8'))
        publish_result.result()
    except Exception as e:
        print(e)
        return e, 500

