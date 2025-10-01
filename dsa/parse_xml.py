import xml.etree.ElementTree as ET
import json
import re
from typing import List, Dict

def parse_sms_xml(path: str) -> List[Dict]:
    tree = ET.parse(path)
    root = tree.getroot()
    transactions = []
    id =0
    for sms in root.findall("sms"):
        body = sms.attrib.get("body", "")


        has_amount = re.search(r"[\d,]+\s*RWF", body)
        keywords = ["payment of", "received", "withdrawn", "transferred", "deposit", "purchased", "airtime"]
        id = id+1
        if not has_amount or not any(k in body.lower() for k in keywords):


            transactions.append({
                "Id":id,
                "transaction_type": "non_transaction",
                "sender": None,
                "receiver": None,
                "amount": None,
                "timestamp": sms.attrib.get("readable_date"),
                "raw_body": body
            })
            continue

        # --- Extract amount ---
        amount_match = re.search(r"(?:payment of|received|transferred|withdrawn|purchased)?\s*([\d,]+)\s*RWF", body, re.IGNORECASE)

        
        date_match = re.search(r"at\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})", body)

        
        body_lower = body.lower()
        if "payment of" in body_lower:
            ttype = "payment"
        elif "received" in body_lower:
            ttype = "deposit"
        elif "withdrawn" in body_lower:
            ttype = "withdrawal"
        elif "purchased" in body_lower or "airtime" in body_lower:
            ttype = "airtime"
        elif "transferred" in body_lower:
            ttype = "transfer"
        else:
            ttype = "other"

        receiver, sender = None, None

        if ttype == "payment":
            receiver_match = re.search(r"to\s+(.+?)(?:\s\d+| at| has been|\.|$)", body, re.IGNORECASE)
            receiver = receiver_match.group(1).strip() if receiver_match else None
            sender = "Me"

        elif ttype == "deposit":
            sender_match = re.search(r"from\s+(.+?)(?:\s\d+| at| has been|\.|$)", body, re.IGNORECASE)
            sender = sender_match.group(1).strip() if sender_match else None
            receiver = "My Account"

        elif ttype == "withdrawal":
            receiver = "Cash Withdrawal"
            sender = "Me"

        elif ttype == "transfer":
            receiver_match = re.search(r"transferred to\s+(.+?)(?:\sfrom| at|\.|$)", body, re.IGNORECASE)
            receiver = receiver_match.group(1).strip() if receiver_match else None
            sender = "Me"

        elif ttype == "airtime":
            receiver = "Airtime"
            sender = "Me"

        else:
            receiver_match = re.search(r"to\s+(.+?)(?:\s\d+| at| has been|\.|$)", body, re.IGNORECASE)
            receiver = receiver_match.group(1).strip() if receiver_match else None
            sender_match = re.search(r"from\s+(.+?)(?:\s\d+| at| has been|\.|$)", body, re.IGNORECASE)
            sender = sender_match.group(1).strip() if sender_match else "Me"

        parsed = {
            "Id":"TxID"+str(id),
            "transaction_type": ttype,
            "amount": int(amount_match.group(1).replace(",", "")) if amount_match else None,
            "sender": sender,
            "receiver": receiver,
            "timestamp": date_match.group(1) if date_match else sms.attrib.get("readable_date"),
            "raw_body": body
        }

        transactions.append(parsed)

    return transactions


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "modified_sms_sample.xml"
    tx = parse_sms_xml(path)
    print(json.dumps(tx, indent=2, ensure_ascii=False))
