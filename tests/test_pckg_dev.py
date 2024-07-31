from wfqc import pckg_dev 

def get_pmids_from_file(shared_datadir):
    filename = os.path.join(shared_datadir, "doi_pmid_library.json")
    doi_list = [{"name": "mzRecal", "doi": "10.1093/bioinformatics/btab056"}, {"name": "DIAgui", "doi": "10.1093/bioadv/vbae001"}]
    pmid_list = asyncio.run(data.get_pmid_from_doi(doi_list, filename))
    assert str(pmid_list[0]["pmid"]) == '33538780'
    assert str(pmid_list[1]["pmid"]) == '38249340'