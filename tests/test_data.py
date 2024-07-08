import os
import pytest
import asyncio
import aiohttp
from wfqc import data

def test_get_tool_metadata_from_file(shared_datadir):
    filename = os.path.join(shared_datadir, "tool_metadata_test20_topic_0121_20250705.json")
    metadata_file = data.get_tool_metadata(outpath='', filename=filename) # this is no longer used anyways. Need to rm 
    pepmatch_pmid = next((tool['pmid'] for tool in metadata_file["tools"] if tool['name'] == 'PEPMatch'), None)
    assert pepmatch_pmid == str(38110863)


@pytest.mark.asyncio
async def test_europepmc_request(shared_datadir):
    protein_prophet_pmid = 14632076 #ProteinProphet has 2949 citations on Jul 12th 2024
    async with aiohttp.ClientSession() as session:
            citations = await data.europepmc_request(session, protein_prophet_pmid)
            print(citations)
    assert len(citations)> 1000


def get_pmids_from_file(shared_datadir):
    filename = os.path.join(shared_datadir, "doi_pmid_library.json")
    doi_list = [{"name": "mzRecal", "doi": "10.1093/bioinformatics/btab056"}, {"name": "DIAgui", "doi": "10.1093/bioadv/vbae001"}]
    pmid_list = asyncio.run(data.get_pmid_from_doi(doi_list, filename))
    assert str(pmid_list[0]["pmid"]) == '33538780'
    assert str(pmid_list[1]["pmid"]) == '38249340'

def test_get_pmid_from_doi(shared_datadir):
    filename = os.path.join(shared_datadir, "doi_pmid_library_empty.json") # need to make sure file is empty again
    doi_list = [{"name": "mzRecal", "doi": "10.1093/bioinformatics/btab056"}, {"name": "DIAgui", "doi": "10.1093/bioadv/vbae001"}]
    pmid_list = asyncio.run(data.get_pmid_from_doi(doi_list, filename)) 
    print(pmid_list)
    assert str(pmid_list[0]["pmid"]) == '33538780'
    assert str(pmid_list[1]["pmid"]) == '38249340'

def test_get_pmid_from_doi_library(shared_datadir):
    filename = os.path.join(shared_datadir, "doi_pmid_library.json")
    doi_list = [{"name": "mzRecal", "doi": "10.1093/bioinformatics/btab056"}]
    pmid_list = asyncio.run(data.get_pmid_from_doi(doi_list, doi_library_filename = filename))
    print(pmid_list)
    assert str(pmid_list[0]["pmid"]) == '33538780'

def test_get_tool_metadata_generate():
    print('') # need to merge with metrics to have the testsize so I can test

