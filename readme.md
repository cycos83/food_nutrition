0. git을 클론합니다.

1. 가상환경을 설치합니다.
$ cd 해당_디렉토리
$ python3 -m venv venv
$ source venv/bin/activate
이후로 작업은 항상 3번쨰 명령어를 이용하여 가상환경으로 접속한 후 합니다.

2. 먼저 의존성 패키지를 설치합니다.

pip 명령어를 이용합니다. pip install -r requirements.txt

(우분투 버전 16.04에서는 pip 대신 pip3를 이용)

3. db를 생성합니다.

$ python manage_tool.py 
Please Input command. 1 is insert_data(xlsx), 2 is init db. 3 is image-resize!
2 (<<<- 2를 입력합니다.)
Successfully initiatied!

4. 서버를 켭니다.

$ python3 server_on.py&

백그라운드로 돌아가게 됩니다.

5. 서버를 자동 실행되게 등재합니다.

$ crontab -e

처음 실행시 3 -> bim.basic 을 선택합니다.
@reboot sh ~/food_nutrition/autorun.sh
을 추가하고 저장합니다.


6. 차후 개발를 합니다.
다른 분이 차후 개발하게 될 경우
https://github.com/hajinhoe/food_nutrition
를 포크하셔서 개발을 진행해주시면 되겠습니다.

번외)

A. 기술 문서파일은 static/docs에 올리면 별도의 작업 필요 없이 반영됩니다.
B. zip 파일은 git 페이지에서 바로 받을 수 있습니다.
C. 기술 문서 페이지에 들어가면 에러가 나요.