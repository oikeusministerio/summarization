# summarization
Automated summarization of legal texts

## Installation
Most of the requirements are listed in requirements.txt and can be installed by
```
python3 -m pip install --user -r requirements.txt
```
or with Anaconda (not tested).
Also following binary-packages should be installed :
```
sudo apt-get install wkhtmltopdf
```

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

## Abstractive summarization
This one is not deployed to server, still just a experiment.

The next script takes texts (here it is supposed they are like the judgments), parses the last section
of each text to be used as target (summary). Those texts are then used to train Encoder/decoder-summarizer.
```
python3 abstractive_summary/abstractive_summarization_learning.py -source_dir 'judgments/data/' \
-embeddings_dir 'embeddings/data/' -texts_length 300 -target_length 40
```
-1 in text_length and target_length means, that let's use all words in texts and their targets. 
In case of legal juggment dataset, the longest texts are 80 000 words long and they do not fit to 6GB GPU, so we have to work with shorter or truncated texts.

The number of epocs is by default 10, can be set with flag -epochs 100.

Once model is trained, summarize: 
```
python3 abstractive_summary/summarize.py -source_dir judgments/test_data/ -embeddings_dir embeddings/data/ -index 1 -summary_length 10

```