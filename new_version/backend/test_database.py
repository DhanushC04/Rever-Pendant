from models import get_db, Conversation, Keynote, Speaker

db = get_db()

# Check latest conversation
conv = db.query(Conversation).order_by(Conversation.id.desc()).first()
print(f"Latest conversation: {conv.title}")

# Check keynotes
keynotes = db.query(Keynote).filter(Keynote.conversation_id == conv.id).all()
print(f"Keynotes: {len(keynotes)}")
for k in keynotes:
    print(f"  [{k.category}] {k.content}")

# Check speakers
speakers = db.query(Speaker).filter(Speaker.conversation_id == conv.id).all()
print(f"Speakers: {len(speakers)}")
for s in speakers:
    print(f"  {s.speaker_label}: {s.total_duration}s")

db.close()