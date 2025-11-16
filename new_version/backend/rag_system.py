from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os

class RAGChatSystem:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
        self.index = faiss.IndexFlatL2(self.dimension)
        self.conversation_ids = []
        self.conversation_texts = []
        self.load_index()
    
    def add_conversation_to_index(self, conversation_id, transcript):
        embedding = self.model.encode([transcript])
        self.index.add(embedding)
        self.conversation_ids.append(conversation_id)
        self.conversation_texts.append(transcript)
        self.save_index()
    
    def semantic_search(self, query, top_k=5):
        if len(self.conversation_ids) == 0:
            return []
        
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, min(top_k, len(self.conversation_ids)))
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.conversation_ids):
                results.append({
                    'conversation_id': self.conversation_ids[idx],
                    'text_snippet': self.conversation_texts[idx][:200],
                    'similarity_score': float(1 / (1 + distances[0][i]))
                })
        
        return results
    
    def chat_with_history(self, user_query):
        relevant_convs = self.semantic_search(user_query, top_k=3)
        
        if not relevant_convs:
            return {
                'response': "I don't have any relevant conversations to reference.",
                'sources': []
            }
        
        from models import get_db, Conversation
        db = get_db()
        
        context = "Based on your past conversations:\n\n"
        sources = []
        
        for conv_data in relevant_convs:
            conv = db.query(Conversation).filter(
                Conversation.id == conv_data['conversation_id']
            ).first()
            
            if conv:
                context += f"From {conv.timestamp.strftime('%Y-%m-%d')}:\n{conv.transcript[:500]}\n\n"
                sources.append({
                    'id': conv.id,
                    'title': conv.title,
                    'date': conv.timestamp.strftime('%Y-%m-%d'),
                    'similarity': conv_data['similarity_score']
                })
        
        db.close()
        
        response = context[:1000]
        
        return {
            'response': response,
            'sources': sources
        }
    
    def save_index(self):
        os.makedirs('rag_storage', exist_ok=True)
        faiss.write_index(self.index, 'rag_storage/conversations.index')
        
        with open('rag_storage/mappings.pkl', 'wb') as f:
            pickle.dump({
                'conversation_ids': self.conversation_ids,
                'conversation_texts': self.conversation_texts
            }, f)
    
    def load_index(self):
        try:
            if os.path.exists('rag_storage/conversations.index'):
                self.index = faiss.read_index('rag_storage/conversations.index')
                
                with open('rag_storage/mappings.pkl', 'rb') as f:
                    data = pickle.load(f)
                    self.conversation_ids = data['conversation_ids']
                    self.conversation_texts = data['conversation_texts']
        except:
            pass

rag_system = RAGChatSystem()