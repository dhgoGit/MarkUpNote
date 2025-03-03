# MarkUpNote
"이미지를 마크업 언어로 변환하는 노트"

# 시스템 요구사항
- Windows 10 이상
- Python 3.8 이상
- Microsoft Visual C++ Redistributable 2015-2022 (x64)
  - 다운로드: https://aka.ms/vs/17/release/vc_redist.x64.exe
  - 또는 winget으로 설치: `winget install Microsoft.VCRedist.2015+.x64`

# 실행 방법
1. 시스템 요구사항 설치 (위 참조)
2. Python 의존성 패키지 설치:
```bash
pip install -r requirements.txt
```

### 2. Hugging Face 토큰 설정
1. https://huggingface.co/settings/tokens 에서 새 토큰 생성
2. `util/access_token/token` 파일을 생성하고 토큰 붙여넣기:
   ```bash
   # Windows
   mkdir -p util/access_token
   echo "your-token-here" > util/access_token/token
   
   # Linux/Mac
   mkdir -p util/access_token
   echo "your-token-here" > util/access_token/token
   ```
3. 이 파일은 실수로 노출되는 것을 방지하기 위해 .gitignore에 포함되어 있습니다.
