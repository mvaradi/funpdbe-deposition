from rest_framework import serializers
from funpdbe_deposition.models import Entry
from funpdbe_deposition.models import Chain
from funpdbe_deposition.models import Residue
from funpdbe_deposition.models import Site
from funpdbe_deposition.models import SiteData
from funpdbe_deposition.models import EvidenceCodeOntology
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    entries = serializers.PrimaryKeyRelatedField(many=True, queryset=Entry.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'entries')


class EvidenceCodeOntologySerializer(serializers.ModelSerializer):
    class Meta:
        model = EvidenceCodeOntology
        fields = ['eco_term', 'eco_code']


class SiteDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteData
        fields = ('site_id_ref', 'raw_score', 'confidence_score', 'confidence_classification')


class ResidueSerializer(serializers.ModelSerializer):
    site_data = SiteDataSerializer(many=True)

    class Meta:
        model = Residue
        fields = ('pdb_res_label', 'aa_type', 'site_data')


class ChainSerializer(serializers.ModelSerializer):
    residues = ResidueSerializer(many=True)

    class Meta:
        model = Chain
        fields = ('chain_label', 'chain_annotation', 'residues')


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ("site_id", "label", "source_database", "source_accession", "source_release_date")


class EntrySerializer(serializers.ModelSerializer):
    chains = ChainSerializer(many=True)
    sites = SiteSerializer(many=True)
    evidence_code_ontology = EvidenceCodeOntologySerializer(many=True)
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Entry
        fields = ('pk', 'pdb_id', 'data_resource', 'resource_version', 'software_version',
                  'resource_entry_url', 'release_date', 'chains', 'sites',
                  'evidence_code_ontology', 'owner')

    def create(self, validated_data):
        chains_data = validated_data.pop('chains', None)
        sites_data = validated_data.pop('sites', None)
        ecos_data = validated_data.pop('evidence_code_ontology', None)
        entry = Entry.objects.create(**validated_data)

        if ecos_data:
            for eco_data in ecos_data:
                EvidenceCodeOntology.objects.create(entry_ref=entry, **eco_data)

        if sites_data:
            for site_data in sites_data:
                Site.objects.create(entry_ref=entry, **site_data)

        if chains_data:
            for chain_data in chains_data:
                residues_data = chain_data.pop('residues', None)
                chain = Chain.objects.create(entry_ref=entry, **chain_data)
                if residues_data:
                    for residue_data in residues_data:
                        site_details = residue_data.pop('site_data', None)
                        residue = Residue.objects.create(chain_ref=chain, **residue_data)
                        for site_detail in site_details:
                            SiteData.objects.create(residue_ref=residue, **site_detail)
        return entry
