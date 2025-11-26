#!/usr/bin/env python3
"""
CLI interface for Agentic AI chatbot using Strands Agents.

Provides an interactive command-line interface for asking questions
about sustainability practices and external information.
"""

import sys
import logging
import subprocess
from pathlib import Path
from typing import List, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import print as rprint

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import supervisor_agent


class AgenticAIChatbotCLI:
    """
    Command-line interface for multi-agent Agentic AI chatbot.

    Uses Supervisor Agent to route questions to specialized agents:
    - Knowledge Agent: Internal knowledge base
    - Search Agent: External information
    """
    
    def __init__(self):
        """Initialize CLI chatbot."""
        self.console = Console()
        self.agent = supervisor_agent
        self.chat_history: List[Tuple[str, str]] = []
        
        # Configure logging
        logging.basicConfig(
            level=logging.WARNING,  # Reduce noise
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def display_welcome(self):
        """Display welcome message."""
        welcome_text = """
# Agentic AI Chatbot (Multi-Agent System)

Welcome to the Agentic AI chatbot powered by Strands Agents.

**What I can help you with:**

1. Internal Knowledge Base Questions
   - Sustainability practices and initiatives
   - Environmental impact and climate action
   - Social responsibility and governance
   - Performance metrics and analysis

2. External Information
   - Company reports and analysis
   - Industry benchmarks and standards
   - News and trends
   - Regulatory updates

**Multi-Agent Architecture:**
- Supervisor Agent: Routes your questions intelligently
- Knowledge Agent: Specialist for internal knowledge base
- Search Agent: Specialist for external information

**Commands:**
- Type your question to get started
- `quit` or `exit` - End session
- `history` - View conversation history
- `clear` - Clear history
- `help` - Show commands
"""
        self.console.print(Panel(Markdown(welcome_text), border_style="cyan"))
    
    def display_help(self):
        """Display help information."""
        help_text = """
**Available Commands:**

- `quit` or `exit` - End the chat session
- `history` - Display conversation history
- `clear` - Clear conversation history
- `help` - Show this help message
- Any other text - Ask your questions

**Example Questions:**

1. Internal Knowledge: "탄소배출량은?"
2. External Information: "현대자동차 지속가능성 보고서"
3. General Topics: "지속가능성 평가 기관"
"""
        self.console.print(Panel(Markdown(help_text), title="Help", border_style="blue"))
    
    def display_history(self):
        """Display conversation history."""
        if not self.chat_history:
            self.console.print("[yellow]No conversation history yet.[/yellow]")
            return
        
        self.console.print("\n[bold cyan]Conversation History:[/bold cyan]\n")
        for idx, (question, answer) in enumerate(self.chat_history, 1):
            self.console.print(f"[bold]Q{idx}:[/bold] {question}")
            self.console.print(f"[bold]A{idx}:[/bold] {answer[:200]}...")
            self.console.print()
    
    def clear_history(self):
        """Clear conversation history."""
        self.chat_history = []
        self.console.print("[green]Conversation history cleared.[/green]")
    
    def process_question(self, question: str, max_clarifications: int = 3) -> str:
        """
        Process user question with supervisor agent.
        Handles clarification loop for unclear questions.

        Args:
            question: User's question
            max_clarifications: Maximum clarification rounds (default: 3)

        Returns:
            Agent's response as string
        """
        clarification_count = 0
        current_question = question

        while clarification_count < max_clarifications:
            try:
                self.console.print("\n[yellow]Processing your question...[/yellow]")

                # Build context from recent conversation history
                context = ""
                if self.chat_history:
                    # Include last 2 exchanges for context
                    recent_history = self.chat_history[-2:]
                    for q, a in recent_history:
                        context += f"Previous Q: {q}\nPrevious A: {a}\n\n"

                    full_question = f"{context}Current question: {current_question}"
                else:
                    full_question = current_question

                # Call supervisor agent with context
                response = self.agent(full_question)
                response_text = str(response)

                # Check if clarification is needed
                if response_text.startswith("CLARIFICATION_NEEDED:"):
                    clarification_count += 1

                    self.console.print(
                        f"\n[yellow]Need clarification ({clarification_count}/{max_clarifications}):[/yellow]"
                    )

                    # Parse clarification questions
                    questions = self._parse_clarification_questions(response_text)

                    # Ask user for clarifications
                    answers = []
                    for idx, q in enumerate(questions, 1):
                        self.console.print(f"\n[cyan]{idx}. {q}[/cyan]")
                        answer = Prompt.ask("[bold green]Your answer[/bold green]")
                        answers.append(answer)

                    # Enhance original question with clarifications
                    current_question = self._enhance_question_with_clarifications(
                        question, questions, answers
                    )

                    self.console.print("\n[green]Thank you! Processing with clarifications...[/green]")
                    continue  # Loop again with enhanced question

                # No clarification needed - return answer
                self.chat_history.append((question, response_text))
                return response_text

            except Exception as e:
                self.logger.error(f"Error processing question: {str(e)}")
                return f"Error: {str(e)}"

        # Max clarifications reached
        return "I'm sorry, but I'm still unable to fully understand your question after multiple clarifications. Could you please rephrase it more specifically?"

    def _parse_clarification_questions(self, response: str) -> List[str]:
        """
        Parse clarification questions from response.

        Args:
            response: Response containing CLARIFICATION_NEEDED marker

        Returns:
            List of clarification questions
        """
        lines = response.split('\n')
        questions = []

        for line in lines[1:]:  # Skip first line (CLARIFICATION_NEEDED:)
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering/bullet
                question = line.lstrip('0123456789.- ')
                if question:
                    questions.append(question)

        return questions

    def _enhance_question_with_clarifications(
        self,
        original_question: str,
        questions: List[str],
        answers: List[str]
    ) -> str:
        """
        Enhance original question with clarification answers.

        Args:
            original_question: Original user question
            questions: Clarification questions asked
            answers: User's answers

        Returns:
            Enhanced question with context
        """
        enhanced = f"Original question: {original_question}\n\n"
        enhanced += "Additional context:\n"

        for q, a in zip(questions, answers):
            enhanced += f"- {q}: {a}\n"

        return enhanced

    def _handle_report_generation(self, response: str) -> str:
        """
        Handle HTML report generation and convert to PDF.

        Args:
            response: Response containing HTML_REPORT_GENERATED marker

        Returns:
            Updated response with PDF status
        """
        try:
            # Extract HTML file path
            if "HTML_REPORT_GENERATED:" not in response:
                return response

            lines = response.split('\n')
            html_path = None

            for line in lines:
                if line.startswith("HTML_REPORT_GENERATED:"):
                    html_path = line.split(":", 1)[1].strip()
                    break

            if not html_path:
                return response

            self.console.print("[yellow]Converting HTML to PDF (scale 80%)...[/yellow]")

            # Convert to PDF using Node.js
            pdf_path = html_path.replace('.html', '.pdf')

            mcp_dir = Path(__file__).parent.parent / "mcp" / "html2pdf"
            abs_html_path = Path(html_path).resolve()
            abs_pdf_path = Path(pdf_path).resolve()

            # Create Node.js conversion script
            script = f"""
const {{ PdfConverter }} = require('./dist/pdf-converter.js');

async function convert() {{
    const converter = new PdfConverter();
    const result = await converter.convertToPdf({{
        htmlPath: '{abs_html_path}',
        outputPath: '{abs_pdf_path}',
        scale: 0.8,
        printBackground: true,
        format: 'A4',
        marginTop: '15mm',
        marginBottom: '15mm',
        marginLeft: '15mm',
        marginRight: '15mm'
    }});

    await converter.cleanup();

    if (result.success) {{
        console.log('SUCCESS');
    }} else {{
        console.error('FAILED:', result.error);
        process.exit(1);
    }}
}}

convert().catch(err => {{
    console.error('ERROR:', err.message);
    process.exit(1);
}});
"""

            script_path = mcp_dir / 'temp_convert.cjs'  # Use .cjs for CommonJS
            with open(script_path, 'w') as f:
                f.write(script)

            # Execute conversion
            result = subprocess.run(
                ['node', str(script_path)],
                cwd=mcp_dir,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Clean up
            script_path.unlink(missing_ok=True)

            # Update response based on result
            if result.returncode == 0 and 'SUCCESS' in result.stdout:
                self.console.print("[green]PDF conversion completed![/green]")

                updated_response = response.replace(
                    "PDF 변환 중입니다...",
                    f"""PDF 변환 완료!

보고서 파일:
- HTML: {html_path}
- PDF: {pdf_path} (scale 80%)

파일을 확인하시면 상세한 분석 내용을 보실 수 있습니다."""
                )
                return updated_response
            else:
                self.console.print("[yellow]PDF conversion failed, HTML available[/yellow]")
                updated_response = response.replace(
                    "PDF 변환 중입니다...",
                    f"(PDF 변환 실패 - HTML 파일을 사용해주세요: {html_path})"
                )
                return updated_response

        except Exception as e:
            self.logger.error(f"Report PDF conversion error: {str(e)}")
            return response.replace("PDF 변환 중입니다...", f"(PDF 변환 오류: {str(e)})")

    def run(self):
        """Run interactive CLI loop."""
        self.display_welcome()
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]You[/bold green]")
                
                # Check for commands
                if user_input.lower() in ['quit', 'exit']:
                    self.console.print("\n[cyan]Thank you for using the Agentic AI chatbot! Goodbye![/cyan]")
                    break
                
                elif user_input.lower() == 'help':
                    self.display_help()
                    continue
                
                elif user_input.lower() == 'history':
                    self.display_history()
                    continue
                
                elif user_input.lower() == 'clear':
                    self.clear_history()
                    continue
                
                elif not user_input.strip():
                    continue
                
                # Process question
                response = self.process_question(user_input)

                # Display response
                self.console.print("\n[bold magenta]Agentic AI Chatbot:[/bold magenta]")
                self.console.print(Panel(Markdown(response), border_style="magenta"))
                
            except KeyboardInterrupt:
                self.console.print("\n\n[cyan]Session interrupted. Goodbye![/cyan]")
                break
            
            except Exception as e:
                self.console.print(f"\n[red]Error: {str(e)}[/red]")
                self.logger.error(f"CLI error: {str(e)}", exc_info=True)


def main():
    """Main entry point."""
    cli = AgenticAIChatbotCLI()
    cli.run()


if __name__ == "__main__":
    main()
