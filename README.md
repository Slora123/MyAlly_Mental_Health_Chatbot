# MyAlly Student Support Chatbot

This project is an empathy-aware Retrieval-Augmented Generation (RAG) chatbot for students. It uses three dataset sources:

- `dataset reddit/`: Empathy-Mental-Health Reddit empathy annotations
- `empatheticdialogues/`: EmpatheticDialogues conversation data
- `mhqa-main/datasets/`: MHQA mental-health question answering data

## What Changed

The app now treats the datasets differently instead of mixing everything into one loose collection:

- Reddit + EmpatheticDialogues are used as empathy and tone examples.
- MHQA is used as factual mental-health knowledge.
- Low-empathy Reddit rows are filtered out during indexing.
- The app will refuse to run if the vector database has not been built.

## Project Flow

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your Hugging Face token

Create a `.env` file in the project root:

```env
HUGGINGFACE_TOKEN=your_token_here
```

### 3. Build the RAG index

```bash
python build_rag_index.py
```

This creates two Chroma collections:

- `student_support_empathy`
- `student_support_knowledge`

### 4. Run the chatbot

```bash
python app.py
```

## Retrieval Design

### Empathy retrieval

Uses:

- `dataset reddit/emotional-reactions-reddit.csv`
- `dataset reddit/interpretations-reddit.csv`
- `dataset reddit/explorations-reddit.csv`
- `empatheticdialogues/train.csv`
- `empatheticdialogues/valid.csv`
- `empatheticdialogues/test.csv`

Purpose:

- retrieve empathetic response patterns
- help the model mirror supportive tone
- avoid copying low-empathy Reddit replies

### Knowledge retrieval

Uses:

- `mhqa-main/datasets/mhqa.csv`
- `mhqa-main/datasets/mhqa-b.csv`

Purpose:

- retrieve mental-health question-answer knowledge
- ground educational parts of the response
- support factual questions without pretending to diagnose

## Safety Notes

- The chatbot is designed for support, not diagnosis.
- Crisis-style messages trigger a safety-first response path.
- For production use, add locale-specific crisis resources and a stronger moderation layer.

## Files

- `app.py`: Gradio app and response generation
- `build_rag_index.py`: data preparation and Chroma indexing
- `rag_chatbot_colab.ipynb`: old notebook prototype; review it as reference only
- `rag_reference_logs.jsonl`: conversation logs after app usage

## Next Improvements

- add a student-specific intent classifier
- add response evaluation for empathy and safety
- add hybrid retrieval with metadata filters and reranking
- add citations or visible grounding cards in the UI
