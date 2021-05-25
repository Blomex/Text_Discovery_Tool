#**Text Discovery Tool**
## Description
App realizes following user flow:
1. User can navigate to a website, where he can use his Google account to log in into the system.
2. After sucessful login, one can upload an image in JPG or PNG format, and this image is stored in Cloud Storage Upload Bucket.
3. First cloud function with a Upload Bucket trigger discovers, than an image was uploaded there, scales down the picture, and stores it into the second bucket.
4. Second cloud function with Second Bucket trigger discovers images in the bucked, makes a call to Vision API and discover the text
visible in the image. Results of the Vision API call are stored in the Datastore. Finally, second cloud function puts the message on Pub/Sub channel that is trigger for third cloud function.
5. Third cloud function sends an email with the link to the image to the GCP User. Email contains signed URLs to both original and resized image. 
Email also contains text discovered for this specific image by Vision API.
6. User can press "Logout" button to log out of the service. 
Once one presses "Logout", One is navigated back to login/initial page, where there is a "Login"
button that one can use to log back into the system.
##Installation


### Using build trigger in empty GCP project
1. Copy this repository as your google cloud repository
2. enable 'Cloud Functions' and 'App Engine' in Cloud Build 
-> Settings -> Service account permissions
3. Enable necessary GCP functionalities: Vision API, Cloud Storage, Firestore, 
Google App Engine, Google Cloud Functions
4. create the following cloudbuild.yaml file:

     ```yaml
    steps:
      - name: gcr.io/google.com/cloudsdktool/cloud-sdk
        env:
          - >-
            GOOGLE_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>
          - GOOGLE_CLIENT_SECRET=<YOUR_GOOGLE_CLIENT_SECRET>
          - >-
            SENDGRID_API_KEY=<YOUR_SENDGRID_API_KEY>
          - UPLOAD_BUCKET=<YOUR_UPLOAD_BUCKET>
          - SECOND_BUCKET=<YOUR_SECOND_BUCKET>
          - PROJECT_ID=<YOUR_PROJECT_ID>
        args:
          - ./deploy_functions.sh
        entrypoint: bash
      - name: gcr.io/google.com/cloudsdktool/cloud-sdk
        env:
          - >-
            GOOGLE_CLIENT_ID=<YOUR_GOOGLE_CLIENT_ID>
          - GOOGLE_CLIENT_SECRET=<YOUR_GOOGLE_CLIENT_SECRET>
        args:
          - gcloud
          - app
          - deploy
    ```
    GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are 
5.
4. In Cloud Build, create trigger from the provided cloudbuild.yaml file
6. In Cloud Build -> Triggers, click "RUN" to run the created trigger.


##
