# 2. 이 폴더는 무조건 파이썬 3.14 쓰도록 고정
uv venv --python 3.12 --allow-existing
# 3. 파이썬 3.14 가상환경 생성 및 활성화
uv venv
source .venv/Scripts/activate

# 2. Pygame 설치
uv add pygame --python 3.12

uv pip install pygame