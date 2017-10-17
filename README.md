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
mkvirtualenv wagtail-appengine-demo # or your preferred method of creating a virtualenv
pip install -r requirements.txt
```

## Prepare a Cloud SQL database

Using the [Google Cloud instructions](https://cloud.google.com/python/django/flexible-environment#install_the_sql_proxy), install the Cloud SQL proxy, create a Cloud SQL instance (with PostgreSQL), create a database user called `wagtail_user` and a database called `wagtail`.

Record the `Instance connection name` from the Overview tab of the Cloud SQL console.

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

You should be able to log in to the Wagtail admin interface at http://127.0.0.1:8000/admin/ with the user details you have just created.

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