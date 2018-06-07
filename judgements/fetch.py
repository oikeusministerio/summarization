
from SPARQLWrapper import SPARQLWrapper, JSON

query = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sfcl: <http://data.finlex.fi/schema/sfcl/>

# Query : List judgments
SELECT ?j WHERE
{
?j rdf:type sfcl:Judgment .
} LIMIT 3
'''


sparql = SPARQLWrapper("http://data.finlex.fi/sparql")
sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

fetch_one = '''
  PREFIX sfcl: <http://data.finlex.fi/schema/sfcl/>

  # Query : Get judgment content
  SELECT ?content
  WHERE {
   <URL/fin/txt> sfcl:text ?content.
  }
'''

for result in results["results"]["bindings"]:
    url = result["j"]["value"]
    sparql.setQuery(fetch_one.replace("URL", url))
    content = sparql.query().convert()
    print(content)
    #for result in results["results"]["bindings"]:
    #    print(result)