class MockData(object):
    """
    This is a mock JSON data which complies with the JSON data schema
    defined at https://github.com/funpdbe-consortium/funpdbe_schema
    """

    def __init__(self):
        self.data = self.set_data()

    @staticmethod
    def set_data():
        return {"pdb_id": "2abc",
            "data_resource": "funsites",
            "resource_version": "1.0.0",
            "software_version": "1.0.0",
            "resource_entry_url": "https://example.com/foo/bar",
            "release_date": "01/01/2000",
            "chains": [{"chain_label": "A",
                "chain_annotation": "foo",
                "residues": [{"pdb_res_label": "1",
                    "aa_type": "ALA",
                    "site_data": [{"site_id_ref": 1,
                        "raw_score": 0.7,
                        "confidence_score": 0.9,
                        "confidence_classification": "high"}]}]}],
            "sites": [{"site_id": 1,
                    "label": "ligand_binding_site",
                    "source_database": "pdb",
                    "source_accession": "2abc",
                    "source_release_date": "01/01/2000"}],
            "evidence_code_ontology": [{"eco_term": "computational combinatorial evidence used in automatic assertion",
                "eco_code": "ECO:0000246"}]}