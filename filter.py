def tier_leads(leads, sent_ids):
    tier1, tier2, tier3 = [], [], []
    for row in leads:
        if not row.get("email", "").strip():
            continue
        if row["id"] in sent_ids:
            continue
        if row.get("worth_reaching_out") == "1":
            tier1.append(row)
        elif row.get("has_website") == "0":
            tier2.append(row)
        else:
            tier3.append(row)
    return tier1, tier2, tier3
