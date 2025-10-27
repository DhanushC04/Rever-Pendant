from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    text = text.strip()
    if not text or text == "[No speech detected]":
        return "No speech detected to summarize."
    
    # Handle long transcripts by chunking if needed
    max_len = 800
    if len(text) > max_len:
        chunks = [text[i:i+max_len] for i in range(0, len(text), max_len)]
        summaries = []
        for chunk in chunks:
            res = summarizer(chunk, max_length=60, min_length=20, do_sample=False)
            summaries.append(res[0]['summary_text'])
        return " ".join(summaries)
    else:
        result = summarizer(text, max_length=60, min_length=20, do_sample=False)
        return result[0]['summary_text']
