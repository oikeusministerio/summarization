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

Install also [Finnish-dep-parser](http://turkunlp.github.io/Finnish-dep-parser/) that will be run on own process.
Let's run it inside Docker so please install Docker first.
Then download image (https://github.com/samisalkosuo/finnish-dep-parser-docker)
by executing:
```
docker pull kazhar/finnish-dep-parser
```

For graph visualisations, please install Graphviz
```bash
sudo apt install python-pydot python-pydot-ng graphviz
```
PDF reading modules requires installing following packages
```bash
sudo apt-get install python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils pstotext tesseract-ocr \
flac ffmpeg lame libmad0 libsox-fmt-mp3 sox libjpeg-dev swig libpulse-dev
```

## Summaries

### Word embeddings

Before training embeddings, some text data is needed. There is a script that fetches finnish juridical judgments.

Fetch judgments and store them locally for learning tasks(embeddings or abstractive).
```
python3 judgments/fetch.py N
```
Where N is number of judgments to fetch (07/2018 there was only about 6200 available).

Any kind of raw text data, that represents the domain, is useful for learning phase. Also different
domains could be mixed.

Train embeddings

```
python3 embeddings/learn_embeddings.py -source_dir judgments/data -destination_dir embeddings/data/
```
where first parameter is the location of texts used for training and second one is the destination of embeddings and dictionary.

Run evaluations
```bash
python3 embeddings/evaluation/evaluate_embeddings.py 
```

### Abstractive summarization
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

## Start server:

Start dependency parser
```bash
docker run -it --rm -p 0.0.0.0:9876:9876 kazhar/finnish-dep-parser
```
If you want to use other address than 0.0.0.0:9876, please modify the new port to config.json.
Then start server.
```
python3 server.py
```

when server running, post a text to summarize: 
```
curl --h-Type: application/json" --request POST --data '{"content":"put text here.", "summary_length":10, "method":"embedding", "return_justification":"False"}' http://localhost:5000/summarize
```

or visit http:localhost:5000 with browser.

To send text file for summarization, use
```
curl -v -F file=@testi.docx 'http://localhost:5000/summarize/file?summary_length=10&method=graph&return_type=json'
```

## Run tests
Start dependency parser before running tests
```bash
docker run -it --rm -p 0.0.0.0:9876:9876 kazhar/finnish-dep-parser
```
```
python -m unittest extractive_summary/summary_methods/test_summary_methods.py
python -m unittest extractive_summary/test_extractives.py
python -m unittest testServer.py
```