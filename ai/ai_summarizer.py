from transformers import pipeline

print("🔄 Chargement du modèle BART...")
summarizer = pipeline(
    task="summarization",
    model="facebook/bart-large-cnn"
)

MAX_INPUT_CHARS = 3000  # sécurité tokens

def clean_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text

def summarize_text(text, max_length=130, min_length=30):
    if not text or len(text) < 100:
        return ""

    text = clean_text(text)
    text = text[:MAX_INPUT_CHARS]

    try:
        result = summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )
        return result[0]["summary_text"]

    except Exception as e:
        print("❌ Erreur résumé IA :", e)
        return ""
