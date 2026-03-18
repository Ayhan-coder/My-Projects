"""
CMPE 300 Project 2
MPI Parallel NLP System

Student Names: Ali Ayhan Gunder , Yigit Memceoktay
Student IDs: 2021400219 , 2022402006
"""

import sys
import argparse
import string
from collections import Counter
from mpi4py import MPI

# Helper functions for text processing

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

def to_lower(sentence):
    # just make everything lowercase
    return sentence.lower()

def strip_punct(sentence):
    # remove all punctuation marks
    translator = str.maketrans('', '', string.punctuation)
    return sentence.translate(translator)

def filter_stopwords(sentence, stopwords):
    # split into words and remove common ones
    words = sentence.split()
    return [word for word in words if word not in stopwords]

def clean_text(sentence, stopwords):
    # do all the cleaning steps in one go
    s = to_lower(sentence)
    s = strip_punct(s)
    return filter_stopwords(s, stopwords)

def compute_tf(sentences, vocab, stopwords):
    # count how many times each word appears
    tf_counts = Counter()
    for sentence in sentences:
        if isinstance(sentence, list):
            words = sentence
        else:
            words = clean_text(sentence, stopwords)
            
        filtered_words = [word for word in words if word in vocab]
        tf_counts.update(filtered_words)
    
    return {word: tf_counts[word] for word in vocab}

def compute_df(sentences, vocab, stopwords):
    # count in how many sentences each word shows up
    df_counts = Counter()
    for sentence in sentences:
        if isinstance(sentence, list):
            words = set(sentence)
        else:
            words = set(clean_text(sentence, stopwords))
            
        filtered_words = [word for word in words if word in vocab]
        df_counts.update(filtered_words)
            
    return {word: df_counts[word] for word in vocab}

def chunk_data(data, num_chunks):
    # split the data into equal parts
    if num_chunks <= 0:
        return []

    n = len(data)
    if n == 0:
        return [[] for _ in range(num_chunks)]

    base = n // num_chunks
    remainder = n % num_chunks

    chunks = []
    start = 0
    for i in range(num_chunks):
        extra = 1 if i < remainder else 0
        end = start + base + extra
        chunks.append(data[start:end])
        start = end

    return chunks


def merge_counts(counts_list):
    # combine all the count dictionaries
    merged = Counter()
    for counts in counts_list:
        merged.update(counts)
    return dict(merged)

# --- MPI Communication Patterns ---
# Each pattern implements a different parallel processing strategy using MPI Send/Recv

def run_pattern_1(comm, args):
    # manager sends chunks to workers, they process and send back
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    if rank == 0:
        # manager part
        text, vocab, stopwords = load_data(args.text, args.vocab, args.stopwords)
        
        num_workers = size - 1
        if num_workers < 1:
            print("Error: Pattern 1 needs at least 2 processes.")
            sys.exit(1)
            
        chunks = chunk_data(text, num_workers)
        
        # send work to each worker
        for i in range(num_workers):
            comm.send((chunks[i], vocab, stopwords), dest=i+1, tag=1)
            
        # get results back
        results = []
        for i in range(num_workers):
            tf_counts = comm.recv(source=i+1, tag=2)
            results.append(tf_counts)
            
        final_tf = merge_counts(results)
        
        print("Term-Frequency (TF) Result:")
        for word in sorted(final_tf.keys()):
            print(f"{word}: {final_tf[word]}")
            
    else:
        # worker part
        data, vocab, stopwords = comm.recv(source=0, tag=1)
        tf_counts = compute_tf(data, vocab, stopwords)
        comm.send(tf_counts, dest=0, tag=2)

def run_pattern_2(comm, args):
    # pipeline: data goes through stages one by one
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    if size != 5:
        if rank == 0: print("Error: Pattern 2 needs exactly 5 processes.")
        sys.exit(1)

    if rank == 0:
        # manager sends chunks to start the pipeline
        text, vocab, stopwords = load_data(args.text, args.vocab, args.stopwords)
        
        # break into small chunks
        num_chunks = max(1, len(text) // 10)
        chunks = chunk_data(text, num_chunks)
        
        for chunk in chunks:
            comm.send(chunk, dest=1, tag=1)
        
        comm.send(None, dest=1, tag=1) # signal end
        
        final_tf = comm.recv(source=4, tag=5)
        
        print("Term-Frequency (TF) Result:")
        for word in sorted(final_tf.keys()):
            print(f"{word}: {final_tf[word]}")

    elif rank == 1:
        # first stage: lowercase
        while True:
            data = comm.recv(source=0, tag=1)
            if data is None:
                comm.send(None, dest=2, tag=2)
                break
            processed = [to_lower(s) for s in data]
            comm.send(processed, dest=2, tag=2)

    elif rank == 2:
        # second stage: remove punctuation
        while True:
            data = comm.recv(source=1, tag=2)
            if data is None:
                comm.send(None, dest=3, tag=3)
                break
            processed = [strip_punct(s) for s in data]
            comm.send(processed, dest=3, tag=3)

    elif rank == 3:
        # third stage: remove stopwords
        _, _, stopwords = load_data(args.text, args.vocab, args.stopwords)
        while True:
            data = comm.recv(source=2, tag=3)
            if data is None:
                comm.send(None, dest=4, tag=4)
                break
            processed = [filter_stopwords(s, stopwords) for s in data]
            comm.send(processed, dest=4, tag=4)

    elif rank == 4:
        # last stage: count TF
        _, vocab, _ = load_data(args.text, args.vocab, args.stopwords)
        total_tf = Counter()
        while True:
            data = comm.recv(source=3, tag=4)
            if data is None:
                break
            tf = compute_tf(data, vocab, set())
            total_tf.update(tf)
        comm.send(dict(total_tf), dest=0, tag=5)

def run_pattern_3(comm, args):
    # multiple pipelines running at the same time
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    num_pipelines = (size - 1) // 4
    if (size - 1) % 4 != 0 or num_pipelines < 1:
        if rank == 0: print("Error: Pattern 3 needs 1 + 4k processes.")
        sys.exit(1)

    if rank == 0:
        # manager splits data for each pipeline
        text, vocab, stopwords = load_data(args.text, args.vocab, args.stopwords)
        pipeline_chunks = chunk_data(text, num_pipelines)
        
        for p in range(num_pipelines):
            head_rank = 1 + p * 4
            p_text = pipeline_chunks[p]
            
            # split into smaller chunks for the pipeline
            num_small_chunks = max(1, len(p_text) // 10)
            small_chunks = chunk_data(p_text, num_small_chunks)
            
            for chunk in small_chunks:
                comm.send(chunk, dest=head_rank, tag=1)
            comm.send(None, dest=head_rank, tag=1)
            
        results = []
        for p in range(num_pipelines):
            tail_rank = 1 + p * 4 + 3
            tf_counts = comm.recv(source=tail_rank, tag=5)
            results.append(tf_counts)
            
        final_tf = merge_counts(results)
        
        print("Term-Frequency (TF) Result:")
        for word in sorted(final_tf.keys()):
            print(f"{word}: {final_tf[word]}")
            
    else:
        # each worker in a pipeline stage
        worker_id = rank - 1
        stage_idx = worker_id % 4
        
        prev_rank = rank - 1
        next_rank = rank + 1
        
        if stage_idx == 0: # lowercase stage
            source = 0
            dest = next_rank
            while True:
                data = comm.recv(source=source, tag=1)
                if data is None:
                    comm.send(None, dest=dest, tag=2)
                    break
                processed = [to_lower(s) for s in data]
                comm.send(processed, dest=dest, tag=2)
                
        elif stage_idx == 1: # punctuation stage
            source = prev_rank
            dest = next_rank
            while True:
                data = comm.recv(source=source, tag=2)
                if data is None:
                    comm.send(None, dest=dest, tag=3)
                    break
                processed = [strip_punct(s) for s in data]
                comm.send(processed, dest=dest, tag=3)
                
        elif stage_idx == 2: # stopwords stage
            source = prev_rank
            dest = next_rank
            _, _, stopwords = load_data(args.text, args.vocab, args.stopwords)
            while True:
                data = comm.recv(source=source, tag=3)
                if data is None:
                    comm.send(None, dest=dest, tag=4)
                    break
                processed = [filter_stopwords(s, stopwords) for s in data]
                comm.send(processed, dest=dest, tag=4)
                
        elif stage_idx == 3: # TF count stage
            source = prev_rank
            dest = 0
            _, vocab, _ = load_data(args.text, args.vocab, args.stopwords)
            total_tf = Counter()
            while True:
                data = comm.recv(source=source, tag=4)
                if data is None:
                    break
                tf = compute_tf(data, vocab, set())
                total_tf.update(tf)
            comm.send(dict(total_tf), dest=dest, tag=5)

def run_pattern_4(comm, args):
    # workers pair up and exchange data, then split tasks
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    num_workers = size - 1
    if num_workers < 2 or num_workers % 2 != 0:
        if rank == 0: print("Error: Pattern 4 needs 1 + 2k processes.")
        sys.exit(1)

    if rank == 0:
        # manager sends data to workers
        text, vocab, stopwords = load_data(args.text, args.vocab, args.stopwords)
        chunks = chunk_data(text, num_workers)
        
        for i in range(num_workers):
            comm.send((chunks[i], vocab, stopwords), dest=i+1, tag=1)
            
        tf_results = []
        df_results = []
        
        for i in range(num_workers):
            worker_rank = i + 1
            if worker_rank % 2 != 0:
                tf = comm.recv(source=worker_rank, tag=5)
                tf_results.append(tf)
            else:
                df = comm.recv(source=worker_rank, tag=5)
                df_results.append(df)
                
        final_tf = merge_counts(tf_results)
        final_df = merge_counts(df_results)
        
        print("Term-Frequency (TF) Result:")
        for word in sorted(final_tf.keys()):
            print(f"{word}: {final_tf[word]}")
        
        print("\nDocument-Frequency (DF) Result:")
        for word in sorted(final_df.keys()):
            print(f"{word}: {final_df[word]}")
            
    else:
        # worker preprocesses and exchanges with partner
        data, vocab, stopwords = comm.recv(source=0, tag=1)
        
        # clean the data first
        preprocessed_data = [clean_text(s, stopwords) for s in data]
        
        # pair up and swap data
        if rank % 2 != 0:
            partner = rank + 1
            comm.send(preprocessed_data, dest=partner, tag=2)
            partner_data = comm.recv(source=partner, tag=2)
        else:
            partner = rank - 1
            partner_data = comm.recv(source=partner, tag=2)
            comm.send(preprocessed_data, dest=partner, tag=2)
            
        combined_data = preprocessed_data + partner_data
        
        # odd ranks do TF, even do DF
        if rank % 2 != 0:
            tf = compute_tf(combined_data, vocab, set())
            comm.send(tf, dest=0, tag=5)
        else:
            df = compute_df(combined_data, vocab, set())
            comm.send(df, dest=0, tag=5)

def main():
    # set up command line arguments
    parser = argparse.ArgumentParser(description="MPI NLP System")
    parser.add_argument('--text', required=True, help="Input text file")
    parser.add_argument('--vocab', required=True, help="Vocabulary file")
    parser.add_argument('--stopwords', required=True, help="Stopwords file")
    parser.add_argument('--pattern', required=True, type=int, choices=[1, 2, 3, 4], help="Pattern 1-4")
    
    args = parser.parse_args()
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    
    if rank == 0:
        print(f"Running Pattern {args.pattern} with {size} processes.")
    
    if args.pattern == 1:
        run_pattern_1(comm, args)
    elif args.pattern == 2:
        run_pattern_2(comm, args)
    elif args.pattern == 3:
        run_pattern_3(comm, args)
    elif args.pattern == 4:
        run_pattern_4(comm, args)


if __name__ == "__main__":
    main()
