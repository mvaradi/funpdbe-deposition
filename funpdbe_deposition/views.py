import re
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from funpdbe_deposition.models import Entry
from funpdbe_deposition.models import RESOURCES
from funpdbe_deposition.serializers import EntrySerializer

PDB_PATTERN = "^[0-9][A-Za-z][A-Za-z0-9]{2}$"
GENERIC_RESPONSES = {
    "no entries": Response("No entries found", status=status.HTTP_404_NOT_FOUND),
    "invalid pattern": Response("Invalid PDB id pattern", status=status.HTTP_400_BAD_REQUEST),
    "invalid resource": Response("Invalid data resource", status=status.HTTP_400_BAD_REQUEST),
    "no permission": Response("User not allowed to perform this request", status=status.HTTP_403_FORBIDDEN),
    "no create permission": Response("User does not have permission to PUT for this resource", status=status.HTTP_403_FORBIDDEN),
    "bad request": Response("PDB id or resource name invalid", status=status.HTTP_400_BAD_REQUEST)
}


def get_existing_entry(entry):
    if not entry:
        return GENERIC_RESPONSES["no entries"]
    else:
        return serialize(entry)


def serialize(entry):
    serializer = EntrySerializer(entry, many=True)
    return Response(serializer.data)


def resource_valid(resource):
    for RESOURCE in RESOURCES:
        if resource in RESOURCE:
            return True
    return False


def pdb_id_valid(pdb_id):
    if re.match(PDB_PATTERN, pdb_id):
        return True
    return False


def user_groups(user):
    user_groups = []
    for group in user.groups.all():
        user_groups.append(str(group))
    return user_groups

def delete_entries(entries):
    if entries:
        for entry in entries:
            entry.delete()
            return True
    else:
        return False


class EntryList(APIView):
    """
    This is the basic view which can list (GET) all entries
    """

    def get(self, request):
        """
        This call can:
        * work OK (200)
        * fail with not found (404) when there are no entries at all
        :param request: Request
        :return: Response
        """
        entries = Entry.objects.all()
        return get_existing_entry(entries)


class EntryListByResource(APIView):
    """
    These views either list entries belonging to a resource (GET), or add new entries
    under one resource (POST)
    """

    def get(self, request, resource):
        """
        This call can:
        * work OK (200)
        * fail with not found (404) when there are no entries for a resource
        * fail with bad request (400) when the resource name is invalid
        :param request: Request
        :param resource: String, resource name provided by the user
        :return: Response
        """

        # Validate resource name
        if resource_valid(resource):
            entries = Entry.objects.filter(data_resource=resource)
            response = get_existing_entry(entries)
        else:
            response = GENERIC_RESPONSES["invalid resource"]
        return response

    def post(self, request, resource):
        """
        This call can:
        * create entry (201)
        * fail with bad request (400) when the JSON is invalid
        * fail with bad request (400) when the resource name provided and resource name in JSON mismatch
        * fail with forbidden (403) when user is anonymous or is not allowed to POST to a resource
        * fail with bad request (400) when the resource name is invalid
        :param request: Request
        :param resource: Resource
        :return:
        """
        # Validate resource name

        for RESOURCE in RESOURCES:
            if resource in RESOURCE:
                try:
                    resource_according_to_json = request.data["data_resource"]
                except:
                    return Response("Invalid JSON data - check against FunPDBe schema", status=status.HTTP_400_BAD_REQUEST)
                if resource != resource_according_to_json:
                    return Response("User provided resource name and JSON does not match", status=status.HTTP_400_BAD_REQUEST)
                user_groups = []
                for group in request.user.groups.all():
                    user_groups.append(str(group))
                if resource not in user_groups:
                    return GENERIC_RESPONSES["no create permission"]
                serializer = EntrySerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save(owner=self.request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return GENERIC_RESPONSES["invalid resource"]


class EntryListByPdb(APIView):
    """
    This view (only GET) can list entries for a specific PDB id
    """

    def get(self, request, pdb_id):
        """
        This call can:
        * work OK (200)
        * fail with bad request (400) when the PDB id has an invalid reg.ex. pattern
        * fail with not found (404)
        :param request: Request
        :param pdb_id: String, pattern: ^[0-9][A-Za-z][A-Za-z0-9]{2}$
        :return: Response
        """
        # Validate PDB id
        if pdb_id_valid(pdb_id):
            entries = Entry.objects.filter(pdb_id=pdb_id.lower())
            response = get_existing_entry(entries)
        else:
            response = GENERIC_RESPONSES["invalid pattern"]
        return response


class EntryDetailByResource(APIView):
    """
    These views either display one specific entry based on resource name
    and PDB id (GET), or remove one specific entry (DELETE)
    """

    def get(self, request, resource, pdb_id):
        """
        This call can:
        * work OK (200)
        * fail with bad request (400) when the PDB id has an invalid reg.ex. pattern
        * fail with bad request (400) when the resource name is invalid
        * fail with not found (404)
        :param request: Request
        :param resource: String, resource name provided by the user
        :param pdb_id: String, pattern: ^[0-9][A-Za-z][A-Za-z0-9]{2}$
        :return: Response
        """
        # Validate PDB id
        if pdb_id_valid(pdb_id):
            # Validate resource name
            if resource_valid(resource):
                entries = Entry.objects.filter(data_resource=resource).filter(pdb_id=pdb_id.lower())
                # If entry/entries exist, serialize them
                response = get_existing_entry(entries)
            else:
                response = GENERIC_RESPONSES["invalid resource"]
        else:
            response = GENERIC_RESPONSES["invalid pattern"]
        return response

    def delete(self, request, resource, pdb_id):
        """
        This call can:
        * delete an entry (301)
        * fail with bad request (400) when the PDB id has an invalid reg.ex. pattern
        * fail with bad request (400) when the resource name is invalid
        * fail with not found (404)
        * fail with forbidden (403) when user is anonymous or has no permission to remove this entry
        :param request: Request
        :param resource: String, resource name provided by the user
        :param pdb_id: String, pattern: ^[0-9][A-Za-z][A-Za-z0-9]{2}$
        :return: Response
        """
        validated = False
        if pdb_id_valid(pdb_id):
            if resource_valid(resource):
                validated = True

        if validated:
            if resource in user_groups(request.user):
                entries = Entry.objects.filter(pdb_id=pdb_id.lower()).filter(data_resource=resource)
                if delete_entries(entries):
                    response = Response("Deleted entry of %s with PDB id %s" % (request.user, pdb_id), status=status.HTTP_301_MOVED_PERMANENTLY)
                else:
                    response = GENERIC_RESPONSES["no entries"]
            else:
                response = GENERIC_RESPONSES["no permission"]
        else:
            response = GENERIC_RESPONSES["bad request"]

        return response

    def post(self, request, resource, pdb_id):
        """
        This call can:
        * update an entry (although by first deleting, then creating) (201)
        * fail with bad request (400) when the PDB id has an invalid reg.ex. pattern
        * fail with bad request (400) when the resource name is invalid
        * fail with not found (404)
        * fail with forbidden (403) when user is anonymous or has no permission to edit this entry
        * fail with bad request (400) when the JSON is invalid
        * fail with bad request (400) when the resource name provided and resource name in JSON mismatch
        :param request:
        :param resource:
        :param pdb_id:
        :return:
        """

        # Try matching PDB id with reg.ex. pattern
        if not re.match(PDB_PATTERN, pdb_id):
            return GENERIC_RESPONSES["invalid pattern"]

        # Check if resource is a valid resource name
        for RESOURCE in RESOURCES:
            if resource in RESOURCE:
                user = request.user
                user_groups = []
                for group in user.groups.all():
                    user_groups.append(str(group))
                # Check if user has permission to edit at this resource
                if resource not in user_groups:
                    return GENERIC_RESPONSES["no create permission"]

                # First delete the entry (cascading)
                entries = Entry.objects.filter(pdb_id=pdb_id.lower()).filter(data_resource=resource)
                if entries:
                    for entry in entries:
                        entry.delete()
                else:
                    return GENERIC_RESPONSES["no entries"]

                # Then try to create a new entry
                try:
                    resource_according_to_json = request.data["data_resource"]
                    if resource != resource_according_to_json:
                        return Response("User provided resource name and JSON does not match", status=status.HTTP_400_BAD_REQUEST)
                    serializer = EntrySerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save(owner=self.request.user)
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response("Invalid JSON data - check against FunPDBe schema", status=status.HTTP_400_BAD_REQUEST)

        return GENERIC_RESPONSES["invalid resource"]
