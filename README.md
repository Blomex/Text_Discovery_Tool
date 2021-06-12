# **Text Discovery Tool**

## Short Description
App allows users to discover what text is available on the image.
This could be useful 
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


### Using single build trigger in empty GCP project
1. Copy this repository as your google cloud repository
2. Check on `deploy_functions.sh` file. Replace --source argument with similiar link to your repository 
(remember to replace `gcp-lectures-306513` with your project id, and `cloud-functions-project` with your repository name)

3. enable 'Cloud Functions' and 'App Engine' in Cloud Build 
-> Settings -> Service account permissions
4. Enable necessary GCP functionalities: Vision API, Cloud Storage, Firestore, 
Google App Engine, Google Cloud Functions
5. create the following cloudbuild.yaml file:

  ```yaml
   steps:
  - name: gcr.io/google.com/cloudsdktool/cloud-sdk
    env:
      - >-
        GOOGLE_CLIENT_ID=???
      - GOOGLE_CLIENT_SECRET=???
      - >-
        SENDGRID_API_KEY=???
      - UPLOAD_BUCKET=???
      - SECOND_BUCKET=???
      - PROJECT_ID=???
      - >-
        SECRET_KEY=???
    args:
      - ./prepare_env.sh
    entrypoint: bash
  - name: gcr.io/google.com/cloudsdktool/cloud-sdk
    args:
      - gcloud
      - app
      - deploy
      - app.yaml
  - name: gcr.io/google.com/cloudsdktool/cloud-sdk
    env:
      - >-
        GOOGLE_CLIENT_ID=???
      - GOOGLE_CLIENT_SECRET=???
      - >-
        SENDGRID_API_KEY=???
      - UPLOAD_BUCKET=???
      - SECOND_BUCKET=???
      - PROJECT_ID=???
    args:
      - ./deploy_functions.sh
    waitFor:
      - '-'
    entrypoint: bash
```
##### GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET 
should be credentials for OAuth2 Client. 
To create credentials, do the following:

Go into APIs & Services -> Credentials

Create credentials for OAuth 2.0 Client ID.

Add https://your_app_link.com/login/callback to Auhtorized redirect URIs


##### SENDGRID_API_KEY
this is API key from sendgrid. To create it, you need to create sendgrid account. 
more informations at: http://sendgrid.com/

##### UPLOAD_BUCKET
this is first bucket name, where all uploaded images are stored.

##### SECOND_BUCKET
this is second bucket name, where images after resize are stored.

##### PROJECT_ID
this is your Google Project ID.
##### SECRET_KEY 
this is used to sign session cookies for protection against cookie data tampering. Without setting this up, CSRF token verification might not work correctly on google app engine.

### Using separate build triggers for cloud functions and GAE Application
This could be useful in development process.


1. Create build trigger for the GAE Application, providing the following yaml file:
```yaml
    steps:
  - name: gcr.io/google.com/cloudsdktool/cloud-sdk
    env:
      - GOOGLE_CLIENT_ID=???
      - GOOGLE_CLIENT_SECRET=???
      - SENDGRID_API_KEY=???
      - UPLOAD_BUCKET=???
      - SECOND_BUCKET=???
      - PROJECT_ID=???
      - SECRET_KEY=???
    args:
      - ./prepare_env.sh
    entrypoint: bash
  - name: gcr.io/google.com/cloudsdktool/cloud-sdk
    env:
      - GOOGLE_CLIENT_ID=???
      - GOOGLE_CLIENT_SECRET=???
      - UPLOAD_BUCKET=???
      - SECOND_BUCKET=???
      - PROJECT_ID=???
    args:
      - gcloud
      - app
      - deploy
      - app.yaml
```
2. Create build triggers for each of the cloud functions. 
```yaml
    steps:
  - name: gcr.io/google.com/cloudsdktool/cloud-sdk
    env:
      - GOOGLE_CLIENT_ID=???
      - GOOGLE_CLIENT_SECRET=???
      - SENDGRID_API_KEY=???
      - UPLOAD_BUCKET=???
      - SECOND_BUCKET=???
      - PROJECT_ID=???
    args:
      - gcloud
      - functions
      - deploy
      - <F_NAME>
      - '--source'
      - <link_to_cloud_function_directory_in_repository>
      - '--runtime'
      - python39
      - '--trigger-bucket'
      - upload_bucket_gcp-lectures-306513
      - '--entry-point=<FUNCTION_NAME>'
    waitFor:
      - '-'
```
replace <F_NAME> with how the function should be named.

replace <link_to_cloud_function_directory_in_repository> with link to your google cloud repository in the following format:

https://source.developers.google.com/projects/<PROJECT_ID>/repos/<REPOSITORY_NAME>/moveable-aliases/master/paths/<PATH_TO_DIRECTORY>

<PROJECT_ID> is the google project id.

<REPOSITORY_NAME> is the google repository name.

<PATH_TO_DIRECTORY> is path to the directory inside the repository. Function should be inside some kind of directory inside file main.py
For example, if function is located in `function/main.py`, you should pass `function` as path to directory.
replace <FUNCTION_NAME> with the function name inside main.py. For example, if function is defined as `def cloudfun1`, replace <FUNCTION NAME> with `cloudfun1`

for the functions in the project, it is as following data will suffice 
(you will need to create google cloud repository on your own): 

cloud function 1 (resize_and_process_image):

F_NAME: resize_and_process_image

FUNCTION_NAME: resize_and_process_image

PATH_TO_DIRECTORY: scale_down

cloud function 2 (discover_text):

F_NAME: discover_text

FUNCTION_NAME: discover_text

PATH_TO_DIRECTORY: scale_down

cloud function 3 (send_email):

F_NAME: send_email

FUNCTION_NAME: send_email

PATH_TO_DIRECTORY: send_email

#### Running Tests
to run tests, you need to have following variables in your environment:
GOOGLE_APPLICATION_CREDENTIALS - path to json file with google application credentials.

to run tests, make sure you are in repo root directory, and that environmental variable with google application credentials is set.

Then, you need to create test environment:

```python -m venv test_env```

activate the environment:

`source test_env/bin/activate`

install requirements to run tests:

`pip install -r ./tests/requirements.txt`

and finally, run the tests:

`python -m pytest run ./tests/tests.py`


##
