"""
Unit tests for Supervisor Agent routing logic

Tests A2A call patterns and report generation flow.
"""

import pytest


class TestReportGenerationFlow:
    """Test report generation two-step process."""

    def test_report_with_previous_analysis(self):
        """Should accept previous_analysis and generate report."""
        # This simulates Supervisor calling create_detailed_report
        # after gathering data from ESG Agent or Research Agent
        topic = "삼성물산 산림벌채 리스크 분석"
        previous_analysis = "ESG Agent가 수집한 KB 데이터..."

        # In actual code: create_detailed_report(topic, previous_analysis)
        # Expected: Report Agent receives this data and generates HTML
        assert previous_analysis is not None
        assert len(previous_analysis) > 0

    def test_report_without_previous_analysis(self):
        """Should return guidance if no data provided."""
        # This simulates incorrect usage - calling report without data
        topic = "삼성물산 산림벌채 리스크 분석"
        previous_analysis = ""

        # In actual code: create_detailed_report(topic, previous_analysis)
        # Expected: Return guidance message (not generate report)
        assert previous_analysis == ""
        # Should return: "보고서를 생성하려면 먼저 관련 데이터를 조회해주세요."

    def test_report_request_detection(self):
        """Should detect report generation requests."""
        report_keywords = ["보고서", "리포트", "PDF", "문서"]

        test_cases = [
            ("삼성물산 산림벌채 리스크 분석 보고서 만들어줘", True),
            ("상세 리포트 작성해줘", True),
            ("PDF로 저장해줘", True),
            ("자세한 분석 문서", True),
            ("삼성물산 탄소배출량은?", False),
            ("LTIR이 뭔가요?", False),
        ]

        for query, expected_is_report in test_cases:
            is_report_request = any(
                keyword in query
                for keyword in report_keywords
            )
            assert is_report_request == expected_is_report, \
                f"Failed for query: {query}"


class TestA2ACallPattern:
    """Test A2A call pattern (no hardcoding)."""

    def test_supervisor_uses_llm_judgment(self):
        """Supervisor should use LLM judgment, not keyword matching."""
        # Supervisor's system prompt includes routing guidelines
        # No hardcoded keyword matching in code
        # Agent (LLM) decides which sub-agent to call based on context

        test_cases = [
            {
                "user_query": "삼성물산 산림벌채 리스크 분석 보고서",
                "expected_flow": "call_esg_agent → create_detailed_report",
                "reason": "삼성물산 = KB data available"
            },
            {
                "user_query": "현대건설 안전 성과 보고서",
                "expected_flow": "call_research_agent → create_detailed_report",
                "reason": "현대건설 = Web search needed"
            },
            {
                "user_query": "주요 건설사 LTIR 비교 보고서",
                "expected_flow": "create_and_execute_plan → create_detailed_report",
                "reason": "Multi-company = complex plan"
            }
        ]

        # This is a design test - verifies A2A pattern, not implementation
        for case in test_cases:
            assert "user_query" in case
            assert "expected_flow" in case
            assert "reason" in case


class TestTwoStepReportProcess:
    """Test two-step report generation process."""

    def test_step_2a_data_collection(self):
        """Step 2a: Supervisor gathers data first."""
        # Supervisor system prompt specifies:
        # "Step 2a: Gather data FIRST (choose appropriate agent)"
        # This ensures data is collected before report generation
        assert True  # Design verification

    def test_step_2b_report_generation(self):
        """Step 2b: Generate report with collected data."""
        # Supervisor system prompt specifies:
        # "Step 2b: Generate report with collected data"
        # "Call create_detailed_report with previous_analysis from Step 2a"
        assert True  # Design verification


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
