from ..models.ollama_model import LocalLLM
import json
import re

def get_underwriter_agent():
    llm = LocalLLM(model_name="llama3.2:3b").get_llm()

    system_prompt = """You are a Loan Underwriter AI. Analyze customer loan applications and return ONLY JSON.

CRITERIA:
- Minimum age: 21
- Maximum age at loan maturity: 60 (assume 5-year loan term)
- Minimum monthly salary: ₹20,000
- Minimum credit score: 650
- Loan amount should not exceed 24x monthly salary
- Must be employed (Salaried or Self-employed)

RETURN ONLY THIS JSON FORMAT:
{
  "eligible": true/false,
  "reason": "Clear explanation based on criteria",
  "risk_score": "Low/Medium/High",
  "next_step": "proceed_to_documents" or "rejected"
}

Examples:
GOOD: {"eligible": true, "reason": "Meets all criteria: age 28, salary ₹75,000, credit score 780, loan amount reasonable", "risk_score": "Low", "next_step": "proceed_to_documents"}
GOOD: {"eligible": false, "reason": "Credit score 600 below minimum 650", "risk_score": "High", "next_step": "rejected"}

Do not add any other text. Return only JSON."""

    return llm, system_prompt

def underwrite(customer_data: dict):
    llm, system_prompt = get_underwriter_agent()

    # Format customer data for better readability
    formatted_data = json.dumps(customer_data, indent=2)
    
    prompt = f"""{system_prompt}

CUSTOMER APPLICATION DATA:
{formatted_data}

UNDERWRITER DECISION:"""

    print("=== UNDERWRITER PROMPT ===")
    print(prompt)
    print("==========================")
    
    response = llm.invoke(prompt)
    
    print(f"=== UNDERWRITER RAW RESPONSE ===")
    print(response)
    print("===============================")
    
    # Robust JSON extraction
    try:
        # Method 1: Try direct JSON parse
        result = json.loads(response.strip())
    except json.JSONDecodeError:
        try:
            # Method 2: Extract JSON from text
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Method 3: Fallback - analyze data manually
                result = manual_underwriting(customer_data)
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            # Method 4: Ultimate fallback
            result = {
                "eligible": False,
                "reason": "System error in underwriting process",
                "risk_score": "High",
                "next_step": "rejected"
            }
    
    # Validate the result structure
    return validate_underwriting_result(result, customer_data)

def manual_underwriting(customer_data: dict):
    """Fallback manual underwriting when LLM fails"""
    try:
        age = customer_data.get('age', 0)
        salary = customer_data.get('salary', 0)
        credit_score = customer_data.get('credit_score', 0)
        loan_amount = customer_data.get('loan_amount', 0)
        employment_type = customer_data.get('employment_type', '')
        
        # Basic criteria check
        eligible = True
        reasons = []
        
        if age < 21:
            eligible = False
            reasons.append(f"Age {age} below minimum 21")
        
        if salary < 20000:
            eligible = False
            reasons.append(f"Salary ₹{salary:,} below minimum ₹20,000")
        
        if credit_score < 650:
            eligible = False
            reasons.append(f"Credit score {credit_score} below minimum 650")
        
        # Loan amount check (should not exceed 24x monthly salary)
        max_loan_amount = salary * 24
        if loan_amount > max_loan_amount:
            eligible = False
            reasons.append(f"Loan amount ₹{loan_amount:,} exceeds maximum ₹{max_loan_amount:,} (24x salary)")
        
        # Age at maturity check (assuming 5-year loan)
        if age + 5 > 60:
            eligible = False
            reasons.append(f"Age at loan maturity would be {age + 5}, exceeding maximum 60")
        
        reason_text = "Meets all criteria" if eligible else "; ".join(reasons)
        
        # Determine risk score
        risk_score = "Low"
        if credit_score < 700:
            risk_score = "Medium"
        if credit_score < 650 or salary < 30000:
            risk_score = "High"
        
        return {
            "eligible": eligible,
            "reason": reason_text,
            "risk_score": risk_score,
            "next_step": "proceed_to_documents" if eligible else "rejected"
        }
        
    except Exception as e:
        return {
            "eligible": False,
            "reason": f"Error in manual underwriting: {str(e)}",
            "risk_score": "High",
            "next_step": "rejected"
        }

def validate_underwriting_result(result: dict, customer_data: dict):
    """Validate and ensure the underwriting result has correct structure"""
    
    # Ensure all required fields exist
    required_fields = ["eligible", "reason", "risk_score", "next_step"]
    for field in required_fields:
        if field not in result:
            # Create a fallback result
            return manual_underwriting(customer_data)
    
    # Ensure boolean type for eligible
    if not isinstance(result['eligible'], bool):
        result['eligible'] = str(result['eligible']).lower() in ['true', 'yes', '1', 'eligible']
    
    # Ensure next_step is valid
    if result['eligible'] and result['next_step'] != 'proceed_to_documents':
        result['next_step'] = 'proceed_to_documents'
    elif not result['eligible'] and result['next_step'] != 'rejected':
        result['next_step'] = 'rejected'
    
    # Ensure risk_score is valid
    valid_risk_scores = ['Low', 'Medium', 'High']
    if result['risk_score'] not in valid_risk_scores:
        # Determine risk score based on data
        credit_score = customer_data.get('credit_score', 0)
        if credit_score >= 750:
            result['risk_score'] = 'Low'
        elif credit_score >= 650:
            result['risk_score'] = 'Medium'
        else:
            result['risk_score'] = 'High'
    
    return result

