"""
Demo script to test the AI Customer Support Bot with sample queries.
This script demonstrates the bot's capabilities with various test scenarios.

Usage:
    python demo.py [--scenario <name>] [--interactive]

Examples:
    python demo.py                          # Run all test scenarios
    python demo.py --scenario "Happy Path"  # Run specific scenario
    python demo.py --interactive            # Interactive testing mode
"""

import argparse
import json
import time
from pathlib import Path
from typing import Any

import requests

API_BASE = "http://127.0.0.1:8000"
DEMO_QUERIES_PATH = Path(__file__).parent / "data" / "demo_queries.json"


def load_demo_queries() -> dict[str, Any]:
    """Load demo queries from JSON file."""
    with open(DEMO_QUERIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def send_chat_message(message: str, session_id: str = "demo") -> dict[str, Any]:
    """Send a chat message to the API."""
    try:
        response = requests.post(
            f"{API_BASE}/api/chat",
            json={"message": message, "session_id": session_id},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return {}


def print_response(response: dict[str, Any], show_details: bool = True) -> None:
    """Pretty print a chat response."""
    if not response:
        return

    print(f"\n🤖 Bot: {response.get('response', 'No response')}")
    
    if show_details:
        print(f"   Intent: {response.get('intent', 'unknown')}")
        print(f"   Confidence: {response.get('confidence', 0):.2f}")
        
        if response.get('created_ticket'):
            print(f"   🎫 Ticket #{response.get('ticket_id')} created")
        
        if response.get('context_summary'):
            print(f"   📄 Context: {response.get('context_summary')[:60]}...")


def run_test_scenario(scenario: dict[str, Any]) -> None:
    """Run a single test scenario."""
    print(f"\n{'='*70}")
    print(f"📋 Scenario: {scenario['name']}")
    print(f"{'='*70}")
    
    session_id = scenario['session_id']
    
    for i, message in enumerate(scenario['messages'], 1):
        print(f"\n👤 User (Turn {i}): {message}")
        response = send_chat_message(message, session_id)
        print_response(response)
        time.sleep(0.5)  # Brief pause between messages
    
    print(f"\n✅ Expected: {scenario['expected_outcome']}")


def run_category_test(category_name: str, queries: list[str]) -> None:
    """Run tests for a specific category of queries."""
    print(f"\n{'='*70}")
    print(f"📂 Testing Category: {category_name}")
    print(f"{'='*70}")
    
    session_id = f"category-{category_name.lower().replace(' ', '-')}"
    
    for i, query in enumerate(queries[:5], 1):  # Limit to 5 per category
        print(f"\n👤 User ({i}): {query}")
        response = send_chat_message(query, session_id)
        print_response(response, show_details=False)
        time.sleep(0.3)


def interactive_mode() -> None:
    """Interactive chat mode for manual testing."""
    print("\n" + "="*70)
    print("🎮 Interactive Mode - Type 'quit' to exit")
    print("="*70)
    
    session_id = f"interactive-{int(time.time())}"
    
    while True:
        try:
            message = input("\n👤 You: ").strip()
            if message.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if not message:
                continue
            
            response = send_chat_message(message, session_id)
            print_response(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break


def check_api_health() -> bool:
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE}/api/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Demo the AI Customer Support Bot")
    parser.add_argument(
        "--scenario",
        type=str,
        help="Run specific test scenario by name",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Start interactive chat mode",
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Test specific query category (faq_matching, escalation, etc.)",
    )
    
    args = parser.parse_args()
    
    # Check API health
    print("🔍 Checking API status...")
    if not check_api_health():
        print("❌ Error: API is not running!")
        print("   Start the server with: uvicorn app.main:app --reload")
        return
    
    print("✅ API is running\n")
    
    # Load demo data
    demo_data = load_demo_queries()
    
    # Interactive mode
    if args.interactive:
        interactive_mode()
        return
    
    # Category test
    if args.category:
        categories = demo_data['categories']
        if args.category in categories:
            cat_data = categories[args.category]
            queries = cat_data.get('queries', [])
            run_category_test(args.category, queries)
        else:
            print(f"❌ Category '{args.category}' not found")
            print(f"   Available: {', '.join(categories.keys())}")
        return
    
    # Specific scenario
    if args.scenario:
        scenarios = demo_data['test_scenarios']
        matching = [s for s in scenarios if args.scenario.lower() in s['name'].lower()]
        
        if matching:
            for scenario in matching:
                run_test_scenario(scenario)
        else:
            print(f"❌ No scenarios found matching '{args.scenario}'")
            print(f"\nAvailable scenarios:")
            for s in scenarios:
                print(f"  - {s['name']}")
        return
    
    # Run all scenarios
    print("\n🚀 Running all test scenarios...\n")
    for scenario in demo_data['test_scenarios']:
        run_test_scenario(scenario)
        time.sleep(1)
    
    print("\n" + "="*70)
    print("✅ All scenarios completed!")
    print("="*70)
    print("\nTry interactive mode: python demo.py --interactive")


if __name__ == "__main__":
    main()
