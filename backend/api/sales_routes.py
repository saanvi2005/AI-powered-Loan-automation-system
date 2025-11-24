from fastapi import APIRouter
from pydantic import BaseModel
from ..agents.sales_agent import collect_customer_info
from ..memory import memory
from ..agents.underwriter import underwrite
import json
import re

router = APIRouter()

class Message(BaseModel):
    session_id: str
    user_message: str

def extract_user_data(user_message: str, current_session: dict):
    """Extract all possible data from user message and update session"""
    message_lower = user_message.lower()
    updated = False
    
    # Extract name (more robust)
    if "name" not in current_session:
        name_patterns = [
            r"my name is (\w+ \w+)",
            r"i am (\w+ \w+)", 
            r"name is (\w+ \w+)",
            r"call me (\w+ \w+)",
            r"i'm (\w+ \w+)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                current_session["name"] = match.group(1).title()
                updated = True
                break
    
    # Extract age
    if "age" not in current_session:
        age_match = re.search(r'(\d{2})\s*(?:years|yrs|year|yo)', message_lower)
        if not age_match:
            age_match = re.search(r'\b(\d{2})\b', user_message)
        if age_match and 18 <= int(age_match.group(1)) <= 70:
            current_session["age"] = int(age_match.group(1))
            updated = True
    
    # Extract salary
    if "salary" not in current_session:
        salary_match = re.search(r'(\d{4,6})\s*(?:inr|rs|rupees|salary)', message_lower)
        if not salary_match:
            salary_match = re.search(r'salary.*?(\d{4,6})', message_lower)
        if not salary_match:
            salary_match = re.search(r'(\d{4,6})', user_message)
        if salary_match:
            salary = int(salary_match.group(1))
            if 10000 <= salary <= 500000:
                current_session["salary"] = salary
                updated = True
    
    # Extract credit score
    if "credit_score" not in current_session:
        credit_match = re.search(r'credit.*?(\d{3})', message_lower)
        if not credit_match:
            credit_match = re.search(r'(\d{3})\s*(?:score|credit)', message_lower)
        if not credit_match:
            credit_match = re.search(r'\b(\d{3})\b', user_message)
        if credit_match:
            score = int(credit_match.group(1))
            if 300 <= score <= 900:
                current_session["credit_score"] = score
                updated = True
    
    # Extract loan amount
    if "loan_amount" not in current_session:
        loan_match = re.search(r'loan.*?(\d{4,7})', message_lower)
        if not loan_match:
            loan_match = re.search(r'(\d{4,7})\s*(?:loan|amount)', message_lower)
        if not loan_match:
            loan_match = re.search(r'(\d{4,7})', user_message)
        if loan_match:
            loan_amt = int(loan_match.group(1))
            if 10000 <= loan_amt <= 10000000:
                current_session["loan_amount"] = loan_amt
                updated = True
    
    # Extract employment type
    if "employment_type" not in current_session:
        if any(word in message_lower for word in ["salaried", "salary job", "employed", "working in"]):
            current_session["employment_type"] = "Salaried"
            updated = True
        elif any(word in message_lower for word in ["self-employed", "self employed", "business", "entrepreneur"]):
            current_session["employment_type"] = "Self-employed"
            updated = True
    
    return updated

def is_valid_json_response(text):
    """Check if the response is valid JSON with all required fields"""
    try:
        data = json.loads(text.strip())
        required_fields = ["name", "age", "salary", "credit_score", "loan_amount", "employment_type"]
        
        # Check if all required fields are present and have valid values
        if all(field in data for field in required_fields):
            # Basic validation
            if (isinstance(data.get('age'), int) and 18 <= data['age'] <= 70 and
                isinstance(data.get('salary'), (int, float)) and data['salary'] >= 10000 and
                isinstance(data.get('credit_score'), int) and 300 <= data['credit_score'] <= 900 and
                isinstance(data.get('loan_amount'), (int, float)) and data['loan_amount'] >= 20000 and
                data.get('employment_type') in ['Salaried', 'Self-employed'] and
                isinstance(data.get('name'), str) and len(data['name']) > 1):
                return True
    except:
        pass
    return False

@router.options("/message")
def options_message():
    from fastapi.responses import Response
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:8000"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Accept"
    return response

@router.post("/message")
def chat(message: Message):
    # Get current session data
    session_data = memory.get(message.session_id)
    
    print(f"BEFORE - Session {message.session_id} data: {session_data}")
    
    # Extract data from user message
    extract_user_data(message.user_message, session_data)
    
    print(f"AFTER EXTRACTION - Session {message.session_id} data: {session_data}")
    
    # Update memory with potentially new data
    memory.update(message.session_id, session_data)
    
    # Get updated session data
    updated_session_data = memory.get(message.session_id)
    
    # Check if all fields are already collected in session data
    required_fields = ["name", "age", "salary", "credit_score", "loan_amount", "employment_type"]
    if all(field in updated_session_data for field in required_fields):
        print("ALL FIELDS COLLECTED IN SESSION DATA - Generating JSON")
        # Manually create JSON since LLM might not be doing it
        final_json = {
            "name": updated_session_data["name"],
            "age": updated_session_data["age"],
            "salary": updated_session_data["salary"],
            "credit_score": updated_session_data["credit_score"],
            "loan_amount": updated_session_data["loan_amount"],
            "employment_type": updated_session_data["employment_type"]
        }
        
        # Send to underwriter
        print("=== SENDING TO UNDERWRITER ===")
        decision = underwrite(final_json)
        
        print(f"=== UNDERWRITER RESULT ===")
        print(json.dumps(decision, indent=2))
        print("===========================")
        
        # Handle underwriter decision
        if decision.get('eligible', False) and decision.get('next_step') == 'proceed_to_documents':
            # Eligible - keep session for document verification
            updated_session_data['_stage'] = 'document_verification'
            updated_session_data['_underwriting_result'] = decision
            memory.update(message.session_id, updated_session_data)
            
            return {
                "agent_reply": f"🎉 Great news! {decision.get('reason', 'You are eligible for further processing.')} Please proceed with document verification.",
                "underwriter_result": decision,
                "status": "eligible_for_documents",
                "collected_data": final_json,
                "next_step": "proceed_to_document_upload"
            }
        else:
            # Not eligible - end conversation
            memory.clear(message.session_id)
            return {
                "agent_reply": f"❌ Thank you for your application. {decision.get('reason', 'Unfortunately, you are not eligible at this time.')}",
                "underwriter_result": decision,
                "status": "rejected",
                "collected_data": final_json,
                "next_step": "end"
            }
    
    # Get agent response
    agent_reply = collect_customer_info(
        user_message=message.user_message,
        session_data=updated_session_data
    )
    
    print(f"AGENT REPLY: {agent_reply}")
    
    # Check if agent returned valid JSON
    if is_valid_json_response(agent_reply):
        try:
            json_data = json.loads(agent_reply.strip())
            
            # Send to underwriter
            print("=== SENDING TO UNDERWRITER (JSON RESPONSE) ===")
            decision = underwrite(json_data)
            
            print(f"=== UNDERWRITER RESULT ===")
            print(json.dumps(decision, indent=2))
            print("===========================")
            
            # Handle underwriter decision
            if decision.get('eligible', False) and decision.get('next_step') == 'proceed_to_documents':
                # Eligible - keep session for document verification
                session_data['_stage'] = 'document_verification'
                session_data['_underwriting_result'] = decision
                memory.update(message.session_id, session_data)
                
                return {
                    "agent_reply": f"🎉 Great news! {decision.get('reason', 'You are eligible for further processing.')} Please proceed with document verification.",
                    "underwriter_result": decision,
                    "status": "eligible_for_documents",
                    "collected_data": json_data,
                    "next_step": "proceed_to_document_upload"
                }
            else:
                # Not eligible - end conversation
                memory.clear(message.session_id)
                return {
                    "agent_reply": f"❌ Thank you for your application. {decision.get('reason', 'Unfortunately, you are not eligible at this time.')}",
                    "underwriter_result": decision,
                    "status": "rejected",
                    "collected_data": json_data,
                    "next_step": "end"
                }
        except Exception as e:
            print(f"JSON parsing error: {e}")
    
    # Return the agent's response for continuing conversation
    return {
        "agent_reply": agent_reply,
        "status": "in_progress",
        "collected_so_far": updated_session_data
    }