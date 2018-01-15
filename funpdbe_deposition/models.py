from django.db import models
from django.contrib.auth.models import User

RESOURCES = (
    ("funsites", "funsites"),
    ("nod", "nod")
)

LABELS = (
    ("ligand_binding_site", "ligand binding site"),
    ("active_site", "active site")
)
SOURCE_DATABASE = (
    ("pdb", "pdb"),
    ("uniprot" ,"uniprot")
)
CLASSIFICATION = (
    ("reliable", "reliable"),
    ("low_confidence" ,"low confidence")
)

# TO DO: Creating ECO term tuple
# WHATEVER

class Entry(models.Model):
    """
    Entry class for FunSites
    """

    owner = models.ForeignKey('auth.User', related_name='entries', on_delete=models.CASCADE)

    pdb_id = models.CharField("PDB identifier",
                              max_length=4)

    data_resource = models.CharField("Resource name",
                                     choices=RESOURCES,
                                     max_length=255)

    resource_version = models.CharField("Version of the resource",
                                        max_length=25,
                                        null=True)

    software_version = models.CharField("Version of the software",
                                        max_length=25,
                                        null=True)

    resource_entry_url = models.URLField("URL of the data at the original resource",
                                         null=True)

    release_date = models.CharField("Release date of the data",
                                    max_length=10,
                                    null=True)


class Chain(models.Model):
    """
    Protein chain level data
    """
    entry_ref = models.ForeignKey(Entry,
                                  verbose_name="FunSitesEntry related to this chain",
                                  related_name="chains",
                                  on_delete=models.CASCADE)

    chain_label = models.CharField("Chain identifier label",
                                   max_length=20)

    chain_annotation = models.CharField("Chain annotation",
                                        null=True,
                                        max_length=255)


class Residue(models.Model):
    """
    Residue (amino acid) level data
    """
    chain_ref = models.ForeignKey(Chain,
                                  verbose_name="Chain this residue relates to",
                                  related_name="residues",
                                  on_delete=models.CASCADE)

    pdb_res_label = models.CharField("PDB residue label",
                                     max_length=10)

    aa_type = models.CharField("Amino acid code",
                               max_length=3)


class SiteData(models.Model):
    """
    Individual site-level information
    """
    residue_ref = models.ForeignKey(Residue,
                                    verbose_name="Residue this site relates to",
                                    related_name="site_data",
                                    on_delete=models.CASCADE)

    site_id_ref = models.IntegerField("Site JSON reference identifier")

    value = models.FloatField("Value",
                              null=True)

    confidence = models.FloatField("Confidence in the value",
                                   null=True)

    classification = models.CharField("Classification of the value",
                                      choices=CLASSIFICATION,
                                      max_length=100,
                                      null=True)


class Site(models.Model):
    """
    Site information (collection of site data)
    """
    site_id = models.IntegerField("Site JSON identifier")

    entry_ref = models.ForeignKey(Entry,
                                  verbose_name="Entry this site relates to",
                                  related_name="sites",
                                  on_delete=models.CASCADE)

    label = models.CharField("Site label",
                             choices=LABELS,
                             max_length=255)

    source_database = models.CharField("Source database",
                                       choices=SOURCE_DATABASE,
                                       max_length=20)

    source_accession = models.CharField("Source accession id",
                                        max_length=255)

    source_release_date = models.CharField("Source release date",
                                           max_length=10,
                                           null=True)


class EvidenceCodeOntology(models.Model):
    """
    ECO terms related to entry
    """
    entry_ref = models.ForeignKey(Entry,
                                  verbose_name="Entry this eco term relates to",
                                  related_name="evidence_code_ontology",
                                  on_delete=models.CASCADE)
    eco_term = models.CharField("Evidence Code Ontology term",
                                max_length=255)
