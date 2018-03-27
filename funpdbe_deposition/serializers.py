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
        fields = ('eco_term', 'eco_code')


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
    """
    This is the most complex of all serializers, mainly
    because this is the entry point for POST calls to the API

    The data coming in (request.data) is parsed and every sub-serializer
    dependent on the main Entry model is called from here
    """
    chains = ChainSerializer(many=True)
    sites = SiteSerializer(many=True)
    evidence_code_ontology = EvidenceCodeOntologySerializer(many=True)
    # Owner is not used in authentication, it is only for identification
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Entry
        fields = ('pk', 'pdb_id', 'data_resource', 'resource_version', 'software_version',
                  'resource_entry_url', 'release_date', 'chains', 'sites',
                  'evidence_code_ontology', 'owner')

    def create_subsection(self, parent, data, next_function):
        if data:
            for item in data:
                next_function(parent, item)

    def create_ecos(self, entry, eco_data):
        EvidenceCodeOntology.objects.create(entry_ref=entry, **eco_data)

    def create_sites(self, entry, site_data):
        Site.objects.create(entry_ref=entry, **site_data)

    def create_chains_or_residues(self, parent, data, label):
        if label not in ["residues", "site_data"]:
            return None
        popped = data.pop(label, None)
        if label == "residues":
            new_item = Chain.objects.create(entry_ref=parent, **data)
            to_call = self.create_residues_data
        else:
            new_item = Residue.objects.create(chain_ref=parent, **data)
            to_call = self.create_site_details
        self.create_subsection(new_item, popped, to_call)

    def create_chains(self, entry, chain_data):
        self.create_chains_or_residues(entry, chain_data, "residues")

    def create_residues_data(self, chain, residue_data):
        self.create_chains_or_residues(chain, residue_data, "site_data")

    def create_site_details(self, residue, site_detail):
        SiteData.objects.create(residue_ref=residue, **site_detail)

    def create(self, validated_data):
        chains_data = validated_data.pop('chains', None)
        sites_data = validated_data.pop('sites', None)
        ecos_data = validated_data.pop('evidence_code_ontology', None)
        entry = Entry.objects.create(**validated_data)

        self.create_subsection(entry, sites_data, self.create_sites)
        self.create_subsection(entry, ecos_data, self.create_ecos)
        self.create_subsection(entry, chains_data, self.create_chains)

        return entry
