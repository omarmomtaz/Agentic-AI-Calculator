"""
Requirements:
1. Install Ollama: https://ollama.com/
2. Pull a model: ollama pull llama3.2
3. pip install requests
"""

import requests
import re
import json

class Calculator:
    """Calculator tool that the AI agent can use"""
    
    @staticmethod
    def calculate(expression):
        """Safely evaluate a mathematical expression"""
        try:
            # Remove any non-math characters for safety
            allowed_chars = set('0123456789+-*/()., ')
            sanitized = ''.join(c for c in expression if c in allowed_chars)
            
            # Evaluate the expression
            result = eval(sanitized)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"


class AgenticCalculator:
    """AI Agent with access to calculator tool"""
    
    def __init__(self, model="llama3.2"):
        self.api_url = "http://localhost:11434/api/generate"
        self.model = model
        self.calculator = Calculator()
        self.conversation_history = []
        
        # System prompt that teaches the AI how to use tools
        self.system_prompt = """
        You are a helpful math assistant with access to a calculator tool. When you need to perform calculations, 
        you MUST use the calculator tool by outputting in this exact format:

        TOOL_CALL: calculator(expression)

        For example:
        - To calculate 25 * 4, output: TOOL_CALL: calculator(25 * 4)
        - To calculate (100 + 50) / 2, output: TOOL_CALL: calculator((100 + 50) / 2)

        After receiving the calculator result, provide a complete answer to the user's question.

        Rules:
        1. For any mathematical computation, use the calculator tool
        2. Break down complex problems into steps if needed
        3. Always show your reasoning
        4. Provide a clear final answer"""
    
    def call_llm(self, prompt):
        """Call Ollama local API"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 500,
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data.get('response', '')
            
        except requests.exceptions.ConnectionError:
            print("\n❌ Error: Cannot connect to Ollama")
            print("\n💡 Solutions:")
            print("1. Install Ollama: https://ollama.com/")
            print("2. Start Ollama: ollama serve")
            print("3. Pull a model: ollama pull llama3.2")
            return ""
        except requests.exceptions.RequestException as e:
            print(f"\n⚠️  API Error: {str(e)}")
            return ""
    
    def parse_tool_calls(self, text):
        """Extract calculator tool calls from AI response"""
        pattern = r'TOOL_CALL:\s*calculator\(([^)]+)\)'
        matches = re.findall(pattern, text)
        return matches
    
    def format_conversation(self):
        """Format conversation history for the LLM"""
        formatted = f"{self.system_prompt}\n\n"
        
        for msg in self.conversation_history:
            role = msg['role'].capitalize()
            content = msg['content']
            formatted += f"{role}: {content}\n\n"
        
        formatted += "Assistant: "
        return formatted
    
    def run(self, user_question, max_iterations=5):
        """Run the agentic loop"""
        print(f"\n{'='*60}")
        print(f"USER: {user_question}")
        print(f"{'='*60}\n")
        
        # Initialize conversation
        self.conversation_history = [
            {"role": "user", "content": user_question}
        ]
        
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"[Iteration {iteration}]")
            
            # Get AI response
            prompt = self.format_conversation()
            ai_response = self.call_llm(prompt)
            
            if not ai_response:
                print("ERROR: No response from AI")
                break
            
            print(f"\nAI AGENT: {ai_response}\n")
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response
            })
            
            # Check for tool calls
            tool_calls = self.parse_tool_calls(ai_response)
            
            if tool_calls:
                # Execute each tool call
                for expression in tool_calls:
                    result = self.calculator.calculate(expression)
                    tool_result = f"Calculator result for {expression}: {result}"
                    
                    print(f"🔧 CALCULATOR TOOL: {expression} = {result}\n")
                    
                    # Add tool result to conversation
                    self.conversation_history.append({
                        "role": "user",
                        "content": tool_result
                    })
            else:
                # No tool calls, agent has finished
                print("✓ Agent completed (no more tool calls)")
                break
        
        if iteration >= max_iterations:
            print(f"\n⚠ Reached maximum iterations ({max_iterations})")
        
        print(f"\n{'='*60}\n")


def main():
    """Main function with example questions"""
    
    print("""
        **AGENTIC AI CALCULATOR**
    """)
    
    print("Available models (install with: ollama pull <model>):")
    print("  - llama3.2 (recommended, 2GB)")
    print("  - llama3.2:1b (fastest, 1.3GB)")
    print("  - mistral (7B)")
    print("  - phi3 (3.8B)")
    
    model = input("\nEnter model name (or press Enter for llama3.2): ").strip() or "llama3.2"
    
    agent = AgenticCalculator(model=model)
    
    # Example questions
    example_questions = [
        "If I buy 3 apples at $2.50 each and 2 oranges at $1.75 each, how much do I spend?",
        "A train travels 120 miles in 2 hours. What is its average speed?",
        "Calculate 15% tip on a $84.50 bill",
    ]
    
    print("\nExample questions:")
    for i, q in enumerate(example_questions, 1):
        print(f"{i}. {q}")
    
    print("\nEnter a question number, or type your own question (or 'quit' to exit):")
    
    while True:
        user_input = input("\n> ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        # Check if user selected an example
        if user_input.isdigit() and 1 <= int(user_input) <= len(example_questions):
            question = example_questions[int(user_input) - 1]
        else:
            question = user_input
        
        if not question:
            continue
        
        # Run the agent
        try:
            agent.run(question)
        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()