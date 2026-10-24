from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

console = Console()


def main():
    console.print("\n[bold cyan]API C2C Recruitment Automation[/bold cyan]")
    console.print(f"Project directory: {BASE_DIR}")
    console.print("[green]Application setup successful![/green]")
    console.print("\nNext: job-post filtering and recruiter data validation.")


if __name__ == "__main__":
    main()
