from ..models.ollama_model import LocalLLM
import json

def get_sales_agent():
    llm = LocalLLM(model_name="llama3.2:3b").get_llm()
    return llm

def collect_customer_info(user_message: str, session_data=None):
    llm = get_sales_agent()
    
    collected_fields = session_data or {}
    
    # Define required fields in order
    required_fields = {
        "name": "Full Name",
        "age": "Age",
        "employment_type": "Employment Type (Salaried/Self-employed)",
        "salary": "Monthly Salary (INR)",
        "credit_score": "Credit Score",
        "loan_amount": "Loan Amount Required (INR)"
    }
    
    # Check what's missing
    missing_fields = {key: value for key, value in required_fields.items() if key not in collected_fields}
    
    system_prompt = """You are a friendly and professional Loan Sales Agent. Your goal is to collect loan application information politely and efficiently.

CRITICAL RULES:
1. Be polite, professional and friendly
2. Only ask for ONE missing piece of information at a time
3. NEVER ask for information that's already collected
4. LOAN AMOUNT and SALARY are TWO DIFFERENT THINGS - ask for them separately
5. When ALL information is complete, return ONLY the JSON data without any additional text
6. Keep your responses concise but warm

FIELD EXPLANATIONS:
- Monthly Salary: How much you earn per month
- Loan Amount: How much money you want to borrow (usually much larger than salary)

make sure to ask about the loan amount required separately from the salary.

Current conversation:"""
    
    # Build the prompt
    prompt = system_prompt + "\n\n"
    
    # Show collected information
    if collected_fields:
        prompt += "✅ Collected Information:\n"
        for field, display_name in required_fields.items():
            if field in collected_fields:
                prompt += f"- {display_name}: {collected_fields[field]}\n"
    else:
        prompt += "No information collected yet.\n"
    
    # Show missing information
    if missing_fields:
        prompt += f"\n❌ Still needed: {', '.join(missing_fields.values())}\n"
        prompt += f"\nAsk for: {list(missing_fields.values())[0]}\n"
    else:
        prompt += "\n🎉 ALL INFORMATION COLLECTED! Return JSON now.\n"
        prompt += "JSON format: {\"name\": \"...\", \"age\": ..., \"salary\": ..., \"credit_score\": ..., \"loan_amount\": ..., \"employment_type\": \"...\"}\n"
    
    prompt += f"\nCustomer: {user_message}"
    prompt += f"\nAgent:"
    
    print(f"=== PROMPT SENT TO LLM ===\n{prompt}\n========================")  # Debug
    
    response = llm.invoke(prompt)
    return response