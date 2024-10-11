import os
from redis import Redis

# 환경 변수에서 REDIS_ENDPOINT 값 불러오기
# 리더(READER) 엔드포인트는 읽기 전용 엔드포인트
redis_host_reader = os.getenv('REDIS_READER_ENDPOINT')
# 기본(PRIMARY) 엔드포인트는 쓰기 전용 엔드포인트
redis_host_primary = os.getenv('REDIS_PRIMARY_ENDPOINT')

# Redis 클라이언트 설정, retriever 구성 정보 탐색용
redis_client_retriever_reader = Redis(
    host=redis_host_reader,
    port=6379,
    #decode_responses=True,
    db=0
)

# Redis 클라이언트 설정, retriever 저장용
redis_client_retriever_primary = Redis(
    host=redis_host_primary,
    port=6379,
    #decode_responses=True,
    db=0
)

# Redis 클라이언트 설정, 학교메일 인증코드 저장용
redis_client_auth_reader = Redis(
    host=redis_host_reader,
    port=6379,
    #decode_responses=True,
    db=1
)

# Redis 클라이언트 설정, 학교메일 인증코드 삭제용
redis_client_auth_primary = Redis(
    host=redis_host_primary,
    port=6379,
    #decode_responses=True,
    db=1
)