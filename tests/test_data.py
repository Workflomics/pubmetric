from WFQC import data
import pytest
import os 

@pytest.mark.asyncio
async def test_get_biotools_metadata(shared_datadir):
    tmp_dir='tmp_out'
    os.system(f'mkdir {tmp_dir}')
    df = await data.get_biotools_metadata(outpath=tmp_dir)
    os.system(f'rm -rf {tmp_dir}') # maybe not the best method?
    assert df.loc[df['name'] == 'PEPMatch', 'pmid'].values[0] == str(38110863)

def test_europepmc(shared_datadir):
    ProteoWizard_pmid = 23051804
    citations = data.europepmc(ProteoWizard_pmid, page_size=1000)
    assert len(citations)> 100



