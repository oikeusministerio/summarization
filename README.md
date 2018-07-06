# summarization
Automated summarization of legal texts

## judgements

```
cd judgements
./run_script.sh
```

## summaries

#### Start server:
```
cd extractive_summary
./run_script.sh
```

when server running, post a text to summarize: 
```
curl --header "Content-Type: application/json" --request POST --data '{"content":"put text here.", "summary_length":30, "minimum_distance":0.1, "method":"embedding"}' http://localhost:5000/summarize
```

or visit http:localhost:5000 with browser.

To send text file for summarization, use
```
curl -v -F file=@testi.docx http://localhost:5000/summarize/file
```

#### Run tests
```
python -m unittest extractive_summary/summary/Test*
python -m unittest extractive_summary/TestDocumentParser.py
python -m unittest extractive_summary/TestSummarizer.py
python -m unittest testServer.py
```

## embeddings

Train embeddings

```
python3 embeddings/learn_embeddings.py -source_dir judgments/data -destination_dir embeddings/data/
```
where first parameter is the location of texts used for training and second one is the destination of embeddings and dictionary.

Run evaluations
```bash
python3 embeddings/evaluation/evaluate_embeddings.py 
```