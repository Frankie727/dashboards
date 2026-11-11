import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "dashboard_data.json"


def call_get_job_details(work_item_id):
    """Call EDI-Prod-get-job-details through the configured MCP CLI."""
    result = subprocess.run(["npx", "mcp", "call", "EDI-Prod-get-job-details",
                             json.dumps({"jobNumber": work_item_id})],
                            capture_output=True, text=True, check=True)
    return result.stdout


def parse_job_details(text, fallback_id):
    def field(name):
        m = re.search(rf"\*\*{re.escape(name)}\*\*:\s*(.*)", text, re.I)
        return m.group(1).strip() if m else None
    return {
        "workItemId": fallback_id,
        "product": field("product"),
        "productArea": field("area"),
        "module": field("module"),
        "status": field("status"),
        "changeType": field("changeType"),
        "createdTime": (field("createdAt") or "")[:10] or None,
        "defectIntroducedWI": field("Defect Introduced in WI"),
        "defectIntroducedCI": field("Defect Introduced in Checkin"),
    }


def cached_items():
    items = {}
    for filename in ("edi_workitems_enriched.json", "edi_workitems_output.json"):
        path = ROOT / filename
        if path.exists():
            doc = json.loads(path.read_text(encoding="utf-8"))
            for item in doc.get("data", []):
                items.setdefault(item.get("workItemId"), item)
    raw = ROOT / "glw_workitems_raw.json"
    if raw.exists():
        for batch in json.loads(raw.read_text(encoding="utf-8")).get("batches", []):
            for item in batch.get("workItems", []):
                items.setdefault(item.get("id"), item)
    return items


def normalize(item, item_id, product_hint):
    return {
        "workItemId": item_id,
        "product": item.get("product") or product_hint,
        "productArea": item.get("productArea") or item.get("area"),
        "module": item.get("module"),
        "status": item.get("status"),
        "changeType": item.get("changeType"),
        "createdTime": (item.get("createdTime") or item.get("createdAt") or "")[:10] or None,
        "defectIntroducedWI": item.get("defectIntroducedWI"),
        "defectIntroducedCI": item.get("defectIntroducedCI"),
    }


def main(live=False):
    ent_ids = [x.strip() for x in (ROOT / "all_work_item_ids.txt").read_text().splitlines() if x.strip()][:199]
    raw = json.loads((ROOT / "glw_workitems_raw.json").read_text(encoding="utf-8"))
    glw_ids = [i["id"] for b in raw.get("batches", []) for i in b.get("workItems", [])
               if i.get("status") == "WRK"][:19]
    ids = [(x, "ENT") for x in ent_ids] + [(x, "GLW") for x in glw_ids]
    cache = cached_items()
    data = []
    for item_id, product in ids:
        if live:
            try:
                data.append(parse_job_details(call_get_job_details(item_id), item_id))
                continue
            except Exception as exc:
                print(f"live fetch failed for {item_id}: {exc}", file=sys.stderr)
        data.append(normalize(cache.get(item_id, {}), item_id, product))
    with_defect = sum(bool(x["defectIntroducedWI"] or x["defectIntroducedCI"]) for x in data)
    output = {"meta": {"totalCount": len(data),
                       "itemsWithDefectIntroduced": with_defect,
                       "itemsWithoutDefectIntroduced": len(data) - with_defect},
              "data": data}
    OUT.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main("--live" in sys.argv)
