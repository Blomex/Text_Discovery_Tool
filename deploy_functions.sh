
gcloud functions deploy resize_and_process_image \
--source https://source.developers.google.com/projects/gcp-lectures-306513/repos/cloud-functions-project/moveable-aliases/master/paths/scale_down \
--runtime python38 \
--trigger-bucket upload_bucket_gcp-lectures-306513 \
--entry-point=resize_and_process_image