import aiohttp
import asyncio
import igraph
import requests # maybe use aio for europepmc too? but not multiple pages so maybe not neccessary? 
import py4cytoscape as p4c
import pandas as pd
import os
from tqdm import tqdm
import pickle
import numpy as np


"""
Functions for fetching data with bio.tools API and europepmc API, and creating a citation network

Alma Nilsson, April 2024 

"""


async def fetch_biotools_page(session, url):
    """ Sync the bio.tools (page) requests so they are all made in a single session """
    async with session.get(url) as response:
        return await response.json()

async def get_biotools_metadata(topicID="topic_0121", format="json"): # probably rm format option as I am processing the data anyways 
    """
    Fetch metadata for biotools with the given topicID and return as a dataframe.
    If a CSV file already exists, load the dataframe from it.
    
    Input topic, output dataframe of metadata of all tools in bio.tools with that topic 

    OBS: should add parameter for optional forced retrieval - even if csv file, still recreate it 
         should make the csv filename contain a time 
    """

    csv_filename = f'biotools_metadata_{topicID}.csv' # should add the date here and then check if date is > a week old

    # Check if CSV file exists
    if os.path.isfile(csv_filename):
        df = pd.read_csv(csv_filename)
        print("Bio.tools data loaded from existing CSV file.")
        return df

    all_tool_data = [] # should predefine the length of this, since we can check how many tools there are in total
    # but then I need to send one request before the loop to define nr_tools. perhaps good idea as a check anyways. 

    page = 1 # start at page 1, could make part of input param so user can specify, but dont know if neccessary 

    async with aiohttp.ClientSession() as session: # while loop requests made during single session

        while page: # as long as there is a next page

            # send request for tools on the page 
            biotools_url = f'https://bio.tools/api/t?topicID=%22{topicID}%22&format={format}&page={page}'
            biotool_data = await fetch_biotools_page(session, biotools_url)
            

            if 'list' in biotool_data: # if there are any tools on the page, might be unnecessary to check for every page since it is only relevant for page 1 
                biotools_lst = biotool_data['list']
                for tool in biotools_lst:
                    name = tool.get('name') # I am giving them the option of choosing format, but here using .get which only works with json. Probably will rm option as it is not very relevant
                    publication = tool.get('publication')
                    topic = tool.get('topic')

                    # dont know if I need to check for all three (especially as it is sorted on topic), but otherwise I need to handle the possibility that one is not present 
                    # also want to chekc if doi than what pmid for the ones that dont have it
                    if name and publication and publication[0].get('pmid') and topic and topic[0].get('term'): 
                        all_tool_data.append({ #predefine, since max length == nr_tools, then need to define this earlier
                            'name': name,
                            'pmid': str(publication[0]['pmid']), # making sure they are all strings
                            'topic': topic[0]['term']
                        })

                page = biotool_data.get('next')
                if page: # else page will be None and loop will stop 
                    page = page.split('=')[-1] # only want the page number 
            else: 
                print(f'Error while fetching tool names from page {page}')
                break

    # Convert list of dictionaries to dataframe
    df = pd.DataFrame(all_tool_data)
    # Save dataframe to file
    df.to_csv(csv_filename, index=False)

    
    if biotool_data: # if there were any pages, check how many tools were retrieved and how many tools had pmids
        nr_tools = int(biotool_data['count']) # if no pages then this will not work, is that a problem? 
        print(f'Found {len(all_tool_data)} out of a total of {nr_tools} tools with PMIDS.')

    return df

def europepmc(article_id, format='JSON', source='MED', page=1, page_size=25): 
    """ 
    Download pmids for the articles citing article_id, return list of citation pmids

    OBS: to make more efficient we can just call output="idlist" immidiately? then we have no metadata but we dont use that anyways!
    
    """ 
    base_url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{article_id}/citations?page={page}&pageSize={page_size}&format={format}'
    result = requests.get(base_url)

    if result.ok:
        return result.json()['citationList']['citation']
    else:
        print('Something went wrong')



def create_citation_network(topicID="topic_0121", testSize=None, randomSeed=42, loadData=True, saveFiles=True): # maybe topic should be just the number for easier use 
    
    """
    Creates a citation network given a topic,

    topicID: bio.tools topic for tools to be used in the network. Default 0121, proteomics. 
    testSize: int or None, default is None. If it is an int, the function will create a smaller testnetwork containing the specified nr of  
    radnomSeed: int, default 42. defines the random seed for the testrun so it can be reproducable
    loadData: boolean, default True. if True it checks if there are saved files to be used (maybe shoudl add that you can specify filenames/paths). 
                 If false it runs edge creation
    saveFiles: Boolean, default True. determines if edges, graph and pmids used are saved. uses pickle.
    """

    # Retrieve the data 
    # run the asynchronous function for single session requests 
    result = asyncio.run(get_biotools_metadata(topicID=topicID)) #is it ok that it uses the same variable?
    pmids = result['pmid'].tolist() # should I use numpy for all my lists? 


    if testSize: # this must be dote after choice of load data- otherwise it will load a previous big one possibly. Perhaps "you picked load data, size unknown, proceed?".  
        print(f"Creating test-network of size {testSize}. Random seed is {randomSeed}.")
        np.random.seed(randomSeed)
        pmids = np.random.choice(pmids,testSize)

    
    # Edge creation 
    if loadData: # Load previously created data or recreate it
        if os.path.isfile('edges.pkl') and os.path.isfile('graph.pkl') and os.path.isfile('included_tools.pkl'): # should give option to specify these names
            print("Loading data")
            with open('edges.pkl', 'rb') as f:
                edges = pickle.load(f)
            with open('graph.pkl', 'rb') as f:
                G = pickle.load(f) 
            with open('included_tools.pkl', 'rb') as f:
                included_tools = pickle.load(f) 
        else:
            print(f"Files not found. Please check that 'edges.pkl', 'graph.pkl' and 'included_tools.pkl' are in your current directory and run again. Or set loadData = False, to create the files. ")
            return 
   
    else:
        # edge creation using europepmc
        print("Downloading citation data from Europepmc.")
        edges = []
        included_tools = [] # this is to create a list of the tools that actually had citations, otherwise they are not included in the graph. 
        for pmid in tqdm(pmids, desc="Processing PMIDs"): # tqdm for progress
            pmid = str(pmid) # moved from doing this in te beginning on full list because more efficient, but maybe this just makes it less understandable 

            citations = europepmc(pmid, page_size=1000)
            for citation in citations:
                edges.append((pmid, str(citation['id']))) # make sure evrything is strings
                if pmid not in included_tools:
                    included_tools.append(pmid) # this is so inefficient goddamn, please update
        
        print("Creating citation graph using igraph.")
        G = igraph.Graph.TupleList(edges, directed=True)

        if saveFiles:
            print("Saving data to 'edges.pkl', 'graph.pkl' and 'included_tools.pkl'.") # sould make these filenames dynamic
            # and save them 
            #Do this nicer later? 
            with open('edges.pkl', 'wb') as f:
                pickle.dump(edges, f)

            with open('graph.pkl', 'wb') as f:
                pickle.dump(G, f)

            with open('included_tools.pkl', 'wb') as f:
                pickle.dump(included_tools, f)    
        
    return edges, G, included_tools # returns edges, graph and pmids used in graph (teh ones that had citations)




#####################################################
"""Cytoscape things """

edges, G, included_tools = create_citation_network(testSize=100, loadData=False)



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