# YouTube Subs (Infrastructure)

## Overview

This folder is the home to the infrastructure necessary to run the YouTube Subs CLI tool.
The Infrastructure as Code (IaC) tool being used is [Pulumi](https://www.pulumi.com/),
and the language in which the infra configurations have been written is Python
([Python's venv](https://docs.python.org/3/library/venv.html) is utilized to manage project dependencies).

### Business logic

1. Through Pulumi we activate [GCP's Speech-to-Text service](https://cloud.google.com/speech-to-text/),
2. and create a [GCS bucket](https://cloud.google.com/storage/docs/buckets)
containing `temporary_bucket_for_audio_files` in its name.

## Prerequisites

* [a Google Cloud Platform (GCP) account](https://cloud.google.com/)
  * **WARNING!!! YOU WILL BE CHARGED FOR GCP USAGE!!!**
  * [gcloud CLI installed and initialized](https://cloud.google.com/sdk/docs/install)
  * [Application Default Credentials (ADC) provided](https://cloud.google.com/docs/authentication/provide-credentials-adc)
* [Pulumi](https://www.pulumi.com/)
  * [Pulumi Service account](https://www.pulumi.com/docs/intro/pulumi-service/)
  * [Pulumi CLI v3.51 or higher](https://www.pulumi.com/docs/get-started/install/)
  * `gcp:region` (plaintext) and `gcp:project` (encrypted) values set accordingly in the `Pulumi.prod.yaml` file
* [Python v3.10 or higher](https://www.python.org/)

## Usage

**a)** Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**b)** Log into the Pulumi Service

```bash
pulumi login
```

**c)** Preview the infrastructure changes

```bash
pulumi preview
```

**d)** Deploy the infrastructure changes

```bash
pulumi up
```

**e)** Destroy the infrastructure changes

```bash
pulumi destroy
```

## Additional reading

* [Pulumi state and backends](https://www.pulumi.com/docs/intro/concepts/state/)
* [Pulumi Frequently Asked Questions (FAQs)](https://www.pulumi.com/docs/support/faq/)
