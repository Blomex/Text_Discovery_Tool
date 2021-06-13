import io
import os
import tempfile
from PIL import Image
from google.cloud import storage

storage_client = storage.Client()


def resize_image(image: Image) -> Image:
    """
    scales down the image to 1024x768 or lower, if it's size is bigger than 1024x768
    Otherwise, scales it to 90% of the size.
    1024x768 is the recommended size for the vision API to detect text.
    more information: https://cloud.google.com/vision/docs/supported-files
    """
    expected_x: int = 1024
    expected_y: int = 768
    x, y = image.size
    if x > expected_x or y > expected_y:
        scale = min(expected_x / x, expected_y / y)
        return image.resize((int(x * scale), int(y * scale)))
    else:
        return image.resize((int(0.9*x), int(0.9*y)))


def resize_and_process_image(data: dict, context):
    """
    Background Cloud Function to be triggered by Cloud Storage,
     which retrieves image from given bucket, resizes it, and saves it to second bucket.
    :param data: dictionary with following fields:
                    name - name of the file to resize
                    bucket - bucket, where file resides.

    :param context: Metadata of triggering event
    :return: None
    """
    file_name = data["name"]
    bucket_name = data["bucket"]
    _, temp_local_filename = tempfile.mkstemp(suffix=file_name)
    blob = storage_client.bucket(bucket_name).get_blob(file_name)
    blob_bytes = blob.download_as_bytes()
    output = io.BytesIO(blob_bytes)
    output.seek(0)
    image = Image.open(output)
    print("trying to resize image")
    # resizes image
    resized_image = resize_image(image)
    resized_image.save(fp=temp_local_filename)
    print("Image resized")

    # Upload result to second bucket
    print("Trying to upload resized image to second bucket")
    second_bucket_name = os.getenv("SECOND_BUCKET")
    second_bucket = storage_client.bucket(second_bucket_name)
    print("second bucket found")
    new_blob = second_bucket.blob(file_name)
    new_blob.metadata = blob.metadata
    print("created new blob")
    new_blob.upload_from_filename(temp_local_filename)
    print("uploaded resized image from file")
    os.remove(temp_local_filename)
