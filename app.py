from bisect import bisect_right
from datetime import date

def analyze(data):
    requests, seen = [], set()
    for request in data["requests"]:
        name = request["id"]
        start, end = (date.fromisoformat(request[key]) for key in ("start","end"))
        priority = request["priority"]
        if not isinstance(name,str) or not name.strip() or name in seen or start >= end or type(priority) is not int or priority < 0:
            raise ValueError("Invalid display request")
        seen.add(name)
        requests.append((end,start,name,priority))
    requests.sort()
    ends = [item[0] for item in requests]
    totals, previous = [0], []
    for i, (_, start, _, priority) in enumerate(requests):
        prior = bisect_right(ends,start,hi=i)
        take = totals[prior] + priority > totals[-1]
        totals.append(totals[prior] + priority if take else totals[-1])
        previous.append((take,prior if take else i))
    selected = []
    cursor = len(requests)
    while cursor:
        take, prior = previous[cursor-1]
        if take:
            selected.append(requests[cursor-1][2])
        cursor = prior
    return {"selected":selected[::-1],"priority":totals[-1],"skipped":len(requests)-len(selected)}

if __name__ == "__main__":
    import json
    from pathlib import Path
    import sys
    try:
        path, = sys.argv[1:]
        result = analyze(json.loads(Path(path).read_text(encoding="utf-8")))
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        sys.exit(2)
