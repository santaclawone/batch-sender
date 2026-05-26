"""Generate batch summaries for the batch-sender GitHub Pages frontend."""
import json, os, glob

basedir = r'C:\Users\openclaw_AI\.openclaw\workspace\audit-reports-hunter\hunter_output\fully_audited'
tracker = r'C:\Users\openclaw_AI\.openclaw\workspace\audit-reports-hunter\hunter_output\sent_tracker.csv'

# Load sent tracker
sent_entries = set()
with open(tracker, encoding='utf-8') as f:
    next(f)
    for line in f:
        parts = line.strip().split(',')
        if len(parts) >= 3:
            sent_entries.add((parts[0].lower(), parts[1].lower().rstrip('/'), parts[2].lower()))

batch_summaries = []

# Industry overrides for known batch ranges
INDUSTRY_MAP = {}
for i in range(0, 2):
    INDUSTRY_MAP[i] = '🔧 Construction'
for i in range(2, 20):
    INDUSTRY_MAP[i] = '🏨 Hotels'
for i in range(20, 30):
    INDUSTRY_MAP[i] = '🚜 Machinery/Farm'
for i in range(30, 40):
    INDUSTRY_MAP[i] = '🪨 Stone/Kitchens'
for i in range(50, 60):
    INDUSTRY_MAP[i] = '🏥 Health/Vets'
for i in range(100, 110):
    INDUSTRY_MAP[i] = '🏦 Insurance'
for i in range(170, 172):
    INDUSTRY_MAP[i] = '💍 Fashion/Boutiques'

for bid in range(172):
    path = os.path.join(basedir, f'batch_{bid:04d}.json')
    if not os.path.exists(path):
        continue
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    
    seen_names = set()
    names_preview = []
    score_sum = 0
    sent_in_batch = 0
    unsent_with_email = 0
    has_hotels = 0
    
    for d in data:
        name = d.get('businessName', '').strip()
        lname = name.lower()
        url = d.get('url', '').strip().lower().rstrip('/')
        emails = d.get('emails', [])
        score = d.get('score', 0)
        score_sum += score
        
        is_sent = any((lname, url, e.lower()) in sent_entries for e in emails)
        if is_sent:
            sent_in_batch += 1
        elif emails:
            unsent_with_email += 1
        
        if lname not in seen_names:
            seen_names.add(lname)
            names_preview.append(name[:40])
            if any(k in lname for k in ['hotel', 'lodge', 'manor', 'inn', 'arms', 'castle', 'villa', 'suite', 'resort', 'hostel']):
                has_hotels += 1
    
    unique_count = len(seen_names)
    avg_score = round(score_sum / len(data)) if data else 0
    
    # Auto-industry if not in map
    industry = INDUSTRY_MAP.get(bid, '📋 Various')
    if bid not in INDUSTRY_MAP:
        hotel_pct = has_hotels / unique_count if unique_count else 0
        if hotel_pct > 0.5:
            industry = '🏨 Hotels'
        elif hotel_pct > 0.2:
            industry = '🏨 Hotels mix'
    
    batch_summaries.append({
        'batch': bid,
        'num': f'{bid:04d}',
        'total': len(data),
        'unique': unique_count,
        'sent': sent_in_batch,
        'unsent': unsent_with_email,
        'avg_score': avg_score,
        'industry': industry,
        'preview': names_preview[:6],
    })

# Output
out = {
    'total_batches': len(batch_summaries),
    'total_sent': sum(b['sent'] for b in batch_summaries),
    'total_unsent': sum(b['unsent'] for b in batch_summaries),
    'batches': batch_summaries,
}

# Save for frontend
out_path = r'C:\Users\openclaw_AI\.openclaw\workspace\batch-sender\batches.json'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f'Saved {len(batch_summaries)} batch summaries to {out_path}')
print(f'Total unsent: {sum(b["unsent"] for b in batch_summaries)}')
print(f'Total sent: {sum(b["sent"] for b in batch_summaries)}')
