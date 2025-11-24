from fastapi import APIRouter
from ..agents.underwriter import underwrite

router = APIRouter()

@router.post("/analyze")
def analyze_customer(customer_data: dict):

    result = underwrite(customer_data)
    return{"decision": result}