"""A Google Cloud Python Pulumi program"""

import pulumi
from pulumi_gcp import storage, projects

configGcp=pulumi.Config('gcp')

projects.Service(
    resource_name='speech_to_text',
    service='speech.googleapis.com',
    project=configGcp.get('project'),
)

bucket = storage.Bucket(
    resource_name='temporary_bucket_for_audio_files',
    location=configGcp.get('region'),
    public_access_prevention='enforced',
)

# Export the DNS name of the bucket
pulumi.export('bucket_name', bucket.url)
