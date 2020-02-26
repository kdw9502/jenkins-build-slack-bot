# jenkins-build-slack-bot

jenkins-build-slack-bot은 슬랙 채팅으로 젠킨스 빌드를 실행시키기 위해 만들어진 아주 간단한 슬랙 봇입니다.

외부 호스팅 서버 없이 로컬에 실행시키기 위해 클래식 앱으로 작성되었습니다.

빌드 시작, 빌드 취소, 파라미터 빌드 시작, 작업목록보기, 실행중인 파이프라인 스테이지 확인을 지원합니다.

## Prerequisites
Python3 after 3.7


## Installing

1. 슬랙에 '클래식' 앱을 추가하세요. [Create](https://api.slack.com/apps?new_classic_app=1)

2. 앱을 설정하고 아래에 있는 스코프들을 추가하세요. (OAth & Permissions 메뉴에 있음)
![scopes](https://user-images.githubusercontent.com/21076531/75315951-7097ca00-58a7-11ea-94d5-8070cf06257e.png)

3. 앱을 워크스페이스에 설치하세요.

4. 깃 디렉토리로 돌아와 의존성을 설치합니다. (가상환경에서 설치하기를 추천드립니다.)
```
pip3 install -r requirements.txt
```
5. 봇을 실행합니다.  Token은 앱 설정에서 OAuth & Permissions 메뉴 상단에서 볼 수 있습니다. 스코프 설정 위에 존재합니다. 
```
python3 StartBot.py [Bot User OAuth Access Token (xoxb)] [OAuth Access Token (xoxp)] [Jenkins URL]
```
6. 봇을 채널에 추가하거나, DM을 보내어 실행시킵니다.

## Example
![example](https://user-images.githubusercontent.com/21076531/75316986-2e23bc80-58aa-11ea-899f-b72e22f3058c.png)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
