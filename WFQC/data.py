"""
Functions to download data.
"""

import pandas as pd         
import os
from tqdm import tqdm       
from datetime import datetime, timedelta
import glob
import json

import aiohttp              # Used for aggregating requests into single session
import nest_asyncio         # For jupyter asyncio compatibility 
nest_asyncio.apply()        # Automatically takes into account how jupyter handles running event loops
import jsonpath_ng as jp    # TODO: import jsonpath_ng.ext      # More efficient json processing look into if actually computationally more efficient 

# TODO: import jsonpath_ng.ext      # More efficient json processing look into if actually computationally more efficient 
import requests             # For single API requests 
import pickle


#TODO: all of the descriptions - Where do I put default value? 

async def aggregate_requests(session, url):
    """ 
    Sync the bio.tools (page) requests so they are all made in a single session 

    Parameters
    ----------
    session : aiohttp.client.ClientSession object
        session object for package aiohttp
    url : str
        url for request
    """
    
    async with session.get(url) as response:
        return await response.json()
    
async def get_biotools_metadata(outpath, topicID="topic_0121"):  # TODO: I removed format. Check if there is any reason to have it 
                                                        # TODO: should add parameter for optional forced retrieval - even if csv file, still recreate it 
                                                        # TODO: Currently no timing - add tracker
    """
    Fetches metadata about tools from bio.tools, belonging to a given topicID and returns as a dataframe.
    If a CSV file already exists load the dataframe from it. 

    Parameters
    ----------
    topicID : str TODO: make this a int instead? why am I writing topic? 
        The ID to which the tools belongs to, ex. "Proteomics" or "DNA" as defined by 
        EDAM ontology (visualisation: https://edamontology.github.io/edam-browser/#topic_0003)

    
    """


    # File name checking and creation 
    date_format = "%Y%m%d"
    pattern = f'biotools_metadata_{topicID}*'
    matching_files = glob.glob(pattern)
    
    if matching_files:
        matching_files.sort(key=os.path.getmtime)
        csv_filename = matching_files[-1]
        
        # Check if file older than a week
        file_date = datetime.strptime(csv_filename.split('_')[-1].split('.')[0], date_format)
        if file_date < datetime.now() - timedelta(days=7):
            print("Old datafile. Updating...")
        else:
            print("Bio.tools data loaded from existing CSV file.")
            df = pd.read_csv(csv_filename)
            return df
    else:
        print("No existing bio.tools CSV file. Downloading data.") 
        # Define the CSV filename
        csv_filename = f'biotools_metadata_{topicID}_{datetime.now().strftime(date_format)}.csv' 
    



    
    # TODO: should filepath/name be allowed to be configurable?
    # then the following could be a separate function called by this one, or is this very inefficient?
    # TODO: should place files created in a folder named for each run

    all_tool_data = [] # TODO: predefine the length, means one more request 
    doi_tools = [] # collect tools without pmid

    # start at page 1 
    page = 1 

    # requests are made during single session
    async with aiohttp.ClientSession() as session: 
        while page:
            # if int(page) > 10:
            #     break # for debug 
            # send request for tools on the page, await further requests and return resonse in json format
            biotools_url = f'https://bio.tools/api/t?topicID=%22{topicID}%22&format=json&page={page}'
            biotool_data = await aggregate_requests(session, biotools_url)
            

            # TODO: Do I need to check? what happens if no response for page == 1? Maybe try/except instead
            # Checking if there are any tools, if 

            # To record nr of tools with primary
            no_primary_publications = 0 
            nr_publications = []

            if 'list' in biotool_data: 
                biotools_lst = biotool_data['list']
                
                for tool in biotools_lst: #add tqdm here 
                    name = tool.get('name') 
                    publications = tool.get('publication') # does this cause a problem if there is no publication? 
                    topic = tool.get('topic')
               
                    if isinstance(publications, list): 
                        nr_publications.append(len(publications))
                        try:
                            for publication in publications:
                                if publication.get('type')[0] == 'Primary':
                                    primary_publication = publication
                                    break
                        except:
                            primary_publication = publications[0] # pick first then 
                            no_primary_publications += 1
                    else:
                        nr_publications.append(1)
                        primary_publication = publications
                        

                    if primary_publication.get('pmid'):
                        all_tool_data.append({
                            'name': name,
                            'pmid': str(primary_publication['pmid']),
                            'topic': topic[0]['term']
                        })
                    else:
                        
                        doi_tools.append({
                            'name': name,
                            'doi': primary_publication.get('doi'),
                            'topic': topic[0]['term']
                        })

                page = biotool_data.get('next')
                if page: # else page will be None and loop will stop 
                    page = page.split('=')[-1] # only want the page number 
            else: 
                print(f'Error while fetching tool names from page {page}')
                break
    
    print("Nr of tools without a primary publication tag:", no_primary_publications)
    print("Largest number of publications for a tool: ",max(nr_publications))
    print("Nr of tools with pmid in bio.tools: ",len(all_tool_data))
    print("Nr of tools without pmid (with doi): ", len(doi_tools))

    # Download pmids from dois
    doi_library_filename = 'doi_pmid_library.json' # TODO: Make it customisable 
    try: 
        with open(doi_library_filename, 'r') as f:
            doi_library = json.load(f)
    except FileNotFoundError:
        print(f'Library file not found. Creating new file named {doi_library_filename}.')
        doi_library = {} # {doi: pmid}, should I perhaps do {name: [pmid doi ]} instead?

    library_updates = False
    async with aiohttp.ClientSession() as session: 
        for tool in tqdm(doi_tools, desc="Fetching pmids from dois."):
            doi = tool["doi"]

            # Check if tool is already in library 
            if doi in doi_library: 
                doi_pmid = doi_library[doi] 
                tool["pmid"] = doi_pmid
                continue
            
            # Otherwise access NCBI API
            library_updates = True

            url = f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=PubMed&retmode=json&term={doi}"
            result = await aggregate_requests(session, url)
            try:
                doi_pmid = str(result.get('esearchresult').get('idlist')[0])
                if str(doi_pmid) == 'null': #this does not feel optimal 
                    doi_pmid = None
            except:
                doi_pmid = None # if no pmid was found, will have to remove these nodes later

            
            tool["pmid"] = doi_pmid

            if doi_pmid: # do not want to include Nones, since they might get updated in future
                doi_library[doi] = doi_pmid

    if library_updates:
        print(f"Writing new doi, pmid pairs to file {doi_library_filename}")
        with open(doi_library_filename, 'w') as f: # will this not overwrite what was in there? 
            json.dump(doi_library, f)
    
    """ nr_publications"""
    with open(f'{outpath}/nr_publications.pkl', 'wb') as f:
        pickle.dump(nr_publications, f)

    # Convert list of dictionaries to dataframe
    df_pmid = pd.DataFrame(all_tool_data)
    df_doi = pd.DataFrame(doi_tools)


    #drop column doi, and drop all rows with "pmid == None" and concatenate them. TODO: maybe export to logfile which ones did not have pmid or doi pmid 
    df_doi.drop(columns=["doi"], inplace=True) # do I need to do =, or is doi still there otherwise?
    
    df_doi = df_doi.dropna(subset=["pmid"])
    nr_doi_id_pmids = len(df_doi.dropna(subset=["pmid"]))
    print('Nr of tools whose pmid could be identified using the doi:', nr_doi_id_pmids )

    df = pd.concat([df_pmid, df_doi], axis=0, ignore_index=True)
    # Save dataframe to file
    df.to_csv(csv_filename, index=False)

    # If there were any pages, check how many tools were retrieved and how many tools had pmids
    if biotool_data: 
        nr_tools = int(biotool_data['count']) 
        nr_included_tools = len(all_tool_data) + nr_doi_id_pmids
        print(f'Found {nr_included_tools} out of a total of {nr_tools} tools with PMIDS.')

    return df

def europepmc(article_id, format='JSON', source='MED', page=1, page_size=1000):   # TODO: replace own wrapper with recommendation? https://github.com/ML4LitS/CAPITAL/tree/main
                                                                                # TODO: call output="idlist" immidiately? then we have no metadata but we dont use that anyways!
    """ 
    Downloads pmids for the articles citing the given article_id, returns list of citation pmids (PubMed IDs)
        
    Parameters
    ----------
    article_id : str # TODO: int? 
        pmid, PubMed ID, for a given article.
    source: str
        source ID as given by the EuropePMC API documentation: https://europepmc.org/Help#contentsources 

    page, int, default == 1
        determines where to start looking TODO: remove this, why would you not start at 1? 

    pagesize, int, default 1000 max 1000
        determines number of results per page
    
    """ 

    # create a url with the given requirements according to the EuropePMC API synthax and query the API
    base_url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{article_id}/citations?page={page}&pageSize={page_size}&format={format}'
    result = requests.get(base_url)

    # Return all citations, given the query was accepted
    # TODO: jsonpath-ng
    if result.ok:
        return result.json()['citationList']['citation']
    else:
        print('Something went wrong') # TODO: better error message. Try/except? 








