import aiohttp
import asyncio
import igraph
import requests # maybe switch to aio for europepmc too? but not multiple pages so maybe not neccessary? 
import json
import py4cytoscape as p4c
import pandas as pd
import os
from tqdm import tqdm
import pickle

"""
Functions for fetching data with bio.tools API and europepmc API

Alma Nilsson, April 2024 

"""


async def fetch_biotools_page(session, url):
    async with session.get(url) as response:
        return await response.json()

async def get_biotools_metadata(topicID="topic_0121", format="json"):
    """
    Fetch metadata for biotools with the given topicID and return as a dataframe.
    If a CSV file already exists, load the dataframe from it.
    """
    csv_filename = f'biotools_metadata_{topicID}.csv'

    # Check if CSV file exists
    if os.path.isfile(csv_filename):
        df = pd.read_csv(csv_filename)
        print("Bio.tools data loaded from existing CSV file.")
        return df

    all_tool_data = []

    page = 1
    async with aiohttp.ClientSession() as session:
        while page:
            #print(page)
            biotools_url = f'https://bio.tools/api/t?topicID=%22{topicID}%22&format={format}&page={page}'
            biotool_data = await fetch_biotools_page(session, biotools_url)
            

            if 'list' in biotool_data:
                biotools_lst = biotool_data['list']
                for tool in biotools_lst:
                    name = tool.get('name')
                    publication = tool.get('publication')
                    topic = tool.get('topic')
                    if name and publication and publication[0].get('pmid') and topic and topic[0].get('term'): # also want to chekc if doi than what pmid for the ones that dont have it
                        all_tool_data.append({ # can maybe make this more efficient by predefining a list, since I know it is max length nr_tools
                            'name': name,
                            'pmid': publication[0]['pmid'],
                            'topic': topic[0]['term']
                        })

                page = biotool_data.get('next')
                if page:
                    page = page.split('=')[-1]
            else:
                print(f'Error while fetching tool names from page {page}')
                break

    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(all_tool_data)
    # Save DataFrame to file
    df.to_csv(csv_filename, index=False)

    # I have not tried this yet
    if biotool_data:
        nr_tools = int(biotool_data['count']) # if no pages then this will not work, is that a problem? 
        print(f'Found {len(all_tool_data)} out of a total of {nr_tools} tools with PMIDS.')

    return df

def europepmc(article_id, format='JSON', source='MED', page=1, page_size=25): # to make more efficient we can just call output="idlist" immidiately? then we have no metadata but we dont use that anyways  
    base_url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{article_id}/citations?page={page}&pageSize={page_size}&format={format}'
    result = requests.get(base_url)

    if result.ok:
        return result.json()['citationList']['citation']
    else:
        print('Something went wrong')





# run the asynchronous function
result = asyncio.run(get_biotools_metadata())
pmids = result['pmid'].tolist()
pmids = [str(i) for i in pmids] # inefficient change !! do it when retrieving

pmids = pmids[:100] # for testng smaller networks 

# edge creation slow, so I load them 
if os.path.isfile('edges.pkl') and os.path.isfile('graph.pkl') and os.path.isfile('included_tools.pkl'):
    with open('edges.pkl', 'rb') as f:
        edges = pickle.load(f)
    with open('graph.pkl', 'rb') as f:
        G = pickle.load(f) 
    with open('included_tools.pkl', 'rb') as f:
        included_tools = pickle.load(f) 
else:
    # edge creation using europepmc
    edges = []
    included_tools = [] # this is to create a list of the tools which actually had any citations, otherwise they are not included. 
    for pmid in tqdm(pmids, desc="Processing PMIDs"): # tqdm for progress
         

        citations = europepmc(pmid, page_size=1000)
        for citation in citations:
            edges.append((pmid, str(citation['id']))) # make sure evrything is strings
            if pmid not in included_tools:
                included_tools.append(str(pmid)) # this is so inefficient goddamn, please update

        

    # Create directed graph from edges
    G = igraph.Graph.TupleList(edges, directed=True)

    

    # and save them 
    #Do this nicer later? 
    with open('edges.pkl', 'wb') as f:
        pickle.dump(edges, f)

    with open('graph.pkl', 'wb') as f:
        pickle.dump(G, f)

    with open('included_tools.pkl', 'wb') as f:
        pickle.dump(included_tools, f)






# shortest_paths_result = G.get_shortest_paths("33538780", "21067998", mode="all")
p4c.create_network_from_igraph(G, "stylish_Proteomics_citation_graph")

# print( included_tools)


p4c.set_node_shape_default("ELLIPSE")
p4c.set_node_width_default(30)
p4c.set_node_height_default(30)
p4c.set_node_border_color_default("#000000")  # Black color in hexadecimal
p4c.set_node_border_width_default(1)
p4c.set_node_color_bypass(included_tools, "#FF0000")  # Red color in hexadecimal
p4c.set_node_size_bypass(included_tools, 100)  