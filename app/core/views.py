import mimetypes
import shutil
import tempfile
from pathlib import Path

from eduone_cdn.app.auth.jwt_decoder import get_superuser, get_user
from eduone_cdn.app.core.schemas import DeleteScheme, Avatar
from eduone_cdn.app.core.tasks import (
    compress_image,
    compress_video,
    compress_file,
    delete_file,
    delete_files_in_folder,
)
from eduone_cdn.app.settings.global_variables import (
    VIDEO,
    IMAGE,
    DIRECTORY_FOR_COMPRESS,
)
from eduone_cdn.app.core.validators import (
    get_course,
    get_achievement,
    get_post,
    validate_avatar_inputs,
)
from eduone_cdn.app.core.files import UploadFileTarget, FileTarget2, abspath
from fastapi import APIRouter, Depends
from fastapi import File, UploadFile, status, HTTPException
from fastapi.responses import JSONResponse
from starlette.requests import Request
from streaming_form_data import StreamingFormDataParser
from eduone_cdn.app.core.helper_functions import (
    upload_meta_of_user_avatar,
    generate_avatar_root,
    upload_meta_of_image_post,
    generate_image_root,
)


router = APIRouter()


@router.post("/cdn/upload/file", tags=['File'], dependencies=[Depends(get_superuser)])
async def upload(request: Request):
    parser = StreamingFormDataParser(request.headers)
    target = UploadFileTarget(DIRECTORY_FOR_COMPRESS)
    try:
        parser.register("file", target)
        async for chunk in request.stream():
            parser.data_received(chunk)
        suffix = Path(target.filename).suffix
        tmp_path = abspath(target.filename)
        if target.filename:
            shutil.move(target.file.file.name, tmp_path)
        else:
            raise HTTPException(422, "Could not find file in body")
        mime = mimetypes.guess_type(tmp_path)[0]
        mime_type = mime.split('/')[0]
        if mime_type == IMAGE:
            compress_image.apply_async(
                args=(tmp_path, "images/", mime_type), queue='queue1'
            )
        elif mime_type == VIDEO:
            compress_video.apply_async(args=(tmp_path, mime_type), queue='queue1')
        else:
            compress_file.apply_async(
                args=(tmp_path, suffix, mime_type), queue='queue1'
            )
    finally:
        await target.file.close()
    return JSONResponse(status_code=status.HTTP_201_CREATED)


@router.post("/cdn/upload/avatar", tags=['Avatar'])
def upload_avatar(
    file: UploadFile = File(...), validated: list = Depends(validate_avatar_inputs)
):
    user_id, course_id, achievement_id = validated[0], validated[1], validated[2]
    suffix = Path(file.filename).suffix
    try:
        f = tempfile.NamedTemporaryFile(
            suffix=suffix, dir=DIRECTORY_FOR_COMPRESS, delete=False
        )
        tmp_path = f.name
        with open(tmp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        schema = {"achievement_id": achievement_id, "course_id": course_id}
        root_dir = generate_avatar_root(schema, user_id=user_id)
        res = delete_files_in_folder.apply_async(args=(root_dir), queue='queue1')
        res.get()
        lst = compress_image.apply_async(
            args=(tmp_path, root_dir, "image"), queue='queue1'
        )
        lst = lst.get()
        data = {
            "url": lst[0],
            "key": lst[1],
            "title": "avatar",
            "user_id": user_id,
            "course_id": course_id,
            "achievement_id": achievement_id,
        }
        upload_meta_of_user_avatar(data)
    except Exception:
        raise HTTPException(status_code=500, detail="Some error in uploading")
    return JSONResponse(status_code=status.HTTP_201_CREATED)


@router.post("/cdn/upload/image/post", tags=['Post'])
def upload_image(file: UploadFile = File(...), post_id: list = Depends(get_post)):
    suffix = Path(file.filename).suffix

    try:
        f = tempfile.NamedTemporaryFile(
            suffix=suffix, dir=DIRECTORY_FOR_COMPRESS, delete=False
        )
        tmp_path = f.name
        with open(tmp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        root_dir = generate_image_root(post_id=post_id)
        lst = compress_image.apply_async(
            args=(tmp_path, root_dir, "image"), queue='queue1'
        )
        lst = lst.get()
        data = {
            "url": lst[0],
            "key": lst[1],
            "title": "image",
            "post_id": post_id,
        }
        upload_meta_of_image_post(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Some error in uploading {e}")
    return JSONResponse(status_code=status.HTTP_201_CREATED)


@router.delete('/cdn/delete/file', tags=['File'], dependencies=[Depends(get_superuser)])
def delete_cdn_file(delete_scheme: DeleteScheme):
    response = delete_file.apply_async(args=(delete_scheme.cdn_key), queue='queue1')
    return response.get()
