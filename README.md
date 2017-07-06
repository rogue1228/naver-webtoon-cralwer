# 설치
BeautifulSoup4 파싱 라이브러리 설치
`pip3 install bs4`

Python Imaging Library 이미지 처리 라이브러리 설치 
`pip3 install pillow`

# 사용법

## add
`http://comic.naver.com/webtoon/list.nhn?titleId=119874&weekday=fri`
웹툰 URL에서 `titleId`를 복사합니다.
`python3 webtoonCrawlerManager.py add {titleId}`를 입력합니다.

## list
추가한 {titleId} 리스트와 웹툰제목이 리스트로 출력 됩니다.

## remove
`python3 webtoonCrawlerManager.py remove {titleId}`
삭제할 {titleId}를 입력합니다.

## crawl
`python3 webtoonCrawlerManager.py crawl`
입력한 웹툰 모두를 수집합니다.
