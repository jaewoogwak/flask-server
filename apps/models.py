import os
from redis import Redis

# 환경 변수에서 REDIS_ENDPOINT 값 불러오기
redis_host = os.getenv('REDIS_ENDPOINT')

# Redis 클라이언트 설정 (retriever 저장용)
redis_client_retriever = Redis(
    host=redis_host,
    port=6379,
    db=0
)

# Redis 클라이언트 설정 (학교메일 인증코드 저장용)
redis_client_auth = Redis(
    host=redis_host,
    port=6379,
    db=1
)