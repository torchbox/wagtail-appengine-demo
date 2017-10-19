# Wagtail on Google App Engine demonstration

This is the simplest possible Wagtail site on Google Cloud, using App Engine Flexible and Cloud SQL.

## Assumptions

1. A project has been created in the Google Cloud Platform Console
2. Billing has been enabled for your project
3. The Google Cloud SDK is installed locally
4. The Google Cloud SQL API has been enabled for your project

These steps are detailed in the [Google Cloud documentation](https://cloud.google.com/python/django/flexible-environment#before-you-begin).

## Download this app and install its dependencies

```
git clone https://github.com/torchbox/wagtail-appengine-demo
cd wagtail-appengine-demo
pyvenv wagtail-appengine-demo # or your preferred method of creating a virtualenv
pip install -r requirements.txt
```

## Configure Cloud SQL

Wagtail will use a Cloud SQL PostgreSQL database for its data storage.

### Create a new Cloud SQL database

Create a new Cloud SQL instance:

```
gcloud sql instances create wagae   \
    --assign-ip                     \
    --database-version=POSTGRES_9_6 \
    --region=europe-west2           \
    --gce-zone=europe-west2-c       \
    --storage-size=50               \
    --storage-type=HDD              \
    --tier=db-g1-small
```

Adjust region, zone storage and machine size (tier) options as necessary.  
While Wagtail supports MySQL, only PostgreSQL has been tested here.

Create a new user and database, substituting a secure password for
`[DB_PASSWORD]`:

```
gcloud sql users create wagtail none --instance=wagae --password=[DB_PASSWORD]
gcloud sql databases create wagtail --instance=wagae
```

### Install the Cloud SQL proxy

This is necessary so Wagtail can connect to its database to run migrations and 
other operations on the local machine.

On 64-bit Linux:

```
curl -Lo cloud_sql_proxy https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 
chmod 755 cloud_sql_proxy
```

For other platforms, see the
[https://cloud.google.com/python/django/flexible-environment#install_the_sql_proxy](GCP documentation)
for download links.

Enable application default credentials in the GCP SDK:

```
gcloud auth application-default login
```

Fetch the instance connection name for the database you created:

```
gcloud sql instances describe wagae --format='value(connection_name)'
torchkube:europe-west2:wagae
```

Replace `[CONNECTION_NAME]` with the connection name.

## Create Google Storage buckets

GCS will be used to store static assets and uploaded media.  Create two new
buckets, using a common prefix:

```
gsutil mb gs://my-wagtail-site-static
gsutil mb gs://my-wagtail-site-media
```

Configure CORS headers on the static bucket so fonts can be loaded from the
site's domain, and make the contents of both buckets readable by default:

```
gsutil cors set cors.json gs://my-wagtail-site-static
gsutil defacl set public-read gs://my-wagtail-site-static
gsutil defacl set public-read gs://my-wagtail-site-media
```

## Configure local settings

Create a file called `wagae/settings/local.py`, and add your site-specific
settings:

```
DB_CONNECTION_NAME = '[CONNECTION_NAME]'
DB_PASSWORD = '[DB_PASSWORD]'
GS_BUCKET_PREFIX = '[BUCKET_PREFIX]'
GS_PROJECT_ID = '[GCP_PROJECT_ID]'
SECRET_KEY = '[SECRET_KEY]'
```

`[GCP_PROJECT_ID]` is the name of your GCP project.  `[BUCKET_PREFIX]` is the
common prefix of the two GCS buckets you created, e.g. `my-wagtail-site`.

`[SECRET_KEY]` should be a long string of random bytes, e.g. generated by
`pwgen -s 64 1`.

## Install the database tables

1. Run Cloud SQL Proxy in a separate terminal:

`./cloud_sql_proxy -instances="[CONNECTION_NAME]=tcp:5432"`

2. Create Wagtail's database tables and an initial user:

```
./manage.py migrate
./manage.py createsuperuser
```

## Upload static files

Ideally, we would let `django-storages` upload static files for us, but
currently it doesn't seem to handle directory paths properly, which breaks asset
loading.  Instead, collect the static files locally and upload them by hand:

```
./manage.py collectstatic --noinput
gsutil -m rsync -R static/ gs://my-wagtailsite-static/
```

## Check everything works locally

`./manage.py runserver`

You should be able to log in to the Wagtail admin interface at
http://127.0.0.1:8000/admin/ with the user details you have just created.

## Deploy to App Engine

Edit `app.yaml` and set `[CONNECTION_NAME]` to the Cloud SQL database connection
name.

Then deploy the application:

```
gcloud app deploy
```

## Set storage permissions

Now that App Engine has created the service account for the application, set the
correct permissions on the media bucket so file uploads will work:

```
gsutil -m acl ch -u [PROJECT_NAME]@appspot.gserviceaccount.com:O gs://[BUCKET_PREFIX]-media
```

## Hardening

1. Once you know the production domain for your site, specify this in
   `ALLOWED_HOSTS` and `BASE_URL`.
1. Update the origin in cors.json and rerun `gsutil cors set cors.json`
1. Google auth
1. Search
1. Email?
1. SSG to Firebase
