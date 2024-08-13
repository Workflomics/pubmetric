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
import pubmetric.log 
import pickle
import asyncio
from collections import defaultdict, Counter
import requests
from tqdm.asyncio import tqdm_asyncio

def download_domain_annotations(annotations: str = "full") -> set:
    """
    Downloads a JSON file containing domain annotations from workflomics repository.

    This function retrieves the JSON file from the provided URL, parses the JSON content,
    and extracts the 'label' (name) for each tool.

    :return: A set of tool names bio.tools domain annotaion JSON file.
             Returns None if the file could not be retrieved.
    """
    if annotations == "full":
        url = "https://raw.githubusercontent.com/Workflomics/domain-annotations/main/genomics/your_file_name.json"
    elif annotations == "workflomics":
        url = "path/to/workflomicstools"
    else:
        raise TypeError("Invalid type for tool_selection string, expected 'full' or 'workflomics'.")    

    response = requests.get(url)

    if response.status_code == 200:
        biotools = response.json()
        return {tool['label'] for tool in biotools["functions"]}
    else:
        print(f"Failed to retrieve file: {response.status_code}")


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
        except aiohttp.ClientError: # as e:
            attempt += 1
            wait_time = backoff ** attempt
            #might be good to print, but it does so so many times 
            #pubmetric.log.log_with_timestamp(f"Request failed: {e}. Retrying in {wait_time:.1f} seconds...")
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
        pubmetric.log.log_with_timestamp("Loading doi-pmid library")
        with open(doi_library_filename, 'r', encoding='utf-8') as f:
            doi_library = json.load(f)
    else:
        pubmetric.log.log_with_timestamp('Creating a new doi-pmid library')
        doi_library = {}

    library_updates = 0
    async with aiohttp.ClientSession() as session:
        for tool in tqdm(doi_tools, desc="Downloading pmids from dois."):
            doi = tool.get("doi")

            if doi in doi_library:
                tool["pmid"] = doi_library[doi]
                continue

            url = f"http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=PubMed&retmode=json&term={doi}"
            result = await aggregate_requests(session, url)
            id_list = result.get('esearchresult', {}).get('idlist', [])
            doi_pmid = next(iter(id_list), None)

            if doi_pmid and doi_pmid != '39073865': # what is this cursed paper? 
                tool["pmid"] = doi_pmid
                doi_library[doi] = doi_pmid
                library_updates += 1
            else:
                continue
            
            if library_updates >= save_interval:
                with open(os.path.join(outpath, doi_library_filename), 'w', encoding='utf-8') as f:
                    json.dump(doi_library, f)
                library_updates = 0  # Reset update counter

    if library_updates > 0:
        with open(os.path.join(outpath, doi_library_filename), 'w', encoding='utf-8') as f:
            json.dump(doi_library, f)

    updated_doi_tools = [tool for tool in doi_tools if tool.get('pmid')]
    pubmetric.log.log_with_timestamp(f"Found {len(updated_doi_tools)} tools with PMIDs using their DOIs")

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
                pubmetric.log.log_with_timestamp(f'Error while fetching tool names from page {page}')
                break
    pubmetric.log.log_with_timestamp(f"Primary publications count: {primary_stat}, missing publication count: {no_publication_stat}")
    total_nr_tools = int(biotool_data['count']) if biotool_data and 'count' in biotool_data else 0

    return pmid_tools, doi_tools, total_nr_tools 


async def fetch_publication_dates(session, pmids): #  TODO: Check if the
    """Fetches publication dates for a list of PMIDs from NCBI."""
    pmid_str = ','.join(pmids)
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid_str}&retmode=json"
    async with session.get(url) as response:
        return await response.json()
    
async def process_publication_dates(tool_metadata: list) -> list: #TODO: do I really need to send the entire list of dictionaries here or should I just send a list of pmids, what is computationally better? 
    """
    Downloads the publication date from NCBI using the PMID of the file and updates the metadat file. 

    :param tool_metadata: list
        List of dictionaries containing tool metadata.

    :return: list
        Updated list of tool metadata with publication dates included.
    """

    pmid_to_tool = {tool['pmid']: tool for tool in tool_metadata if 'pubDate' not in tool or not tool['pubDate'] or tool['pubDate'] == 'null'}
    pmids = list(pmid_to_tool.keys())

    # If no pmids need updates return the original list
    if not pmids:
        return tool_metadata

    async with aiohttp.ClientSession() as session:
        data = await fetch_publication_dates(session, pmids)

    results = data.get('result', {})
    tools_without_pubdate = 0

    for pmid in pmids:
        tool = pmid_to_tool.get(pmid)
        pub_date = results.get(pmid, {}).get('pubdate', None)
        if pub_date:
            tool['pubDate'] = int(str(pub_date).split()[0])
        else:
            tools_without_pubdate += 1

    pubmetric.log.log_with_timestamp(f"Nr of tools for which publication date could not be found: {tools_without_pubdate}")
    return tool_metadata

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
            raise FileNotFoundError(f"Can not find {os.path.join(inpath, metadata_file_name)} ")
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

    get_pmids_time = datetime.now()


    
    pmid_tools, doi_tools, tot_nr_tools = await get_pmids(topic_id=topic_id, test_size=test_size)

    pubmetric.log.step_timer(get_pmids_time, "Downloading pmids")

    metadata_file['totalNrTools'] = tot_nr_tools  
    metadata_file['biotoolsWOpmid'] = len(doi_tools)

    # Update list of doi_tools to include pmid TODO server disconnection
    get_pmid_from_doi_time = datetime.now()
    
    doi_tools = await get_pmid_from_doi(outpath=outpath, doi_tools=doi_tools)


    pubmetric.log.step_timer(get_pmid_from_doi_time, "Downloading pmids from doi's")
    metadata_file["nrpmidfromdoi"] = len(doi_tools)

    all_tools = pmid_tools + doi_tools

    #TODO: ensure only unique tools, for some reason I am seeing repetition later - in included tools
    publication_dates_time = datetime.now()
    all_tools_with_age = await process_publication_dates(all_tools)
    pubmetric.log.step_timer(publication_dates_time, "Downloading publication dates")

    metadata_file["tools"] = all_tools_with_age
    
    pubmetric.log.log_with_timestamp(f'Found {len(all_tools_with_age)} out of a total of {tot_nr_tools} tools with PMIDS.')

    return metadata_file

async def fetch_citations(article_id: str, session: aiohttp.ClientSession, source: str = 'MED', batch_size: int = 1000, page: int = 1) -> list:
    """
    Recursively fetches all citation PMIDs for a given article ID, handling pagination.
    
    :param article_id: PubMed ID for the article.
    :param session: An aiohttp.ClientSession object used for making HTTP requests.
    :param source: The source from which citations are fetched. Default is 'MED'.
    :param batch_size: Number of citations to fetch per request. Default is 1000.
    :param page: The page number for pagination. Defaults to 1.
    
    :return: A list of citation PMIDs.
    """
    url = f'https://www.ebi.ac.uk/europepmc/webservices/rest/{source}/{article_id}/citations?page={page}&pageSize={batch_size}&format=json'
    async with session.get(url) as response:
        if response.ok:
            result = await response.json()
            citations = result.get('citationList', {}).get('citation', [])
            citation_ids = [citation['id'] for citation in citations]
            total_hits = result.get('hitCount', 0)
            
            if len(citation_ids) < min(batch_size, total_hits):
                next_page_citations = await fetch_citations(article_id, session, source, batch_size, page + 1)
                return citation_ids + next_page_citations
            else:
                return citation_ids
        else:
            pubmetric.log.log_with_timestamp(f'Something went wrong with request {url}')
            return []

async def fetch_citations_batch(article_ids, session: aiohttp.ClientSession, source: str = 'MED', batch_size: int = 1000) -> dict:
    """
    Asynchronously fetches all citation PMIDs for a batch of article PMIDs from EuropePMC, handling pagination recursively.

    :param article_ids: List of article IDs for which citations are to be fetched.
    :param session: An aiohttp.ClientSession object used for making HTTP requests.
    :param source: The source from which citations are fetched. Default is 'MED'.
    :param batch_size: Number of citations to fetch per request. Default is 1000.
    
    :raises ValueError: If the HTTP request fails or the response status is not OK.

    :return: A dictionary where each key is an article ID and the value is a list of citation IDs for that article. If an error occurs, the value is an empty list.
    """

    results = {}
    for article_id in tqdm_asyncio(article_ids, desc="Fetching Citations", unit="article"):
        try:
            citations = await fetch_citations(article_id, session, source, batch_size)
            results[article_id] = citations
        except Exception as e:
            pubmetric.log.log_with_timestamp(f"Failed to fetch citations for {article_id}: {str(e)}")
            results[article_id] = []  # TODO do I want to continue processing other articles even if one fails?

    return results





async def process_citation_data(metadata_file: list, threshold: int = 20,batch_size: int = 1000) -> dict:
    """
    Processes citation data by fetching citations for tools listed in the metadata file and filtering them
    based on a citation threshold.

    :param metadata_file: A list containing metadata for tools, including their PMIDs.
    :param threshold: The maximum number of citations allowed for it to concievibly represent a workflow. Default is 20.
    :param batch_size: Number of tools to process per batch when fetching citations. Default is 1000.
    
    :raises FileNotFoundError: If the 'paper_citations.json' file is missing and no data is available.
    
    :return: A dictionary where each key is a citation PMID and the value is a set of PMIDs of papers that cite it. Citations with counts exceeding the threshold or referencing only one paper are removed.
    """
    citation_counts = Counter()
    paper_citations = defaultdict(set)

    if os.path.exists('paper_citations.json'):
        with open('paper_citations.json', 'r') as f:
            saved_data = json.load(f)
    else:
        saved_data = {}

    pending_tools = [tool['pmid'] for tool in metadata_file['tools'] if tool['pmid'] not in saved_data]

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
        while pending_tools:
            current_batch = pending_tools[:batch_size]
            pending_tools = pending_tools[batch_size:]

            batch_results = await fetch_citations_batch(current_batch, session)
            
            # Saving data incrementally
            saved_data.update(batch_results)
            with open('paper_citations.json', 'w') as f:
                json.dump(saved_data, f)

            await asyncio.sleep(60)
    
    for tool in tqdm(metadata_file['tools'], desc="Processing citations", unit="tool"):
        paper_pmid = tool['pmid']
        citations = saved_data.get(paper_pmid, [])
        if citations:
            tool['nrCitations'] = len(citations)
            for citation_pmid in citations:
                if citation_pmid == paper_pmid:
                    continue
                paper_citations[citation_pmid].add(paper_pmid)
                citation_counts[citation_pmid] += 1

    paper_citations = {citation: papers for citation, papers in paper_citations.items()
                       if 1 < citation_counts[citation] <= threshold}
    
    removed_citations = len(citation_counts) - len(paper_citations)
    pubmetric.log.log_with_timestamp(
        f"Number of citations removed due to exceeding threshold {threshold} or referencing only one paper: {removed_citations}")
    
    return paper_citations