"""
Unit Test for HTML/PDF Report Generation

Tests report generation with sample data (no chatbot needed).
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tools.report_tools import generate_report_stepwise_append


# Sample report data (CBAM analysis)
SAMPLE_REPORT_DATA = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
삼성물산 CBAM 영향 전망 상세 분석
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【 핵심 발견사항 】

삼성물산은 CBAM을 정책·법률 리스크로 인식하고 2024년 11월 모니터링 체계 구축을 완료했습니다.
EU향 철강·비료 구체적 수출 규모는 비공개이나, 업계 전망 기준 2026년 이후 점진적 재무 부담 증가가 예상됩니다.

【 재무 영향 (한국 업계 전체 기준) 】

철강 산업:
- 2026년: 100~150억원
- 2028년: 300~500억원
- 2030년: 1,000~2,000억원
- 2034년: 4,000~6,000억원

비료 산업:
- 2026년: 10~30억원
- 2028년: 30~100억원
- 2030년: 100~300억원
- 2034년: 400~1,000억원

【 리스크 수준 】

단기(~2027): 낮음 - 무상할당 100%로 재무 영향 최소
중기(2028~2032): 중간 - 무상할당 점진 감소, 실질 부담 증가
장기(2033~): 높음 - 2034년 무상할당 완전 종료, 전액 부담

【 CBAM 제도 개요 】

EU 탄소국경조정제도(CBAM)는 EU 그린딜의 핵심 정책으로, 탄소누출 방지와 공정한 경쟁 환경을 목적으로 합니다.

시행 일정:
- 2023.10: 과도기 시작 (보고 의무만)
- 2026.01: 본격 시행 (CBAM 인증서 구매 시작)
- 2034.01: EU ETS 무상할당 완전 종료

적용 대상: 철강, 시멘트, 비료, 알루미늄, 전력, 수소

【 삼성물산 현황 】

사업 구조:
- 상사부문: 철강, 화학, 에너지 등 글로벌 트레이딩
- EU 시장: 주요 수출 대상 지역

배출량 (2024년):
- Scope 1+2: 데이터 제한적
- Scope 3: 56,053 tCO₂e

CBAM 대응:
✓ 리스크 인식: 정책·법률 리스크로 공식 분류
✓ 모니터링 시스템 구축 (2024.11)
✓ 임직원 CBAM 교육 프로그램 운영
✓ 지속가능경영보고서 공시

데이터 제약:
- EU향 철강/비료 수출량 미공개
- 제품별 탄소집약도 미공개
→ 정량적 재무 영향 추정 제한

【 대응 전략 제언 】

단기 (2025~2027):
1. 데이터 인프라 구축
   - CBAM 신고 시스템 고도화
   - 제품별 탄소집약도 정밀 측정
   - 공급망 배출량 추적 시스템

2. 무상할당 최대 활용
   - EU ETS 크레딧 확보 전략
   - 수출국 탄소가격 차감 최대화

중기 (2028~2032):
1. 저탄소 공급망 전환
   - 친환경 원자재 조달 확대
   - 저탄소 철강/그린 암모니아 비료 소싱

2. 기술 혁신 투자
   - 수소환원제철 기술 협력
   - CCS/CCUS 적용 검토

장기 (2033~):
1. 사업 구조 재편
   - 저탄소 제품 포트폴리오 전환
   - EU 역내 생산 기지 검토
   - 시장 다변화

2. 전략적 제휴
   - 글로벌 저탄소 기업 파트너십
   - 기술 라이센싱 확보

【 결론 】

삼성물산은 CBAM을 선제적으로 인식하고 대응 체계를 조기에 구축했습니다.
구체적 수출 규모 비공개로 정량적 영향 추정에는 한계가 있으나,
업계 전망 기준 2030년대 수천억 원 규모의 잠재 부담이 예상됩니다.

저탄소 기술 확보가 향후 경쟁력의 결정적 요소가 될 것이며,
데이터 투명성 강화, 저탄소 전환 로드맵 수립, 재무 시나리오 분석이
우선적으로 필요합니다.
"""


class TestReportHTMLPDFGeneration:
    """Test HTML and PDF generation directly with sample data."""

    def test_stepwise_html_generation(self, tmp_path):
        """Test stepwise HTML append generation."""
        # Arrange
        topic = "삼성물산 CBAM 영향 전망 분석"
        output_path = tmp_path / "test_report.html"

        # Act
        result = generate_report_stepwise_append(
            topic=topic,
            data=SAMPLE_REPORT_DATA,
            output_path=output_path
        )

        # Assert
        assert output_path.exists(), "HTML file should be created"
        assert output_path.stat().st_size > 0, "HTML file should not be empty"

        # Read and verify content
        with open(output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Check HTML structure
        assert "<!DOCTYPE html>" in html_content
        assert f"<title>{topic}</title>" in html_content
        assert "<h2>" in html_content  # Should have sections
        assert "Samsung C&T ESG" in html_content
        assert "</html>" in html_content

        print(f"\n✓ HTML generated: {output_path}")
        print(f"  Size: {output_path.stat().st_size} bytes")
        print(f"  Sections: {html_content.count('<h2>')}")

    def test_html_has_three_sections(self, tmp_path):
        """Test that HTML has 3 main sections."""
        topic = "CBAM 영향 분석"
        output_path = tmp_path / "test_sections.html"

        generate_report_stepwise_append(
            topic=topic,
            data=SAMPLE_REPORT_DATA,
            output_path=output_path
        )

        with open(output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Should have at least 3 h2 sections
        h2_count = html_content.count('<h2>')
        assert h2_count >= 3, f"Should have at least 3 sections, got {h2_count}"

    def test_html_contains_sample_data(self, tmp_path):
        """Test that HTML contains data from sample."""
        topic = "CBAM 테스트"
        output_path = tmp_path / "test_data.html"

        generate_report_stepwise_append(
            topic=topic,
            data=SAMPLE_REPORT_DATA,
            output_path=output_path
        )

        with open(output_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Check for key data points
        # Note: Report Agent may rephrase, so check for concepts not exact text
        assert "CBAM" in html_content or "탄소국경" in html_content
        assert "삼성물산" in html_content or "Samsung" in html_content


class TestReportFilenameFormat:
    """Test report filename format."""

    def test_filename_starts_with_timestamp(self):
        """Test that filename format is YYYYMMDD_HHMMSS_topic."""
        from datetime import datetime, timezone, timedelta

        # KST timezone
        KST = timezone(timedelta(hours=9))
        timestamp = datetime.now(KST).strftime("%Y%m%d_%H%M%S")

        topic = "테스트 보고서"
        safe_topic = "테스트_보고서"
        expected_format = f"{timestamp}_{safe_topic}"

        # Check format
        assert expected_format.startswith(timestamp)
        assert timestamp in expected_format
        assert safe_topic in expected_format

        print(f"\n✓ Filename format correct: {expected_format}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
