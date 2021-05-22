
# deploys function to scale down
gcloud functions deploy resize_and_process_image \
--source https://source.developers.google.com/projects/gcp-lectures-306513/repos/cloud-functions-project/moveable-aliases/master/paths/scale_down \
--runtime python39 \
--trigger-bucket upload_bucket_gcp-lectures-306513 \
--entry-point=resize_and_process_image \
--set-env-vars SECOND_BUCKET_NAME=resize_bucket__gcp-lectures-306513

gcloud functions deploy discover_text \
--source https://source.developers.google.com/projects/gcp-lectures-306513/repos/cloud-functions-project/moveable-aliases/master/paths/discover_text \
--runtime python39 \
--trigger-bucket resize_bucket__gcp-lectures-306513 \
--entry-point=discover_text \
--set-env-vars PROJECT_ID=gcp-lectures-306513

gcloud functions deploy send_email \
--source https://source.developers.google.com/projects/gcp-lectures-306513/repos/cloud-functions-project/moveable-aliases/master/paths/send_email \
--runtime python39 \
--trigger-topic new_image \
--entry-point=send_email \
--env-vars-file .env.yaml \
--service-account=gcp-lectures-306513@appspot.gserviceaccount.com
