ENGINEER_PROMPT = """
You are a Senior Embedded Linux BSP Engineer.

Analyze the following BSP migration.

Filename:
{filename}

Vendor Changes

{vendor_changes}

Customer Changes

{customer_changes}

Tasks

1. Summarize vendor modifications.

2. Summarize customer modifications.

3. Detect conflicts.

4. Recommend merge strategy.

5. Estimate risk.

Return ONLY JSON.

{{
    "summary":"",
    "recommendation":"",
    "risk":"",
    "confidence":90
}}
"""