# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import Group


class EvidenceCodeOntology(models.Model):
    """
    Evidence Code Ontology terms

    Terms are a subset of https://www.ebi.ac.uk/ols/ontologies/eco
    with focus on terms that are relevant to FunPDBe annotations
    """
    evidence_code_ontology = models.CharField("Evidence Code Ontology term",
                                              primary_key=True,
                                              max_length=255)
#     NOTE TO SELF: This will be a controlled dictionary


class DataResource(models.Model):
    """
    Data resources defined in Groups()
    """
    data_resource = models.ForeignKey(Group,
                                      verbose_name="Related group class")


class Classification(models.Model):
    """
    Classification terms
    """
    classification = models.CharField("Classification of the data",
                                      primary_key=True,
                                      max_length=200)
#     NOTE TO SELF: This should be a limited enumeration, once we know what the vocabulary is


class Label(models.Model):
    """
    Labels for sites
    """
    label = models.CharField("Site label",
                             primary_key=True,
                             max_length=255)


class SourceDataset(models.Model):

    source_release_date = models.DateField("Date of the release of the original data",
                                           null=True)

    source_database = models.CharField("Name of the evidence source database (PDB or UniProt for most cases)",
                                 max_length=100,
                                 null=False)


class Site(models.Model):

    label_ref = models.ForeignKey(Label,
                                  verbose_name="Label related to this site")

    source_dataset_ref = models.ForeignKey(SourceDataset,
                                           verbose_name="Source dataset related to this site")

    source_accession = models.CharField("Source dataset accession identifier",
                                        max_length=255,
                                        null=False)


class Entry(models.Model):

    data_resource_ref = models.ForeignKey(DataResource,
                                          verbose_name="Data resource related to this entry")

    resource_version = models.CharField("Version of the resource",
                                        max_length=25,
                                        null=True)

    software_version = models.CharField("Version of the software",
                                         max_length=25,
                                         null=True)

    resource_entry_url = models.URLField("URL of the data at the original resource",
                                         null=True)

    release_date = models.DateField("Release date of the data",
                                    null=True)

    pdb_id = models.CharField("PDB identifier",
                              null=False,
                              max_length = 10)


class EvidenceCodeOntologyOfEntry(models.Model):

    evidence_code_ontology_ref = models.ForeignKey(EvidenceCodeOntology,
                                                   verbose_name="Related ECO")

    entry_ref = models.ForeignKey(Entry,
                                  verbose_name="Related entry")


class Chain(models.Model):

    entry_ref = models.ForeignKey(Entry,
                                  verbose_name="Entry related to this chain")

    chain_label = models.CharField("Chain identifier label",
                                   null=False,
                                   max_length=20)


class Residue(models.Model):

    chain_ref = models.ForeignKey(Chain,
                                  verbose_name="Chain this residue relates to ")

    pdb_res_label = models.CharField("PDB residue label",
                                     max_length=10,
                                     null=False)

    aa_type = models.CharField("Amino acid code",
                               max_length=3,
                               null=False)


class SiteData(models.Model):

    residue_ref = models.ForeignKey(Residue,
                                    verbose_name="Residue this site data relates to",
                                    null=False)

    site_ref = models.ForeignKey(Site,
                                 verbose_name="Site of this site data",
                                 null=False)

    classification_ref = models.ForeignKey(Classification,
                                           verbose_name="Classification of this site data",
                                           null=True)

    value = models.FloatField("Value",
                              null=False)

    confidence = models.FloatField("Confidence of value",
                                   null=True)