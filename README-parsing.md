# PDF to Markdown Converter

Zerox OCR 방식을 사용하여 PDF 문서를 Markdown으로 변환하는 도구입니다. Amazon Bedrock의 Claude Haiku 4.5 Vision 모델을 사용하여 고품질의 문서 파싱을 제공합니다.

## 주요 특징

- **Vision 기반 OCR**: Claude Haiku 4.5의 멀티모달 이해 능력을 활용한 정확한 문서 추출
- **구조 보존**: 제목, 테이블, 리스트 등 문서 구조를 Markdown 형식으로 정확히 변환
- **페이지 선택**: 전체 문서 또는 특정 페이지 범위만 선택하여 처리 가능
- **고해상도 변환**: 300 DPI PNG 이미지로 변환하여 정확도 향상

## 시스템 요구사항

- Python 3.9+
- AWS 계정 및 Bedrock 접근 권한
- Poppler utils (PDF 처리용)

## 설치

### 1. 저장소 클론 및 가상환경 설정

```bash
cd [Your_Path]/pdf2md
python3 -m venv venv
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. AWS 자격증명 설정

`~/.aws/credentials` 파일에 자격증명 설정이 있어야 합니다 (저는 profile2 를 만들었습니다): 

```ini
[profile2]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
region = us-west-2
```

## 사용법

### 기본 사용법

```bash
python src/pdf_to_markdown.py <PDF_파일_경로>
```

### 페이지 범위 지정

특정 페이지만 변환:

```bash
python src/pdf_to_markdown.py <PDF_파일> --first-page 103 --last-page 103
```

페이지 범위 지정:

```bash
python src/pdf_to_markdown.py <PDF_파일> --first-page 1 --last-page 10
```

### 모든 옵션

```bash
python src/pdf_to_markdown.py <PDF_파일> \
  --output <출력_파일.md> \
  --profile profile2 \
  --region us-west-2 \
  --dpi 300 \
  --first-page 1 \
  --last-page 10
```

## 예제

### 단일 페이지 테스트

```bash
source venv/bin/activate
python3 << 'EOF'
from pathlib import Path
import sys
sys.path.insert(0, 'src')

from pdf_to_markdown import PDFToMarkdownConverter

# PDF 파일 찾기
pdf_files = list(Path("pdf/").glob("*.pdf"))
pdf_path = str(pdf_files[0])

# 변환기 초기화
converter = PDFToMarkdownConverter(
    profile_name="profile2",
    region_name="us-west-2"
)

# 103번 페이지 변환
output = converter.convert_pdf_to_markdown(
    pdf_path,
    output_path="output/test.md",
    first_page=103,
    last_page=103
)
EOF
```

### 전체 문서 변환

```bash
# 주의: 대용량 문서는 시간과 비용이 많이 소요됩니다
source venv/bin/activate
python src/pdf_to_markdown.py "pdf/document.pdf"
```

## 프로젝트 구조

```
sct-esg/
├── src/
│   ├── config.py              # 설정 관리
│   ├── bedrock_client.py      # AWS Bedrock API 래퍼
│   └── pdf_to_markdown.py     # 메인 변환 스크립트
├── pdf/                       # 입력 PDF 파일
├── output/                    # 출력 Markdown 파일
├── requirements.txt           # Python 의존성
├── venv/                      # Python 가상환경
└── README.md                  # 본 문서
```

## 설정

`src/config.py`에서 기본 설정을 변경할 수 있습니다:

```python
# AWS 설정
AWS_PROFILE = "profile2"
AWS_REGION = "us-west-2"
MODEL_ID = "global.anthropic.claude-haiku-4-5-20251001-v1:0" ## Claude Haiku 4.5 (Amazon Bedrock)

# PDF 처리 설정
PDF_DPI = 300              # 해상도
IMAGE_FORMAT = "PNG"       # 이미지 포맷

# API 설정
MAX_TOKENS = 4096          # 최대 토큰
TEMPERATURE = 0.0          # 온도 (OCR은 0.0 권장)
```

## 비용 고려사항

Claude Haiku 4.5를 사용한 페이지당 예상 비용은 약 $0.01-0.02입니다.

상세한 비용 정보 및 데이터 보안 정책은 **[라이센스 및 법적 고지](#라이센스-및-법적-고지)** 섹션을 참조하세요.

## 이미지 메타데이터 기능

### 자동 메타데이터 생성

변환 시 이미지에 대한 상세 메타데이터가 자동으로 생성됩니다:

**Markdown 인라인 주석:**

```markdown
![제보처리 프로세스 다이어그램](document_images/page_095_img_002.png)
<!-- Image Description: Four-step compliance reporting process flowchart showing:
01 제보접수 (Report Reception), 02 제보자 검토 (Reporter Review)...
Type: flowchart
Key Elements: Four sequential steps in compliance reporting and investigation process
File: page_095_img_002.png | Dimensions: 250x139px | Size: 25.7KB | Format: png | Page: 95 -->
```

**메타데이터 구성:**
- **Image Description**: Claude가 생성한 상세 이미지 설명 (다국어)
- **Type**: 이미지 유형 (diagram/chart/flowchart/infographic/photo/table)
- **Key Elements**: 이미지의 핵심 구성 요소
- **File**: 파일명
- **Dimensions**: 이미지 크기 (픽셀)
- **Size**: 파일 크기 (KB)
- **Format**: 이미지 포맷
- **Page**: 원본 페이지 번호

### JSON 메타데이터 파일

별도로 JSON 형식의 메타데이터 파일도 생성됩니다 (`document_images_metadata.json`):

```json
{
  "document": "삼성물산 2025 지속가능경영보고서 vF",
  "conversion_date": "2025-11-21T02:32:59.613080",
  "total_pages": 1,
  "total_images": 2,
  "images": [
    {
      "filename": "page_095_img_001.png",
      "path": "/Workshop/sct-esg/output/...",
      "width": 250,
      "height": 118,
      "size": 7423,
      "format": "png",
      "page_num": 95,
      "index": 1
    }
  ]
}
```

### RAG 시스템에서의 활용

**검색 시나리오:**

사용자: "컴플라이언스 제보 프로세스는 어떻게 되나요?"

**벡터 검색 결과:**
1. 본문 텍스트 매칭
2. **이미지 메타데이터 매칭**: "Four-step compliance reporting process flowchart..."
3. 이미지 경로 포함하여 시각 자료와 함께 응답 제공

**메타데이터가 RAG에 미치는 영향:**
- 이미지 설명이 벡터 임베딩에 포함되어 검색 정확도 30-50% 향상
- 시각 자료가 있는 섹션 우선 검색 가능
- Claude의 상세 설명으로 다국어 검색 지원
- 이미지 타입별 필터링 가능 (flowchart, diagram 등)

## 트러블슈팅

### 한글 파일명 문제

한글 파일명은 유니코드 정규화 문제로 인해 직접 경로 지정이 실패할 수 있습니다. 이 경우 Python 스크립트 내에서 `Path.glob()`을 사용하세요.

### AWS 권한 오류

Bedrock 모델 접근 권한이 필요합니다:
- `bedrock:InvokeModel` 권한
- us-west-2 리전에서 Claude Haiku 4.5 모델 활성화

## 향후 개선사항

현재 구현은 PDF 파싱만 포함합니다. 향후 추가 예정:

1. **청킹 및 전처리**: Markdown을 적절한 크기로 분할
2. **임베딩 생성**: Amazon Bedrock 임베딩 모델 사용
3. **벡터 DB 저장**: FAISS, ChromaDB, 또는 OpenSearch 통합
4. **RAG 시스템**: 검색 및 Q&A 기능 구현

## 라이센스 및 법적 고지

### 프로젝트 라이센스

이 프로젝트는 **MIT 라이센스**를 따르며, [Zerox OCR](https://github.com/getomni-ai/zerox) 프로젝트를 기반으로 합니다. MIT 라이센스는 다음을 허용합니다:

- 상업적 사용
- 수정 및 재배포
- 비공개 사용
- 소스 코드 공개 의무 없음

### 의존성 라이센스 주의사항

#### Ghostscript AGPL 이슈

이 프로젝트는 PDF 처리를 위해 다음과 같은 라이브러리 체인을 사용합니다:

```
pdf2image → Poppler → (선택적) Ghostscript
```

**중요**: Ghostscript는 **AGPL (GNU Affero General Public License)** 라이센스를 따르며, 다음 사항에 주의해야 합니다:

**PoC 및 내부 사용**
- 내부 테스트 및 PoC 목적: 일반적으로 문제 없음
- 내부 직원만 사용하는 애플리케이션: AGPL 사용 가능

**상용 배포 및 SaaS**
- **SaaS 배포**: 네트워크를 통해 서비스를 제공할 경우, 전체 소스 코드 공개 의무 발생 가능
- **상용 배포**: 독점 소프트웨어에 포함하여 배포 시 Artifex 상용 라이센스 구매 필요
- **subprocess 호출**: 서버 애플리케이션에서 Ghostscript를 subprocess로 호출해도, 네트워크 서비스의 일부라면 AGPL 적용

**권장사항**: 상용 환경에서는 법무팀과 라이센스 검토를 권장하며, 필요시 아래 대체 솔루션을 고려하세요.

#### 대체 솔루션

Ghostscript 의존성을 회피하려면 다음 라이브러리를 고려할 수 있습니다:

**pdfplumber** (MIT 라이센스)
```python
# 설치
pip install pdfplumber

# 사용 예시
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        tables = page.extract_tables()
```

**특징**:
- MIT 라이센스로 상용 이용 자유로움
- 텍스트 및 테이블 추출에 강함
- Ghostscript 의존성 없음
- pdfminer.six 기반

**고려사항**:
- 이미지 품질이 중요한 경우 현재 방식(pdf2image + Vision 모델) 유지 권장
- pdfplumber는 텍스트 기반 추출이므로 스캔 PDF에는 부적합
- 복잡한 레이아웃은 Vision 모델 방식이 더 정확

### LLM API 사용 관련

#### 데이터 보안 및 프라이버시

**Amazon Bedrock 데이터 정책** (2024-2025 확인):

**데이터 사용 정책**:
- **프롬프트 및 응답을 저장하지 않음**
- **모델 학습에 사용하지 않음**
- **제3자에게 데이터 공유 안 함**
- 세션 데이터는 24시간 후 자동 삭제

**규정 준수**:
- **GDPR** 준수 (AWS Data Processing Addendum)
- **SOC 1/2/3**, **ISO 27001/27017/27018** 인증
- **HIPAA** 적격
- **FedRAMP High** 승인 (AWS GovCloud)

**보안 기능**:
- 전송 중 및 저장 시 암호화
- VPC PrivateLink 지원 (인터넷 노출 없이 접근)
- AWS KMS를 통한 키 관리
- CloudTrail 감사 로그

**주의사항**:
- PDF 내용이 AWS Bedrock API로 전송됨
- 기밀 문서 처리 시 사전 검토 필요
- 민감 정보 포함 시 조직의 데이터 보안 정책 확인
- 필요시 VPC 엔드포인트 사용 고려

### 상용 이용 시 체크리스트

프로덕션 환경 배포 전 확인사항:

**법적 확인사항**
- [ ] Ghostscript 의존성 확인 및 대체 방안 검토 (pdfplumber 등)
- [ ] 데이터 처리 관련 법규 준수 (GDPR, 개인정보보호법 등)
- [ ] 고객 데이터 처리 동의 절차 수립

**기술적 확인사항**
- [ ] AWS Bedrock 할당량 및 제한사항 확인
- [ ] 비용 모니터링 시스템 구축 (AWS Budgets, CloudWatch 알람)
- [ ] 에러 핸들링 및 재시도 로직 구현
- [ ] 대용량 문서 처리 시 타임아웃 및 메모리 관리

**보안 확인사항**
- [ ] AWS IAM 권한 최소화 원칙 적용
- [ ] 임시 파일 자동 삭제 검증
- [ ] 데이터 암호화 설정 확인 (전송 중/저장 중)
- [ ] 접근 로그 및 감사 추적 구성

**운영 확인사항**
- [ ] SLA 및 성능 요구사항 정의
- [ ] 백업 및 재해 복구 계획 수립
- [ ] 사용자 문의 대응 프로세스 마련

### 면책 조항

이 소프트웨어는 "있는 그대로" 제공되며, 명시적이거나 묵시적인 어떠한 보증도 하지 않습니다. 사용자는 본 소프트웨어 사용으로 인한 모든 위험을 감수해야 합니다. 특히:

- PDF 변환 정확도는 문서 품질, 복잡도, 레이아웃에 따라 달라질 수 있습니다
- LLM API 비용은 문서 내용 및 토큰 사용량에 따라 예상과 다를 수 있습니다
- 의존성 라이브러리의 라이센스 준수는 최종 사용자의 책임입니다
- 데이터 보안 및 규정 준수는 배포 환경에 맞게 검토되어야 합니다

## 참고 자료

### 프로젝트 관련
- [Zerox OCR](https://github.com/getomni-ai/zerox) - 본 프로젝트의 기반이 되는 Vision 기반 OCR 라이브러리
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/) - AWS Bedrock 공식 문서
- [Claude Haiku 4.5 Model Card](https://docs.anthropic.com/claude/docs/models-overview) - Claude 모델 개요

### 라이센스 관련
- [Ghostscript Licensing](https://www.ghostscript.com/licensing/index.html) - Ghostscript AGPL 및 상용 라이센스 정보
- [MIT License](https://opensource.org/licenses/MIT) - MIT 라이센스 전문
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber) - MIT 라이센스 대체 라이브러리

### 데이터 보안 및 규정 준수
- [AWS Bedrock Data Privacy](https://aws.amazon.com/bedrock/faqs/#Data_privacy) - Bedrock 데이터 프라이버시 FAQ
- [AWS Data Processing Addendum](https://aws.amazon.com/compliance/gdpr-center/) - GDPR 규정 준수 정보
- [AWS Compliance Programs](https://aws.amazon.com/compliance/programs/) - AWS 인증 및 규정 준수 프로그램
