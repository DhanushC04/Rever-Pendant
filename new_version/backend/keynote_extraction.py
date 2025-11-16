"""
Enhanced Keynote Extraction
Works without transformers - uses regex patterns
"""

import re
from models import get_db, Keynote

class KeynoteExtractor:
    def __init__(self):
        self.categories = [
            "action_item",
            "decision",
            "question",
            "important_fact",
            "deadline"
        ]
    
    def extract_keynotes(self, transcript, conversation_id):
        """
        Extract keynotes from transcript
        Returns list of keynotes with categories
        """
        if not transcript or len(transcript) < 20:
            print("⚠️ Transcript too short for keynote extraction")
            return []
        
        keynotes = []
        
        try:
            # Extract different types of keynotes
            keynotes.extend(self._extract_action_items(transcript))
            keynotes.extend(self._extract_decisions(transcript))
            keynotes.extend(self._extract_questions(transcript))
            keynotes.extend(self._extract_deadlines(transcript))
            keynotes.extend(self._extract_important_facts(transcript))
            
            # Save to database
            if keynotes:
                self._save_keynotes(conversation_id, keynotes)
                print(f"✅ Extracted {len(keynotes)} keynotes")
            else:
                print("⚠️ No keynotes found in transcript")
            
            return keynotes
            
        except Exception as e:
            print(f"❌ Keynote extraction error: {e}")
            return []
    
    def _extract_action_items(self, transcript):
        """Extract action items and to-dos"""
        patterns = [
            r"(?:need to|should|must|have to|going to|will)\s+([^.,;!?]+)",
            r"(?:action item|todo|task):\s*([^.,;!?]+)",
            r"(?:let's|we should|we need to)\s+([^.,;!?]+)",
            r"(?:I will|I'll|we will|we'll)\s+([^.,;!?]+)",
        ]
        
        action_items = []
        seen = set()  # Avoid duplicates
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches:
                content = match.strip()
                # Filter: must be 15-200 chars, not already seen
                if 15 <= len(content) <= 200 and content.lower() not in seen:
                    action_items.append({
                        'content': content,
                        'category': 'action_item',
                        'importance_score': 0.9
                    })
                    seen.add(content.lower())
        
        return action_items[:5]  # Top 5
    
    def _extract_decisions(self, transcript):
        """Extract decisions made"""
        patterns = [
            r"(?:decided|agreed|concluded|determined)\s+(?:that\s+)?([^.,;!?]+)",
            r"(?:decision|verdict):\s*([^.,;!?]+)",
            r"(?:we'll go with|we chose|we selected)\s+([^.,;!?]+)",
        ]
        
        decisions = []
        seen = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches:
                content = match.strip()
                if 15 <= len(content) <= 200 and content.lower() not in seen:
                    decisions.append({
                        'content': content,
                        'category': 'decision',
                        'importance_score': 0.85
                    })
                    seen.add(content.lower())
        
        return decisions[:5]
    
    def _extract_questions(self, transcript):
        """Extract important questions"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', transcript)
        questions = []
        seen = set()
        
        # Look for question patterns
        question_keywords = ['why', 'how', 'what', 'when', 'where', 'who', 'can we', 'should we', 'would']
        
        for sentence in sentences:
            sentence = sentence.strip()
            # Check if it's a question (contains ? or starts with question word)
            if sentence and len(sentence) > 15:
                lower_sent = sentence.lower()
                if any(lower_sent.startswith(kw) for kw in question_keywords) or '?' in sentence:
                    content = sentence.rstrip('?') + '?'
                    if content.lower() not in seen and len(content) <= 200:
                        questions.append({
                            'content': content,
                            'category': 'question',
                            'importance_score': 0.7
                        })
                        seen.add(content.lower())
        
        return questions[:3]
    
    def _extract_deadlines(self, transcript):
        """Extract deadlines and time-sensitive items"""
        patterns = [
            r"(?:by|before|until|deadline is?)\s+([^.,;!?]+)",
            r"(?:due|expires?)\s+([^.,;!?]+)",
            r"(?:next|this)\s+(week|month|monday|tuesday|wednesday|thursday|friday|saturday|sunday)([^.,;!?]*)",
        ]
        
        deadlines = []
        seen = set()
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    content = ' '.join(match).strip()
                else:
                    content = match.strip()
                
                if 10 <= len(content) <= 200 and content.lower() not in seen:
                    deadlines.append({
                        'content': content,
                        'category': 'deadline',
                        'importance_score': 0.95
                    })
                    seen.add(content.lower())
        
        return deadlines[:3]
    
    def _extract_important_facts(self, transcript):
        """Extract important facts using simple heuristics"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', transcript)
        facts = []
        seen = set()
        
        # Importance indicators
        importance_patterns = [
            r'\b(important|critical|essential|key|vital|crucial)\b',
            r'\b(note that|remember|keep in mind|don\'t forget)\b',
            r'\b(the main|the primary|the core)\b',
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if 20 <= len(sentence) <= 200:
                # Check if sentence contains importance indicators
                for pattern in importance_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        if sentence.lower() not in seen:
                            facts.append({
                                'content': sentence,
                                'category': 'important_fact',
                                'importance_score': 0.75
                            })
                            seen.add(sentence.lower())
                        break
        
        return facts[:5]
    
    def _save_keynotes(self, conversation_id, keynotes):
        """Save keynotes to database"""
        db = get_db()
        
        try:
            saved_count = 0
            for keynote_data in keynotes:
                keynote = Keynote(
                    conversation_id=conversation_id,
                    content=keynote_data['content'],
                    importance_score=keynote_data['importance_score'],
                    category=keynote_data['category']
                )
                db.add(keynote)
                saved_count += 1
            
            db.commit()
            print(f"✅ Saved {saved_count} keynotes to database")
            return True
        
        except Exception as e:
            db.rollback()
            print(f"❌ Error saving keynotes: {e}")
            return False
        
        finally:
            db.close()
    
    def get_keynotes_by_conversation(self, conversation_id):
        """Retrieve keynotes for a conversation"""
        db = get_db()
        
        try:
            keynotes = db.query(Keynote).filter(
                Keynote.conversation_id == conversation_id
            ).order_by(Keynote.importance_score.desc()).all()
            
            result = [{
                'id': k.id,
                'content': k.content,
                'category': k.category,
                'importance_score': k.importance_score,
                'is_completed': k.is_completed
            } for k in keynotes]
            
            return result
            
        except Exception as e:
            print(f"❌ Error retrieving keynotes: {e}")
            return []
        
        finally:
            db.close()