GET_CLAIM_STATUS_QUERY = "SELECT status FROM life_claim.claims WHERE CLAIM_NUMBER = %s"

GET_POLICY_DETAILS_QUERY="SELECT policyNumber, Name FROM clientdetails WHERE MobileNo = %s AND DATE(DOB) = %s"