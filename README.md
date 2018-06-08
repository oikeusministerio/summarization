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
curl --header "Content-Type: application/json" --request POST --data '{"content":"text here"}' http://localhost:5000/summarize
```
