# summarization
Automated summarization of legal texts

## judgements

```
cd judgements
./run_script.sh
```

## summaries

Start server:
```
cd extractive-summary
./run_script.sh
```

when server running, post a text to summarize: 
```
curl --header "Content-Type: application/json" --request POST --data '{"content":"put text here.", "summary_length":30, "minimum_distance":0.1}' http://localhost:5000/summarize
```

