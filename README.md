# bentley

## 로깅(Logging)

`post_to_blogger` 함수는 Blogger 포스팅 성공/실패 여부를 Python logging 모듈을 통해 기록합니다.

- **성공 시**: INFO 레벨로 "Post created successfully! Post ID, URL" 메시지 출력
- **실패 시**: ERROR 레벨로 "An error occurred while posting to Blogger: ..." 메시지 출력

기본적으로 로그는 콘솔에 출력되며, 필요에 따라 logging 설정을 변경하여 파일로 저장할 수도 있습니다.

예시:
```
INFO:root:Post created successfully! Post ID: 1234567890, URL: https://yourblog.blogspot.com/2024/06/your-post.html
ERROR:root:An error occurred while posting to Blogger: ...
```

## 환경 변수(Environment Variables) 설정

Blogger 자동 포스팅을 위해 아래 환경 변수들이 필요합니다.

| 변수명                        | 설명                                      |
|------------------------------|------------------------------------------|
| `GOOGLE_CLIENT_ID`           | Google Cloud Console에서 발급받은 OAuth Client ID |
| `GOOGLE_CLIENT_SECRET`       | Google Cloud Console에서 발급받은 OAuth Client Secret |
| `BLOGGER_BLOG_ID`            | Blogger 블로그의 ID (숫자)                |
| `BLOGGER_TOKEN_PICKLE_B64`   | (선택) base64로 인코딩된 token.pickle 값 (GitHub Actions 등 자동화 시 사용) |

### 1. 로컬에서 최초 인증 및 token.pickle 생성

1. 환경 변수 설정 (예시, bash/zsh)
    ```bash
    export GOOGLE_CLIENT_ID="your-client-id"
    export GOOGLE_CLIENT_SECRET="your-client-secret"
    export BLOGGER_BLOG_ID="your-blog-id"
    ```
2. `python src/post_blogger.py` 실행  
   → 브라우저가 열리면 Google 계정으로 로그인 및 권한 허용  
   → 실행 후 `src/token.pickle` 파일이 생성됨

### 2. GitHub Actions에서 자동화 (환경변수로 인증)

1. 로컬에서 생성된 `token.pickle`을 base64로 인코딩
    ```bash
    base64 -i src/token.pickle
    ```
    출력된 문자열을 복사

2. GitHub 저장소 > Settings > Secrets and variables > Actions에서  
   `BLOGGER_TOKEN_PICKLE_B64` 이름으로 base64 문자열을 등록

3. GitHub Actions workflow에서 아래와 같이 환경변수로 사용
    ```yaml
    env:
      GOOGLE_CLIENT_ID: ${{ secrets.GOOGLE_CLIENT_ID }}
      GOOGLE_CLIENT_SECRET: ${{ secrets.GOOGLE_CLIENT_SECRET }}
      BLOGGER_BLOG_ID: ${{ secrets.BLOGGER_BLOG_ID }}
      BLOGGER_TOKEN_PICKLE_B64: ${{ secrets.BLOGGER_TOKEN_PICKLE_B64 }}
    ```

### 참고
- `token.pickle`은 Google OAuth 인증 토큰이므로 **절대 외부에 노출되지 않도록 주의**하세요.
- 블로그 ID는 Blogger 대시보드 URL에서 확인할 수 있습니다.  
  예: `https://www.blogger.com/blog/post/edit/12345678901234567890/12345678901234567890`  
  → 여기서 첫 번째 숫자가 블로그 ID입니다.
