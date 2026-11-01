# Introduction to RAG

## What is RAG?

Retrieval-Augmented Generation (RAG) is a technique where a language model answers questions using information retrieved from an external collection of documents. Instead of relying only on what the model learned during training, the system first searches the documents for relevant passages and then gives those passages to the model as context.

## Why use RAG?

Language models can hallucinate, which means they produce answers that sound confident but are wrong. They also know nothing about private or recent documents. RAG reduces hallucinations by grounding the answer in real text, and it lets the model answer questions about documents it was never trained on. Because the retrieved passages are known, the system can also show the sources behind each answer.

## How does RAG work?

A RAG pipeline has two phases. In the ingestion phase, documents are split into chunks, each chunk is converted into an embedding, and the embeddings are stored in a vector database. In the query phase, the question is converted into an embedding, the most similar chunks are retrieved, and the language model generates an answer based on those chunks.

## What are embeddings?

An embedding is a list of numbers that represents the meaning of a text. Texts with similar meaning get embeddings that are close to each other. This makes it possible to search by meaning instead of exact keywords. A common way to measure how close two embeddings are is cosine similarity.