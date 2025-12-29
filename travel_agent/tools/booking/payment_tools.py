import random
import string
import uuid
from google.adk.tools.tool_context import ToolContext

def execute_payment(tool_context: ToolContext, payment_mode: str, amount: str) -> str:
    print(f"\n[TOOL LOG] 💳 Processing {amount} via {payment_mode}...")
    
    mode = payment_mode.lower()
    
    if "card" in mode:
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        txn_id = f"TXN-CC-{suffix}"
        
    elif "upi" in mode:
        utr = "".join(random.choices(string.digits, k=12))
        txn_id = f"UPI-REF-{utr}"
        
    elif "netbanking" in mode:
        nums = "".join(random.choices(string.digits, k=8))
        txn_id = f"NB-REF-{nums}"
        
    elif "amazon" in mode or "wallet" in mode:
        uid = str(uuid.uuid4())[:8].upper()
        txn_id = f"APAY-W-{uid}"
        
    else:
        uid = str(uuid.uuid4())[:12].upper()
        txn_id = f"TXN-{uid}"

    tool_context.state["payment_status"] = "COMPLETED"
    tool_context.state["last_txn_id"] = txn_id
    
    return f"PAYMENT SUCCESSFUL. Transaction ID: {txn_id}. Mode: {payment_mode}. Amount: {amount}"