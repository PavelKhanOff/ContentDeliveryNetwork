import os
import subprocess
import tempfile
import uuid
from typing import Optional
from eduone_cdn.app.core.modules import ProgressPercentage
import boto3
import pyvips
from boto3.s3.transfer import TransferConfig
from eduone_cdn.app.core.helper_functions import get_video_duration
from eduone_cdn.app.settings.config import (
    AWS_REGION_NAME,
    AWS_ENDPOINT_URL,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    ROOT_FOR_VIDEO,
    ROOT_FOR_FILE,
    ROOT_FOR_IMAGE,
    BUCKET_STATIC,
    AWS_ENDPOINT_URL_FOR_GETTER,
)
from eduone_cdn.app.settings.global_variables import MIMETYPES_TO_COMPRESS
from eduone_cdn.app.task_app.celery_app import app


session = boto3.session.Session()
client = session.client(
    's3',
    region_name=AWS_REGION_NAME,
    endpoint_url=AWS_ENDPOINT_URL,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

DIRECTORY_FOR_COMPRESS = '/compress_dir/'

MP_THRESHOLD = 1
MP_CONCURRENCY = 5
MAX_RETRY_COUNT = 3
GB = 1024 ** 3


def upload_file_to_cdn(
    tmp_path: str, cdn_key_name: str, output_path: Optional[str] = None
):
    url = AWS_ENDPOINT_URL_FOR_GETTER + "/" + cdn_key_name
    try:
        mp_threshold = MP_THRESHOLD * GB
        concurrency = MP_CONCURRENCY
        transfer_config = TransferConfig(
            multipart_threshold=mp_threshold,
            use_threads=True,
            max_concurrency=concurrency,
        )

        client.upload_file(
            output_path,
            BUCKET_STATIC,
            cdn_key_name,
            ExtraArgs={'ACL': 'public-read'},
            Config=transfer_config,
            Callback=ProgressPercentage(output_path),
        )

    except Exception as e:
        print(e)
    finally:
        os.unlink(output_path)
        if tmp_path:
            os.unlink(tmp_path)
    return (url, cdn_key_name)


@app.task
def compress_image(tmp_path: str, root_dir: str, mime_type: str):
    output_path = tempfile.NamedTemporaryFile(
        suffix=MIMETYPES_TO_COMPRESS['image_format'],
        dir=DIRECTORY_FOR_COMPRESS,
        delete=False,
    )
    cdn_key_name = root_dir + str(uuid.uuid4()) + MIMETYPES_TO_COMPRESS['image_format']

    image = pyvips.Image.new_from_file(tmp_path, access="sequential")
    for name in image.get_fields():
        image.remove(name)
    image.webpsave(output_path.name, Q=60)
    lst = upload_file_to_cdn(tmp_path, cdn_key_name, output_path.name)
    return lst


@app.task
def compress_video(tmp_path: str, mime_type: str):
    output_path = tempfile.NamedTemporaryFile(
        suffix=MIMETYPES_TO_COMPRESS['video_format'],
        delete=False,
        dir=DIRECTORY_FOR_COMPRESS,
    )
    cdn_key_name = (
        ROOT_FOR_VIDEO + '/' + str(uuid.uuid4()) + MIMETYPES_TO_COMPRESS['video_format']
    )
    try:
        command = (
            f'ffmpeg -y -i {tmp_path} '
            f'-i eduone_cdn/eduone_logo_trans.png -filter_complex "overlay=10:main_h-overlay_h-10" '
            f'-c:v libvpx-vp9 '
            f' -crf 33 -b:v 0 -cpu-used -6 -threads 8  -tile-columns 1 -row-mt 1 -c:a libopus {output_path.name}'
        )
        subprocess.call(command, shell=True)
        get_video_duration(tmp_path)
    except Exception as e:
        raise e
    url = upload_file_to_cdn(tmp_path, cdn_key_name, output_path.name)
    return url


@app.task
def compress_file(tmp_path: str, suffix: str, mime_type: str):
    cdn_key_name = ROOT_FOR_FILE + '/' + str(uuid.uuid4()) + suffix
    url = upload_file_to_cdn(
        tmp_path=None, cdn_key_name=cdn_key_name, output_path=tmp_path
    )
    return url


# DELETE FILES FROM AWS
@app.task
def delete_file(cdn_key: str):
    response = client.delete_object(Bucket=BUCKET_STATIC, Key=cdn_key)
    return response


@app.task
def delete_files_in_folder(cdn_key: str):
    response = client.list_objects(Bucket=BUCKET_STATIC, Prefix=cdn_key)
    if not response.get('Contents'):
        return "Not Found"
    for obj in response.get('Contents'):
        client.delete_object(Bucket=BUCKET_STATIC, Key=obj['Key'])
    return response
