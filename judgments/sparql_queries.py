
prefix_sfcl = "http://data.finlex.fi/schema/sfcl/"

get_judgements_query = '''
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX sfcl: <PREFIX_SFCL>

SELECT ?j ?l WHERE
{
?j rdf:type sfcl:Judgment .
?j sfcl:isRealizedBy ?l
} LIMIT N
'''

fetch_one_judgement = '''
  PREFIX sfcl: <PREFIX_SFCL>

  SELECT ?content
  WHERE {
   <URL/LANGUAGE/txt> sfcl:text ?content.
  }
'''

def get_judgements(n):
    """
    :param n number of judgements to return:
    :return: query
    """
    return get_judgements_query.replace("PREFIX_SFCL", prefix_sfcl)\
        .replace("N",str(n))

def get_judgement_content(url, language='fin'):
    """
    :param url: identifier of judgement
    :return: query
    """
    return fetch_one_judgement.replace("PREFIX_SFCL", prefix_sfcl) \
        .replace("URL", url).replace("LANGUAGE", language)
