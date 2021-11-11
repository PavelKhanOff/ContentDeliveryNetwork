import math
import re
from subprocess import check_output
import requests
from eduone_cdn.app.settings.config import (
    CORE_UPLOAD_PROFILE_AVATAR,
    CORE_CHECK_ACHIEVEMENT,
    CORE_CHECK_COURSE,
    CORE_UPLOAD_IMAGE_POST,
    FEED_URL_CHECK_POST,
)
import orjson


def get_video_duration(path_video: str):
    # Create the command for getting the information of the input video via ffprobe.
    cmd = ['ffprobe', '-show_format', '-pretty', '-loglevel', 'quiet', path_video]
    # Get the information of the input video via ffprobe command.
    info_byte = check_output(cmd)  # <bytes>
    # Decode the information.
    info_str = info_byte.decode("utf-8")  # <str>
    # Split the information.
    info_list = re.split('[\n]', info_str)

    # Get the duration of the input video.
    for info in info_list:
        if 'duration' in info:
            # E.g., 'info' = 'duration=0:00:01.860000'.
            duration = re.split('[=]', info)[1]

    hh, mm, ss = map(float, duration.split(":"))
    duration_in_seconds = hh * 3600 + mm * 60 + ss
    return math.ceil(duration_in_seconds)


def upload_meta_of_user_avatar(request):
    url_for_upload = CORE_UPLOAD_PROFILE_AVATAR
    try:
        requests.post(url=url_for_upload, json=request, timeout=8)
    except requests.exceptions.ConnectionError as e:
        return {'Ошибка': e}
    except Exception as e:
        return {'Ошибка': e}


def upload_meta_of_image_post(request):
    url_for_upload = CORE_UPLOAD_IMAGE_POST
    try:
        requests.post(url=url_for_upload, json=request, timeout=8)
    except requests.exceptions.ConnectionError as e:
        return {'Ошибка': e}
    except Exception as e:
        return {'Ошибка': e}


def generate_avatar_root(request, user_id: str):
    if request["course_id"]:
        root_dir = f"courses/{request['course_id']}/avatar/"
        return root_dir
    if request['achievement_id']:
        root_dir = f"achievements/{request['achievement_id']}/avatar/"
        return root_dir
    root_dir = f"users/{user_id}/avatar/"
    return root_dir


def generate_image_root(post_id: int):
    root_dir = f"posts/{post_id}/images/"
    return root_dir


def check(course_id: int = None, achievement_id: int = None, user_id: str = None):
    params = {}
    if course_id:
        url_for_upload = f'{CORE_CHECK_COURSE}{course_id}'
        params = {"user_id": user_id}
    elif achievement_id:
        url_for_upload = f'{CORE_CHECK_ACHIEVEMENT}{achievement_id}'
    try:
        response = requests.get(url=url_for_upload, params=params, timeout=8)
    except requests.exceptions.ConnectionError as e:
        return {'Ошибка': e}
    except Exception as e:
        return {'Ошибка': e}
    data = orjson.loads(response.text).get('message')
    if data == "True":
        return True
    return False


def check_post(post_id: int, user_id):
    url_for_check = FEED_URL_CHECK_POST
    try:
        response = requests.get(
            url=url_for_check,
            params={"user_id": user_id, "post_id": post_id},
            timeout=8,
        )
    except Exception as e:
        return {'Ошибка': e}
    return response.json()
