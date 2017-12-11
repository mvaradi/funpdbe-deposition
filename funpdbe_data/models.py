# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class EvidenceCodeOntology(models.Model):

    evidence_code_ontology = models.CharField("Evidence Code Ontology term",
                                              primary_key=True,
                                              max_length=255,
                                              null=False)


class DataResource(models.Model):

    data_resource = models.CharField("Data resource name",
                                     primary_key=True,
                                     max_length=255,
                                     null=False)
#     NOTE TO SELF: This should probably be controlled by the Group class from funpdbe_accounts


class Classification(models.Model):

    classification = models.CharField("Classification of the data",
                                      primary_key=True,
                                      max_length=200,
                                      null=False)

#     NOTE TO SELF: This should be a limited enumeration


class Label(models.Model):

    label = models.CharField("Site label",
                             primary_key=True,
                             max_length=255,
                             null=False)


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
                                    verbose_name="Residue this site data relates to")

    site_ref = models.ForeignKey(Site,
                                 verbose_name="Site of this site data")

    classification_ref = models.ForeignKey(Classification,
                                           verbose_name="Classification of this site data")

    value = models.FloatField("Value",
                              null=False)

    confidence = models.FloatField("Confidence of value",
                                   null=True)