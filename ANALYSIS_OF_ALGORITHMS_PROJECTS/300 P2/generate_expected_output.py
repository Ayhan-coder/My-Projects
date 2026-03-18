import string
from collections import Counter
import sys

# NLP helper functions - copied from solution.py

def load_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

def load_data(text_path, vocab_path, stopwords_path):
    text = load_file(text_path)
    vocab = set(load_file(vocab_path))
    stopwords = set(load_file(stopwords_path))
    return text, vocab, stopwords

def lowercase_sentence(sentence):
    return sentence.lower()

def remove_punctuation(sentence):
    translator = str.maketrans('', '', string.punctuation)
    return sentence.translate(translator)

def remove_stopwords_from_sentence(sentence, stopwords):
    words = sentence.split()
    return [word for word in words if word not in stopwords]

def preprocess_sentence(sentence, stopwords):
    # lowercase -> remove punctuation -> remove stopwords
    s = lowercase_sentence(sentence)
    s = remove_punctuation(s)
    return remove_stopwords_from_sentence(s, stopwords)

def compute_tf(sentences, vocab, stopwords):
    tf_counts = Counter()
    for sentence in sentences:
        words = preprocess_sentence(sentence, stopwords)
        # Only count words that are in the vocabulary
        filtered_words = [word for word in words if word in vocab]
        tf_counts.update(filtered_words)
    
    # Ensure all vocab words are present (even if count is 0)
    final_tf = {word: tf_counts[word] for word in vocab}
    return final_tf

def compute_df(sentences, vocab, stopwords):
    df_counts = Counter()
    for sentence in sentences:
        words = set(preprocess_sentence(sentence, stopwords)) # Unique words per sentence
        # Only count words that are in the vocabulary
        filtered_words = [word for word in words if word in vocab]
        df_counts.update(filtered_words)
            
    # Ensure all vocab words are present
    final_df = {word: df_counts[word] for word in vocab}
    return final_df

def main():
    # Use paths relative to the script location, assuming resources folder is present
    text_path = "resources/sample_text.txt"
    vocab_path = "resources/sample_vocab.txt"
    stopwords_path = "resources/sample_stopwords.txt"
    
    print(f"Loading data from: {text_path}, {vocab_path}, {stopwords_path}")
    text, vocab, stopwords = load_data(text_path, vocab_path, stopwords_path)
    
    print(f"Number of sentences: {len(text)}")
    print(f"Vocabulary size: {len(vocab)}")
    print(f"Stopwords count: {len(stopwords)}")
    
    print("\n--- Computing Expected TF ---")
    tf_results = compute_tf(text, vocab, stopwords)
    print("Term-Frequency (TF) Result:")
    for word in sorted(tf_results.keys()):
        print(f"{word}: {tf_results[word]}")
        
    print("\n--- Computing Expected DF ---")
    df_results = compute_df(text, vocab, stopwords)
    print("Document-Frequency (DF) Result:")
    for word in sorted(df_results.keys()):
        print(f"{word}: {df_results[word]}")

if __name__ == "__main__":
    main()
