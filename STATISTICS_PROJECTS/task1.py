import random
# Step 1: Read the sentences.txt file and remove <|start|> and <|end|> tokens
def read_sentences(file_path):
    sentences = []
    file = open(file_path, 'r')
    for line in file:
        words = line.strip().split()
        cleaned_sentence = []
        for word in words:
            if word != "<|start|>" and word != "<|end|>":
                cleaned_sentence.append(word)
        sentences.append(cleaned_sentence)
    file.close()
    return sentences
# Step 2: Calculate conditional probabilities
def calculate_conditional_probabilities(sentences):
    word_counts = {}
    conditional_counts = {}
    for sentence in sentences:
        sentence = ['<|start|>'] + sentence + ['<|end|>']  # Add <|start|> and <|end|>
        for i in range(len(sentence) - 1):
            w1 = sentence[i]
            w2 = sentence[i + 1]
            # Update word counts
            if w1 in word_counts:
                word_counts[w1] += 1
            else:
                word_counts[w1] = 1
            # Update conditional counts
            if w1 not in conditional_counts:
                conditional_counts[w1] = {}
            if w2 in conditional_counts[w1]:
                conditional_counts[w1][w2] += 1
            else:
                conditional_counts[w1][w2] = 1
    # Calculate conditional probabilities P(w2 | w1)
    conditional_probabilities = {}
    for w1 in conditional_counts:
        conditional_probabilities[w1] = {}
        total_w1 = word_counts[w1]
        for w2 in conditional_counts[w1]:
            count = conditional_counts[w1][w2]
            conditional_probabilities[w1][w2] = float(count) / total_w1
    return conditional_probabilities
# Step 3: Generate sentences using conditional probabilities
def generate_sentence(conditional_probabilities):
    sentence = []
    current_word = '<|start|>'
    while True:
        if current_word not in conditional_probabilities:
            break
        next_words = list(conditional_probabilities[current_word].keys())
        probabilities = list(conditional_probabilities[current_word].values())
        # Randomly choose next word based on probabilities
        total = sum(probabilities)
        rnd = random.uniform(0, total)
        upto = 0
        for word, prob in zip(next_words, probabilities):
            if upto + prob >= rnd:
                next_word = word
                break
            upto += prob
        if next_word == "<|end|>":
            break
        sentence.append(next_word)
        current_word = next_word
    return " ".join(sentence)

# Main function to execute the task
if __name__ == "__main__":
    # Load sentences and remove <|start|> and <|end|> tokens
    sentences = read_sentences('sentences.txt')
    # Calculate conditional probabilities
    conditional_probabilities = calculate_conditional_probabilities(sentences)
    # Generate 5 sentences
    for _ in range(20):
        sentence = generate_sentence(conditional_probabilities)
        print("Generated Sentence:", sentence)
