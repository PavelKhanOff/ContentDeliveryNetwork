import os

# JWT AUTH
SECRET = os.getenv("JWTSECRET", "SOMESECRET")

# AWS(CDN) SETTINGS
BUCKET_STATIC = 'ecdn'
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_ENDPOINT_URL_FOR_GETTER = f"https://{BUCKET_STATIC}.fra1.digitaloceanspaces.com"
# Roots for videos,images,files
ROOT_FOR_VIDEO = 'videos'
ROOT_FOR_IMAGE = 'images'
ROOT_FOR_FILE = 'files'

# Bucket Name for static files


# Postgress
DB_ENGINE = os.environ.get('DB_ENGINE', 'postgresql')
POSTGRES_USER = os.environ.get('POSTGRES_USER', 'admin')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'LOYAg3Wv')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'db')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT', '5432')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'eduonepostgresdb')
GENERAL_NAME = 'general_name'
VARIABLE_NAME = 'variable_name'
TABLE_FILES = 'Files'

# CELERY
REDIS_HOST = os.environ.get("REDIS_HOST", 'redis')
REDIS_PORT = os.environ.get("REDIS_PORT", '6379')
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", 'secrett')
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://admin:mypass@rabbitmq/")
CELERY_BACKEND_URL = (
    "sentinel://sentinel-0.sentinel.default.svc.cluster.local:5000/0;"
    "sentinel://sentinel-1.sentinel.default.svc.cluster.local:5000/0;"
    "sentinel://sentinel-2.sentinel.default.svc.cluster.local:5000/0"
)

# Middleware
MIDDLEWARE_HOST = os.environ.get("MIDDLEWARE_HOST", "middleware-service")
MIDDLEWARE_PORT = os.environ.get("MIDDLEWARE_PORT", 6000)
# CORE
CORE_HOST = os.environ.get("CORE_HOST", "core-service")
CORE_PORT = os.environ.get("CORE_PORT", 8000)
PROTOCOL = 'http'
# FEED
FEED_HOST = os.environ.get("FEED_HOST", "feed-service")
FEED_PORT = os.environ.get("FEED_PORT", 7000)
# UPLOAD
URL_UPLOAD_PROFILE_AVATAR = "core/middleware/upload/avatar"
CORE_UPLOAD_PROFILE_AVATAR = (
    f'{PROTOCOL}://{CORE_HOST}:{CORE_PORT}/{URL_UPLOAD_PROFILE_AVATAR}'
)

URL_UPLOAD_IMAGE_POST = "feed/middleware/upload/image"
CORE_UPLOAD_IMAGE_POST = f'{PROTOCOL}://{FEED_HOST}:{FEED_PORT}/{URL_UPLOAD_IMAGE_POST}'


# Checkers
# CHECK USER
URL_CHECK_SUPER_USER = os.environ.get(
    "URL_CHECK_SUPER_USER", 'middleware/check_superuser'
)
URL_CHECK_USER = os.environ.get("URL_CHECK_SUPER_USER", 'middleware/check_user')
MIDDLEWARE_URL_CHECK_SUPER_USER = (
    f'{PROTOCOL}://{MIDDLEWARE_HOST}:{MIDDLEWARE_PORT}/{URL_CHECK_SUPER_USER}'
)
MIDDLEWARE_URL_CHECK_USER = (
    f'{PROTOCOL}://{MIDDLEWARE_HOST}:{MIDDLEWARE_PORT}/{URL_CHECK_USER}'
)
# CHECK Course
CHECK_COURSE = "core/middleware/check_course_exists/"
CORE_CHECK_COURSE = f'{PROTOCOL}://{CORE_HOST}:{CORE_PORT}/{CHECK_COURSE}'
# CHECK ACHIEVEMENT
CHECK_ACHIEVEMENT = "core/middleware/check_achievement_exists/"
CORE_CHECK_ACHIEVEMENT = f'{PROTOCOL}://{CORE_HOST}:{CORE_PORT}/{CHECK_ACHIEVEMENT}'
# CHECK POST
URL_CHECK_POST = "feed/middleware/post/check"
FEED_URL_CHECK_POST = f'{PROTOCOL}://{FEED_HOST}:{FEED_PORT}/{URL_CHECK_POST}'
