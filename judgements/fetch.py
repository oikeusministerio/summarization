
from SPARQLWrapper import SPARQLWrapper, JSON
from sparql_queries import get_judgements, get_judgement_content

def extract_id(url):
    """
    :param url like http://data.finlex.fi/ecli/kko/1998/138:
    :return: 1998_138
    """
    splitted = url.split('/')
    return splitted[-2] + '_' + splitted[-1]

end_point = "http://data.finlex.fi/sparql"
filepath = "data/"

sparql = SPARQLWrapper(end_point)
query = get_judgements(2)
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    url = result["j"]["value"]
    query = get_judgement_content(url)
    id = extract_id(url)
    sparql.setQuery(query)
    content = sparql.query().convert()
    binding = content["results"]["bindings"][0]
    text = binding["content"]["value"]
    with open(filepath + id + '.txt', 'a') as out:
        out.write(text+ '\n')