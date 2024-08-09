"""
Module to download meta data about software in bio.tools

"""
import os
from tqdm import tqdm       
from datetime import datetime
import json
import numpy as np
from typing import Optional
import aiohttp              
from .exceptions import SchemaValidationError 
from .log import log_with_timestamp
import pickle
import asyncio

async def aggregate_requests(session: aiohttp.ClientSession, url: str, retries: int = 3, backoff: float = 2.0) -> dict:
    """
    Sync requests so they are all made in a single session

    :param session: aiohttp.ClientSession object
        Session object for package aiohttp
    :param url: str
        URL for request

    :return: dict
        JSON response from the request
    """
    attempt = 0
    while attempt < retries:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            attempt += 1
            wait_time = backoff ** attempt
            log_with_timestamp(f"Request failed: {e}. Retrying in {wait_time:.1f} seconds...")
            await asyncio.sleep(wait_time)
    raise Exception(f"Failed to fetch data from {url} after {retries} attempts.")



async def get_pmid_from_doi(doi_tools: dict, outpath: str, doi_library_filename: str = 'doi_pmid_library.json', save_interval: int = 10) -> dict:
    """
    Given a list of dictionaries with data about (tool) publications, 
    this function uses their DOIs to retrieve their PMIDs from NCBI eutils API.

    :param doi_tools: list of dicts
    :param outpath: str
    :param doi_library_filename: str, default 'doi_pmid_library.json'
    :param save_interval: int, default 10, Save progress after this many updates

    :return: Updated list of dicts with PMIDs included.

    """
    if os.path.isfile(doi_library_filename):
        log_with_timestamp("Loading doi-pmid library")
        with open(doi_library_filename, 'r', encoding='utf-8') as f:
            doi_library = json.load(f)
    else:
        log_with_timestamp('Creating a new doi-pmid library')
        doi_library = {}

    library_updates = 0
    async with aiohttp.ClientSession() as session:
        for tool in tqdm(doi_tools, desc="Downloading pmids from dois."):
            doi = tool.get("doi")

            # Check if DOI already exists in the library
            if doi in doi_library:
                tool["pmid"] = doi_library[doi]
                continue

            # Attempt to fetch the PMID using the DOI
            url = f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=PubMed&retmode=json&term={doi}"
            result = await aggregate_requests(session, url)
            id_list = result.get('esearchresult', {}).get('idlist', [])
            doi_pmid = next(iter(id_list), None)

            if doi_pmid:
                tool["pmid"] = doi_pmid
                doi_library[doi] = doi_pmid
                library_updates += 1
            else:
                continue
            
            # Save progress 
            if library_updates >= save_interval:
                with open(os.path.join(outpath, doi_library_filename), 'w', encoding='utf-8') as f:
                    json.dump(doi_library, f)
                library_updates = 0  # Reset update counter

    # Final save if there were any remaining updates
    if library_updates > 0:
        with open(os.path.join(outpath, doi_library_filename), 'w', encoding='utf-8') as f:
            json.dump(doi_library, f)

    updated_doi_tools = [tool for tool in doi_tools if tool.get('pmid')]
    log_with_timestamp(f"Found {len(updated_doi_tools)} tools with PMIDs using their DOIs")

    return updated_doi_tools



async def get_pmids(topic_id: Optional[str], test_size: Optional[int]) -> tuple:
    """ 
    Downloads all (or a specified amount) of the bio.tools tools for a specific topic and returns metadata about the tools.

    :param topic_id: str
        The ID to which the tools downloaded belong, e.g., "Proteomics" or "DNA" as defined by EDAM ontology. 
    :param test_size: int, default None
        Determines the number of tools downloaded

    :return: tuple
        Tuple containing a list of tools (dictionaries) with PMIDs, a list of tools without PMIDs, and the total number of tools.
    """

    pmid_tools = []
    doi_tools = [] # collect tools without pmid

    if topic_id:
        base_url = f'https://bio.tools/api/t?topicID=%22{topic_id}%22&format=json&page='
    else:
        base_url = 'https://bio.tools/api/t?%22&format=json&page=' # Full bio.tools

    page = 1
    log_with_timestamp("Downloading tool metadata from bio.tools")

    # graph stats:
    primary_stat = 0
    no_publication_stat = 0



    async with aiohttp.ClientSession() as session:
        while page:
            # Sends request for tools on the page, await further requests and return resonse in json format
            biotools_url = base_url + str(page)
            biotool_data = await aggregate_requests(session, biotools_url)
            

            # TODO: Do I need to check? what happens if no response for page == 1? Maybe try/except instead
            if 'list' in biotool_data: 
                biotools_list = biotool_data['list']
                
                for tool in biotools_list:
                    publications = tool.get('publication')
                    if not publications: # Tools without linked publications can not be used in the graph
                        no_publication_stat += 1
                        continue

                    name = tool.get('name')
                    topic = tool.get('topic')
                    nr_publications = len(publications)
                    #primary_publication = next((pub for pub in publications if 'Primary' in pub.get('type')), publications[0])
                    primary_publication = next((pub for pub in publications if 'Primary' in pub.get('type')), None)
                    if primary_publication is None:
                        primary_publication = publications[0]
                        primary_stat +=1

                    all_publications = [pub.get('pmid') for pub in publications]

                    if primary_publication.get('metadata'):
                        pub_date = primary_publication['metadata'].get('date')
                        if pub_date:
                            pub_date = int(pub_date.split('-')[0])
                    else: 
                        pub_date = None
                    if primary_publication.get('pmid'):
                        pmid_tools.append({
                            'name': name,
                            'doi': primary_publication.get('doi'), # adding doi here too 
                            'topics': [t.get('term') for t in topic] if topic else None,
                            'nrPublications':  nr_publications,
                            'allPublications': all_publications,
                            'pubDate': pub_date,
                            'pmid': str(primary_publication['pmid'])

                        })
                    else:
                        
                        doi_tools.append({
                            'name': name,
                            'doi': primary_publication.get('doi'),
                            'topics': [t.get('term') for t in topic] if topic else None,
                            'nrPublications':  nr_publications,
                            'allPublications': all_publications,
                            'pubDate': pub_date
                        })

                if test_size and len(pmid_tools) + len(doi_tools) >= test_size: # TODO: this does not guar. that tot nr tools with pmid is at least test_size. only include pmid_tools in calc?
                    break

                page = biotool_data.get('next')
                if page: # else page will be None and loop will stop 
                    page = page.split('=')[-1] # only want the page number 
            else: 
                log_with_timestamp(f'Error while fetching tool names from page {page}')
                break
    print(primary_stat, no_publication_stat)
    # Record the total nr of tools
    total_nr_tools = int(biotool_data['count']) if biotool_data and 'count' in biotool_data else 0

    return pmid_tools, doi_tools, total_nr_tools 


async def get_publication_dates(tool_metadata: list) -> list: #TODO: do I really need to send the entire list of dictionaries here or should I just send a list of pmids, what is computationally better? 
    """
    Downloads the publication date from NCBI using the PMID of the file and updates the metadat file. 

    :param tool_metadata: list
        List of dictionaries containing tool metadata.

    :return: list
        Updated list of tool metadata with publication dates included.
    """

    tools_without_pubdate = 0
    async with aiohttp.ClientSession() as session: 
        for tool in tqdm(tool_metadata, desc= 'Downloading publication dates'):

            if 'pubDate' in tool and tool['pubDate'] and tool['pubDate'] != 'null': # only fetch info for the ones that did not already have it 
                continue

            tools_without_pubdate += 1
            pmid = tool['pmid']
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"

            data = await aggregate_requests(session, url)
            
            if 'result' in data and pmid in data['result']:
                pub_date = data['result'].get(pmid, {}).get('pubdate', None)
                tool['pubDate'] = int(str(pub_date).split()[0]) if pub_date else None
            else:
                tool['pubDate'] = None
    log_with_timestamp(f"Nr of tools in bio.tools without a publication date: {tools_without_pubdate}")
    return tool_metadata # TODO: do I have to return it or can I just update it using the function, i think i can just update it? 


async def get_tool_metadata(outpath: str, topic_id: str , inpath: Optional[str] = None, test_size: Optional[int] = None, random_seed: int = 42) -> dict:
    """
    Fetches metadata about tools from bio.tools, belonging to a given topic_id and returns as a dictionary.

    :param outpath: str
        Path to directory where a newly created file should be placed.
    :param topic_id: str
        The ID to which the tools downloaded belong 
    :param inpath: The path to an already existing file which will be loaded. 
    :param update: bool, default False
        Determines whether or not to force the retrieval of a new data file.
    :param test_size: int, default None
        Determines the size of the test sample - the number of tools included in the final dictionary.

    :return: dict
        Dictionary containing metadata about the tools.
    """
   
    # Specifying the file name
    if test_size:
        metadata_file_name = f'tool_metadata_test{test_size}.json' # I removed date from the filename, it is inside if needed
    else:
        metadata_file_name = 'tool_metadata.json'

    if inpath: # Indicates we want to load a file
        metadata_path = os.path.join(inpath, metadata_file_name)
        if os.path.isfile(metadata_path): 
            with open(metadata_path, "r") as f:
                metadata_file = json.load(f)
        else:
            raise FileNotFoundError(" ")
        # TODO should have somoe criteria for what is loaded here. Needs to follow the metadatafile schema # TODO specify schema
        if not isinstance(metadata_file['tools'], list) or not isinstance(metadata_file['tools'][0], dict):
            raise SchemaValidationError("Metadata file does not have the required structure. Please refer to metadata file schema.")

        if test_size: # Takes a random selection of the specified size from the file
            np.random.seed(random_seed)
            test_tools = list(np.random.choice(metadata_file['tools'], size = test_size)) 
            metadata_file['tools'] = test_tools
        
        return metadata_file

    # If no inpath is specified we recreate the metadatafile
    # Creating json file 
    metadata_file = {
        "creationDate": str(datetime.now()),
        "topic": topic_id #or "full_biotools" # If topic ID is None 
    }

    try:
        with open("pmid_tools.pkl", 'rb') as f:
            pmid_tools = pickle.load( f)
        with open("doi_tools1.pkl", 'rb') as f:
            doi_tools = pickle.load( f)
        with open("tot_nr_tools.pkl", 'rb') as f:
            tot_nr_tools = pickle.load( f)

    except (FileNotFoundError, EOFError):
        # Download bio.tools metadata
        pmid_tools, doi_tools, tot_nr_tools = await get_pmids(topic_id=topic_id, test_size=test_size)
        ### tmeporary save
        with open("pmid_tools.pkl", 'wb') as f:
            pickle.dump(pmid_tools, f)
        with open("doi_tools1.pkl", 'wb') as f:
            pickle.dump(doi_tools, f)
        with open("tot_nr_tools.pkl", 'wb') as f:
            pickle.dump(tot_nr_tools, f)
    

    metadata_file['totalNrTools'] = tot_nr_tools  
    metadata_file['biotoolsWOpmid'] = len(doi_tools)

    # Update list of doi_tools to include pmid TODO server disconnection
    try:
        with open("doi_tools2.pkl", 'rb') as f:
            doi_tools = pickle.load(f)
    except (FileNotFoundError, EOFError):
        doi_tools = await get_pmid_from_doi(outpath=outpath, doi_tools=doi_tools)
        with open("doi_tools2.pkl", 'wb') as f:
            pickle.dump(doi_tools, f)

    metadata_file["nrpmidfromdoi"] = len(doi_tools)

    all_tools = pmid_tools + doi_tools

    #TODO: ensure only unique tools, for some reason I am seeing repetition later - in included tools

    all_tools_with_age = await get_publication_dates(all_tools)

    metadata_file["tools"] = all_tools_with_age
    
    log_with_timestamp(f'Found {len(all_tools_with_age)} out of a total of {tot_nr_tools} tools with PMIDS.')

    return metadata_file


async def europepmc_request(session: aiohttp.ClientSession, article_id: str, page: int = 1, source: str = 'MED') -> list: 
    """ 
    Downloads PMIDs for the articles citing the given article_id, returns a list of citation PMIDs (PubMed IDs).
        
    :param session: aiohttp.ClientSession
        Session object for making asynchronous HTTP requests.
    :param article_id: str  
        PubMed ID for a given article. Can be given as int, but PubMed IDs sometimes contain letters. 
    :param page: int, default 1
        Page number for query.
    :param source: str
        Source ID as given by the EuropePMC API documentation (https://europepmc.org/Help#contentsources).
    :param random_seed: int, Specifies the seed used to randomly pick tools in a test run. Default is 42.

    :return: list
        List of citation PMIDs.
    """ 

    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{article_id}/citations?page={page}&pageSize=1000&format=json'
    async with session.get(url) as response:
        if response.ok:
            result = await response.json()
            citations = result['citationList']['citation']
            citation_ids = [citation['id'] for citation in citations]
            if result['hitCount'] <= 1000 * page:
                return citation_ids
            else:
                next_page_citations = await europepmc_request(session, article_id, page + 1, source)
                return citation_ids + next_page_citations
        else:
            log_with_timestamp(f'Something went wrong with request {url}')
            return None
