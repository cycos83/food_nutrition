1. 먼저 의존성 패키지를 설치합니다.

pip 명령어를 이용합니다. pip install -r requirements.txt
또한 gevent를 추가로 설치합니다.
pip install gevent

(우분투 버전 16.04에서는 pip 대신 pip3를 이용)

2. 서버를 켭니다.

python3 server_on.py&

백그라운드로 돌아가게 됩니다.

3. 서버를 자동 실행되게 등재합니다.

crontab -e

처음 실행시 3 -> bim.basic 을 선택합니다.
@reboot sh ~/food_nutrition/autorun.sh
을 추가하고 저장합니다.


4. 차후 개발를 합니다.
다른 분이 차후 개발하게 될 경우
https://github.com/hajinhoe/food_nutrition
를 포크하셔서 개발을 진행해주시면 되겠습니다.
