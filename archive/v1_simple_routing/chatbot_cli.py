#!/usr/bin/env python3
"""
CLI interface for ESG chatbot using Strands Agents.

Provides an interactive command-line interface for asking questions
about Samsung C&T's ESG practices and external ESG information.
"""

import sys
import logging
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


class ESGChatbotCLI:
    """
    Command-line interface for multi-agent ESG chatbot.
    
    Uses Supervisor Agent to route questions to specialized agents:
    - ESG Agent: Samsung C&T knowledge base
    - Search Agent: External ESG information
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
# Samsung C&T ESG Chatbot (Multi-Agent System)

Welcome to the Samsung C&T ESG chatbot powered by Strands Agents.

**What I can help you with:**

1. Samsung C&T ESG Questions
   - Sustainability practices and initiatives
   - Environmental impact and climate action
   - Social responsibility and governance
   - ESG performance metrics

2. External ESG Information
   - Other companies' ESG reports
   - Industry benchmarks and standards
   - ESG news and trends
   - Regulatory updates

**Multi-Agent Architecture:**
- Supervisor Agent: Routes your questions intelligently
- ESG Agent: Specialist for Samsung C&T (124-page report)
- Search Agent: Specialist for external ESG information

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
- Any other text - Ask a question about ESG topics

**Example Questions:**

1. Samsung C&T: "삼성물산의 탄소배출량은?"
2. Other Companies: "현대자동차 ESG 보고서"
3. General ESG: "ESG rating agencies"
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
    
    def process_question(self, question: str) -> str:
        """
        Process user question with supervisor agent.

        Args:
            question: User's question

        Returns:
            Agent's response as string
        """
        try:
            self.console.print("\n[yellow]Processing your question...[/yellow]")

            # Call supervisor agent (Strands Agents - very simple!)
            response = self.agent(question)

            # Convert AgentResult to string
            response_text = str(response)

            # Add to history
            self.chat_history.append((question, response_text))

            return response_text

        except Exception as e:
            self.logger.error(f"Error processing question: {str(e)}")
            return f"Error: {str(e)}"
    
    def run(self):
        """Run interactive CLI loop."""
        self.display_welcome()
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold green]You[/bold green]")
                
                # Check for commands
                if user_input.lower() in ['quit', 'exit']:
                    self.console.print("\n[cyan]Thank you for using the ESG chatbot! Goodbye![/cyan]")
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
                self.console.print("\n[bold magenta]ESG Chatbot:[/bold magenta]")
                self.console.print(Panel(Markdown(response), border_style="magenta"))
                
            except KeyboardInterrupt:
                self.console.print("\n\n[cyan]Session interrupted. Goodbye![/cyan]")
                break
            
            except Exception as e:
                self.console.print(f"\n[red]Error: {str(e)}[/red]")
                self.logger.error(f"CLI error: {str(e)}", exc_info=True)


def main():
    """Main entry point."""
    cli = ESGChatbotCLI()
    cli.run()


if __name__ == "__main__":
    main()
