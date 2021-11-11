from eduone_cdn.app.core.helper_functions import (
    upload_meta_of_user_avatar,
    generate_avatar_root,
    check,
    upload_meta_of_image_post,
    generate_image_root,
    check_post,
)
from fastapi import Depends
from typing import Optional
from fastapi import HTTPException
from eduone_cdn.app.auth.jwt_decoder import get_user, check_is_user


async def get_post(post_id: int, user: str = Depends(get_user)):
    if post_id:
        check_post_exists = check_post(user_id=user, post_id=post_id)
        if not check_post_exists:
            raise HTTPException(
                status_code=400,
                detail={"message": "Post does not exist or You are not owner of post"},
            )
    else:
        raise HTTPException(
            status_code=400,
            detail={"message": "Post does not exist"},
        )
    return post_id


async def get_course(course_id: Optional[int] = None):
    if course_id:
        check_course_exists = check(course_id=course_id)
        if not check_course_exists:
            raise HTTPException(
                status_code=400, detail={"message": "Course does not exist"}
            )
    return course_id


async def get_achievement(achievement_id: Optional[int] = None):
    if achievement_id:
        check_ach_exists = check(achievement_id=achievement_id)
        if not check_ach_exists:
            raise HTTPException(
                status_code=400, detail={"message": "Achievement does not exist"}
            )


async def validate_avatar_inputs(
    achievement_id: Optional[int] = None,
    course_id: Optional[int] = None,
    user_id: str = Depends(get_user),
):
    if achievement_id:
        check_ach_exists = check(achievement_id=achievement_id)
        if not check_ach_exists:
            raise HTTPException(
                status_code=400, detail={"message": "Achievement does not exist"}
            )
        checker = await check_is_user(user_id, is_superuser=True)
        if checker != "True":
            raise HTTPException(status_code=403, detail="Not enough privileges")

    if course_id:
        check_course_exists = check(course_id=course_id, user_id=user_id)
        if not check_course_exists:
            raise HTTPException(
                status_code=400,
                detail={"message": "Course does not exist or You are not owner"},
            )
    return [user_id, course_id, achievement_id]
