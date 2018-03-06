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

    def pop_one(self, data, label):
        popped = data.pop(label, None)
        return [data, popped]

    def create_chains(self, entry, chain_data):
        popped = self.pop_one(chain_data, "residues")
        chain = Chain.objects.create(entry_ref=entry, **popped[0])
        self.create_subsection(chain, popped[1], self.create_residues_data)

    def create_residues_data(self, chain, residue_data):
        popped = self.pop_one(residue_data, "site_data")
        residue = Residue.objects.create(chain_ref=chain, **popped[0])
        self.create_subsection(residue, popped[1], self.create_site_details)

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
