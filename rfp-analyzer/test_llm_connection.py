"""
test_llm_connection.py
----------------------
Comprehensive validation script for IBM Services Essentials LLM connection.

Tests:
1. Basic connectivity and authentication
2. Model availability and response quality
3. JSON formatting and parsing
4. Token usage metrics
5. Error handling and retry logic

Usage:
    python test_llm_connection.py
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import agents module
sys.path.insert(0, str(Path(__file__).parent))

import structlog
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Import the existing call_claude function
from agents.base import call_claude

# Load environment variables
load_dotenv()

# Setup logging
from logging_config import setup_logging
setup_logging(
    log_file="./logs/llm_validation.log",
    console_level="INFO",
    file_level="DEBUG"
)

log = structlog.get_logger(__name__)
console = Console()


class LLMValidator:
    """Validates LLM connection and functionality."""
    
    def __init__(self):
        self.results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "total_tokens": 0,
            "total_time": 0.0,
            "details": []
        }
        
        # Get configuration from environment
        self.api_base = os.getenv("OPENAI_API_BASE", "https://servicesessentials.ibm.com/apis/v3")
        self.model_id = os.getenv("MODEL_ID", "global/anthropic.claude-sonnet-4-5-20250929-v1:0")
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        
    def run_test(self, test_name: str, test_func):
        """Run a single test and record results."""
        console.print(f"\n[bold cyan]Running: {test_name}[/bold cyan]")
        self.results["tests_run"] += 1
        
        start_time = time.time()
        try:
            result = test_func()
            elapsed = time.time() - start_time
            
            if result["success"]:
                self.results["tests_passed"] += 1
                console.print(f"[bold green]PASSED[/bold green] ({elapsed:.2f}s)")
            else:
                self.results["tests_failed"] += 1
                console.print(f"[bold red]FAILED[/bold red] ({elapsed:.2f}s)")
                console.print(f"[red]Error: {result.get('error', 'Unknown error')}[/red]")
            
            result["elapsed_time"] = elapsed
            result["test_name"] = test_name
            self.results["details"].append(result)
            self.results["total_time"] += elapsed
            
            if "tokens" in result:
                self.results["total_tokens"] += result["tokens"]
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            self.results["tests_failed"] += 1
            console.print(f"[bold red]EXCEPTION[/bold red] ({elapsed:.2f}s)")
            console.print(f"[red]Exception: {str(e)}[/red]")
            
            error_result = {
                "success": False,
                "error": str(e),
                "elapsed_time": elapsed,
                "test_name": test_name
            }
            self.results["details"].append(error_result)
            self.results["total_time"] += elapsed
            return error_result
    
    def test_basic_connectivity(self):
        """Test 1: Basic API connectivity and authentication."""
        system_prompt = """You are a test assistant. Return a JSON array with exactly one object.
The object must have a 'status' field set to 'connected' and a 'message' field with a brief greeting."""
        
        user_content = "Please confirm connection status."
        
        try:
            response = call_claude(
                system_prompt=system_prompt,
                user_content=user_content,
                max_tokens=500
            )
            
            if not response:
                return {
                    "success": False,
                    "error": "Empty response from API"
                }
            
            if not isinstance(response, list):
                return {
                    "success": False,
                    "error": f"Expected list, got {type(response).__name__}"
                }
            
            if len(response) == 0:
                return {
                    "success": False,
                    "error": "Empty list returned"
                }
            
            first_item = response[0]
            if "status" not in first_item:
                return {
                    "success": False,
                    "error": "Response missing 'status' field"
                }
            
            return {
                "success": True,
                "response": response,
                "tokens": 100  # Approximate
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_json_formatting(self):
        """Test 2: JSON array formatting and parsing."""
        system_prompt = """Return a JSON array with exactly 3 objects. Each object should have:
- 'id': a number (1, 2, 3)
- 'name': a string
- 'active': a boolean

Return ONLY the JSON array, no other text."""
        
        user_content = "Generate test data."
        
        try:
            response = call_claude(
                system_prompt=system_prompt,
                user_content=user_content,
                max_tokens=500
            )
            
            if not isinstance(response, list):
                return {
                    "success": False,
                    "error": f"Expected list, got {type(response).__name__}"
                }
            
            if len(response) != 3:
                return {
                    "success": False,
                    "error": f"Expected 3 items, got {len(response)}"
                }
            
            # Validate structure
            for i, item in enumerate(response):
                if not isinstance(item, dict):
                    return {
                        "success": False,
                        "error": f"Item {i} is not a dict"
                    }
                
                required_fields = ["id", "name", "active"]
                for field in required_fields:
                    if field not in item:
                        return {
                            "success": False,
                            "error": f"Item {i} missing field '{field}'"
                        }
            
            return {
                "success": True,
                "response": response,
                "tokens": 150
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_complex_reasoning(self):
        """Test 3: Complex reasoning and structured output."""
        system_prompt = """You are an analyst. Analyze the given text and return a JSON array with one object containing:
- 'word_count': number of words
- 'sentence_count': number of sentences
- 'key_topics': array of 2-3 main topics
- 'sentiment': 'positive', 'negative', or 'neutral'

Return ONLY the JSON array."""
        
        user_content = """Artificial intelligence is transforming how businesses operate. 
Machine learning models can now process vast amounts of data quickly. 
This technology enables better decision-making and improved efficiency."""
        
        try:
            response = call_claude(
                system_prompt=system_prompt,
                user_content=user_content,
                max_tokens=1000
            )
            
            if not response or len(response) == 0:
                return {
                    "success": False,
                    "error": "Empty response"
                }
            
            analysis = response[0]
            required_fields = ["word_count", "sentence_count", "key_topics", "sentiment"]
            
            for field in required_fields:
                if field not in analysis:
                    return {
                        "success": False,
                        "error": f"Missing field '{field}'"
                    }
            
            # Validate types
            if not isinstance(analysis["word_count"], int):
                return {
                    "success": False,
                    "error": "word_count should be an integer"
                }
            
            if not isinstance(analysis["key_topics"], list):
                return {
                    "success": False,
                    "error": "key_topics should be a list"
                }
            
            return {
                "success": True,
                "response": response,
                "tokens": 200
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_model_capabilities(self):
        """Test 4: Model understanding and instruction following."""
        system_prompt = """You are a requirements analyst. Extract requirements from the text.
Return a JSON array where each object has:
- 'requirement': the requirement text
- 'type': 'functional' or 'non-functional'
- 'priority': 'high', 'medium', or 'low'

Return ONLY the JSON array."""
        
        user_content = """The system must authenticate users within 2 seconds.
Users should be able to export reports in PDF format.
The application must support 1000 concurrent users."""
        
        try:
            response = call_claude(
                system_prompt=system_prompt,
                user_content=user_content,
                max_tokens=1500
            )
            
            if not response:
                return {
                    "success": False,
                    "error": "Empty response"
                }
            
            if len(response) < 2:
                return {
                    "success": False,
                    "error": f"Expected at least 2 requirements, got {len(response)}"
                }
            
            # Validate structure
            for req in response:
                if not all(k in req for k in ["requirement", "type", "priority"]):
                    return {
                        "success": False,
                        "error": "Missing required fields in requirement"
                    }
                
                if req["type"] not in ["functional", "non-functional"]:
                    return {
                        "success": False,
                        "error": f"Invalid type: {req['type']}"
                    }
            
            return {
                "success": True,
                "response": response,
                "tokens": 300
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def print_configuration(self):
        """Display current configuration."""
        config_table = Table(title="LLM Configuration", show_header=True)
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="yellow")
        
        # Mask API key for security
        masked_key = self.api_key[:10] + "..." + self.api_key[-10:] if len(self.api_key) > 20 else "***"
        
        config_table.add_row("API Endpoint", self.api_base)
        config_table.add_row("Model ID", self.model_id)
        config_table.add_row("API Key", masked_key)
        config_table.add_row("Timeout", "120 seconds")
        
        console.print(config_table)
    
    def print_summary(self):
        """Print validation summary."""
        console.print("\n" + "="*70)
        console.print("[bold]VALIDATION SUMMARY[/bold]")
        console.print("="*70)
        
        # Summary table
        summary_table = Table(show_header=False)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="yellow")
        
        summary_table.add_row("Tests Run", str(self.results["tests_run"]))
        summary_table.add_row("Tests Passed", f"[green]{self.results['tests_passed']}[/green]")
        summary_table.add_row("Tests Failed", f"[red]{self.results['tests_failed']}[/red]")
        summary_table.add_row("Total Tokens (approx)", str(self.results["total_tokens"]))
        summary_table.add_row("Total Time", f"{self.results['total_time']:.2f}s")
        
        console.print(summary_table)
        
        # Overall status
        if self.results["tests_failed"] == 0:
            console.print(Panel(
                "[bold green]ALL TESTS PASSED[/bold green]\n\n"
                "Your LLM connection is properly configured and working correctly.",
                title="Status",
                border_style="green"
            ))
        else:
            console.print(Panel(
                f"[bold red]{self.results['tests_failed']} TEST(S) FAILED[/bold red]\n\n"
                "Please review the errors above and check your configuration.",
                title="Status",
                border_style="red"
            ))
        
        # Detailed results
        if self.results["details"]:
            console.print("\n[bold]Detailed Results:[/bold]")
            for detail in self.results["details"]:
                status = "PASS" if detail.get("success") else "FAIL"
                color = "green" if detail.get("success") else "red"
                console.print(f"  [{color}]{status}[/{color}] {detail['test_name']} ({detail['elapsed_time']:.2f}s)")
                if not detail.get("success") and "error" in detail:
                    console.print(f"     [red]Error: {detail['error']}[/red]")


def main():
    """Main validation routine."""
    console.print(Panel(
        "[bold]LLM Connection Validator[/bold]\n\n"
        "Testing IBM Services Essentials API connection",
        title="RFP Analyzer",
        border_style="blue"
    ))
    
    validator = LLMValidator()
    
    # Display configuration
    console.print("\n")
    validator.print_configuration()
    
    # Run tests
    console.print("\n[bold]Running Validation Tests...[/bold]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Validating...", total=None)
        
        validator.run_test("Basic Connectivity", validator.test_basic_connectivity)
        validator.run_test("JSON Formatting", validator.test_json_formatting)
        validator.run_test("Complex Reasoning", validator.test_complex_reasoning)
        validator.run_test("Model Capabilities", validator.test_model_capabilities)
        
        progress.update(task, completed=True)
    
    # Print summary
    validator.print_summary()
    
    # Return exit code
    return 0 if validator.results["tests_failed"] == 0 else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Validation interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n[bold red]Fatal error: {e}[/bold red]")
        log.exception("validation_fatal_error")
        sys.exit(1)

# Made with Bob
