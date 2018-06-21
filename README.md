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
python3 -m unittest extractive_summary/summary/Test*
```

## embeddings

Add correct Redis address and port to extractive_summary/config.json.

Train embeddings

```
python3 embeddings/learn_embeddings.py "../judgements/data" "data/"
python3 embeddings/calcul_distances.py
```
where first parameter is the location of texts used for training and second one is the destination of embeddings and dictionary.
