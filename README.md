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

## Update your database settings

Replace `<DB PASSWORD>` and `<INSTANCE CONNECTION NAME>` in `wagae/settings/base.py`.

## Install the database tables

1. Run Cloud SQL Proxy in a separate terminal:

`./cloud_sql_proxy -instances="<INSTANCE CONNECTION NAME>"=tcp:5432`

2. Create Wagtail's database tables and an initial user:

```
./manage.py migrate
./manage.py createsuperuser
```

## Check everything works locally

`./manage.py runserver`

The styling will be broken, but you should be able to log in to the Wagtail admin interface at http://127.0.0.1:8000/admin/ with the user details you have just created.

## Create a bucket for static content

```
gsutil mb gs://<GCS BUCKET NAME>
gsutil defacl set public-read gs://<GCS BUCKET NAME>
gsutil cors set cors.json gs://<GCS BUCKET NAME>
```

Update `STATIC_URL` in `wagae/settings/base.py`:

```python
STATIC_URL = 'https://storage.googleapis.com/<GCS BUCKET NAME>/static/'
```

and copy the files across:

```
gsutil rsync -R static/ gs://<GCS BUCKET NAME>/static
```

## Configure the app for App Engine

Set `<INSTANCE CONNECTION NAME>` in `app.yaml`.

In `settings/base.py`, update `<GCS BUCKET NAME>` and `<GCP PROJECT ID>`, 
and set `<YOUR SECRET KEY>`, e.g. using

```python
import random
''.join([random.SystemRandom().choice(
    'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    ) for i in range(50)])
```

Deploy your site with `gcloud app deploy`.

## Hardening

1. Once you know the production domain for your site, specify this in `ALLOWED_HOSTS` and `BASE_URL`.
1. Update the origin in cors.json and rerun `gsutil cors set cors.json`
1. Google auth
1. Search
1. Email?
1. SSG to Firebase
