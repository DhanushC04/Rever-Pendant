"""
Test Keynote Extraction
Run this to verify keynote extraction is working
"""

from keynote_extraction import KeynoteExtractor
from models import get_db, Conversation, Keynote
import sys

def test_keynote_extraction():
    print("\n" + "="*70)
    print("🔑 KEYNOTE EXTRACTION TEST")
    print("="*70 + "\n")
    
    # Test transcripts with different types of keynotes
    test_cases = [
        {
            'name': 'Test 1: Action Items',
            'transcript': '''
                We need to finish the project report by next Friday.
                I should call the client tomorrow morning.
                Let's schedule a meeting with the team.
                We must review the budget before submitting.
            '''
        },
        {
            'name': 'Test 2: Decisions',
            'transcript': '''
                We decided to go with option A for the design.
                The team agreed to hire two more developers.
                We concluded that the deadline should be extended.
            '''
        },
        {
            'name': 'Test 3: Questions',
            'transcript': '''
                What should be our marketing strategy?
                How can we reduce costs?
                When should we launch the product?
                Who will lead the project?
            '''
        },
        {
            'name': 'Test 4: Deadlines',
            'transcript': '''
                The report is due by Friday at 5 PM.
                We have a deadline next Monday for the presentation.
                Everything needs to be completed before the end of this month.
            '''
        },
        {
            'name': 'Test 5: Mixed Content',
            'transcript': '''
                We need to launch the product by next quarter.
                I decided to invest in marketing.
                What should our pricing strategy be?
                The team agreed to work on weekends if necessary.
                Remember to update the documentation before release.
            '''
        }
    ]
    
    extractor = KeynoteExtractor()
    total_keynotes = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'─'*70}")
        print(f"📝 {test_case['name']}")
        print(f"{'─'*70}")
        
        transcript = test_case['transcript'].strip()
        print(f"Transcript length: {len(transcript)} characters\n")
        
        # Extract keynotes
        keynotes = extractor.extract_keynotes(transcript, conversation_id=i)
        
        if keynotes:
            print(f"✅ Found {len(keynotes)} keynotes:\n")
            for j, keynote in enumerate(keynotes, 1):
                category_emoji = {
                    'action_item': '📋',
                    'decision': '✅',
                    'question': '❓',
                    'deadline': '⏰',
                    'important_fact': '💡'
                }.get(keynote['category'], '📌')
                
                print(f"{j}. {category_emoji} [{keynote['category'].upper()}]")
                print(f"   Content: {keynote['content']}")
                print(f"   Importance: {int(keynote['importance_score'] * 100)}%\n")
            
            total_keynotes += len(keynotes)
        else:
            print("❌ No keynotes found\n")
    
    print("\n" + "="*70)
    print(f"📊 SUMMARY: Extracted {total_keynotes} total keynotes from {len(test_cases)} tests")
    print("="*70 + "\n")
    
    return total_keynotes > 0

def test_with_database():
    """Test keynote extraction with actual database conversation"""
    print("\n" + "="*70)
    print("🗄️  DATABASE KEYNOTE TEST")
    print("="*70 + "\n")
    
    db = get_db()
    
    # Get latest conversation
    conversations = db.query(Conversation).order_by(Conversation.id.desc()).limit(3).all()
    
    if not conversations:
        print("⚠️  No conversations found in database")
        print("   Run a full process first (Face → Audio → Summary)")
        db.close()
        return False
    
    print(f"Found {len(conversations)} recent conversation(s)\n")
    
    extractor = KeynoteExtractor()
    
    for conv in conversations:
        print(f"{'─'*70}")
        print(f"📝 Conversation ID: {conv.id}")
        print(f"   Title: {conv.title}")
        print(f"   Date: {conv.timestamp}")
        print(f"{'─'*70}\n")
        
        # Get existing keynotes
        existing_keynotes = db.query(Keynote).filter(
            Keynote.conversation_id == conv.id
        ).all()
        
        print(f"💾 Keynotes in database: {len(existing_keynotes)}")
        
        if existing_keynotes:
            for i, k in enumerate(existing_keynotes, 1):
                print(f"{i}. [{k.category}] {k.content[:60]}...")
        
        # Re-extract to test
        print(f"\n🔄 Re-extracting keynotes from transcript...\n")
        
        if conv.transcript:
            new_keynotes = extractor.extract_keynotes(conv.transcript, conv.id)
            
            if new_keynotes:
                print(f"✅ Newly extracted: {len(new_keynotes)} keynotes")
            else:
                print("⚠️  No keynotes extracted (transcript might be too short)")
        else:
            print("❌ No transcript available")
        
        print()
    
    db.close()
    return True

def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*70)
    print("🔬 EDGE CASE TESTS")
    print("="*70 + "\n")
    
    extractor = KeynoteExtractor()
    
    test_cases = [
        ("Empty string", ""),
        ("Very short", "Hi"),
        ("No keywords", "The weather is nice today. Birds are singing."),
        ("Only punctuation", "!!! ??? ..."),
    ]
    
    for name, transcript in test_cases:
        print(f"Test: {name}")
        print(f"Input: '{transcript}'")
        keynotes = extractor.extract_keynotes(transcript, 999)
        print(f"Result: {len(keynotes)} keynotes")
        print(f"Status: {'✅ Pass' if len(keynotes) == 0 else '⚠️  Unexpected'}\n")
    
    return True

if __name__ == '__main__':
    print("\n🚀 Starting Keynote Extraction Tests...\n")
    
    # Run all tests
    test1 = test_keynote_extraction()
    test2 = test_with_database()
    test3 = test_edge_cases()
    
    # Summary
    print("\n" + "="*70)
    print("🎯 TEST RESULTS")
    print("="*70)
    print(f"Basic Extraction Test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Database Test: {'✅ PASS' if test2 else '⚠️  SKIP (no data)'}")
    print(f"Edge Cases Test: {'✅ PASS' if test3 else '❌ FAIL'}")
    print("="*70 + "\n")
    
    if test1:
        print("✅ Keynote extraction is working correctly!")
        print("\nNext steps:")
        print("1. Run full process (Face → Audio → Summary)")
        print("2. Check History → Conversation → Keynotes tab")
        print("3. Keynotes should appear with categories")
    else:
        print("❌ Keynote extraction has issues")
        print("\nDebugging steps:")
        print("1. Check keynote_extraction.py file exists")
        print("2. Verify no syntax errors: python keynote_extraction.py")
        print("3. Check regex patterns are working")