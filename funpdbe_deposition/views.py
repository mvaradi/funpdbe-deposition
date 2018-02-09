import re
from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from funpdbe_deposition.serializers import UserSerializer
from funpdbe_deposition.models import Entry
from funpdbe_deposition.models import RESOURCES
from funpdbe_deposition.serializers import EntrySerializer


class EntryList(APIView):
    """
    This is the basic view which can list (GET) all entries
    """

    def get(self, request):
        """
        This GET view can:
        * work OK (200)
        * fail with not found (404) when there are no entries at all
        :param request: Request
        :return: Response
        """
        entries = Entry.objects.all()
        if not entries:
            return Response("No entries found", status=status.HTTP_404_NOT_FOUND)
        serializer = EntrySerializer(entries, many=True)
        return Response(serializer.data)


class EntryListByResource(APIView):
    """
    These views either list entries belonging to a resource (GET), or add new entries
    under one resource (POST)
    """

    def get(self, request, resource):
        """
        This view can:
        * work OK (200)
        * fail with not found (404) when there are no entries for a resource
        * fail with bad request (400) when the resource name is invalid
        :param request: Request
        :param resource: String, resource name provided by the user
        :return: Response
        """
        for RESOURCE in RESOURCES:
            if resource in RESOURCE:
                entries = Entry.objects.filter(data_resource=resource)
                if not entries:
                    return Response("No entries found", status=status.HTTP_404_NOT_FOUND)
                serializer = EntrySerializer(entries, many=True)
                return Response(serializer.data)
        return Response("Invalid data resource", status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, resource):
        """
        This view can:
        * create entry (201)
        * fail with bad request (400) when the JSON is invalid
        * fail with bad request (400) when the resource name provided and resource name in JSON mismatch
        * fail with forbidden (403) when user is anonymous or is not allowed to POST to a resource
        * fail with bad request (400) when the resource name is invalid
        :param request: Request
        :param resource: Resource
        :return:
        """
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
                    return Response("User does not have permission to POST to this resource", status=status.HTTP_403_FORBIDDEN)
                try:
                    serializer = EntrySerializer(data=request.data)
                except:
                    return Response("Invalid JSON data - check against FunPDBe schema", status=status.HTTP_400_BAD_REQUEST)
                if serializer.is_valid():
                    serializer.save(owner=self.request.user)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("Invalid data resource", status=status.HTTP_400_BAD_REQUEST)


class EntryListByPdb(APIView):
    """
    This view (only GET) can list entries for a specific PDB id
    """

    def get(self, request, pdb_id):
        """
        This view can:
        * work OK (200)
        * fail with bad request (400) when the PDB id has an invalid reg.ex. pattern
        * fail with not found (404)
        :param request: Request
        :param pdb_id: String, pattern: ^[0-9][A-Za-z][A-Za-z0-9]{2}$
        :return: Response
        """
        if not re.match("^[0-9][A-Za-z][A-Za-z0-9]{2}$", pdb_id):
            return Response("Invalid PDB id pattern", status=status.HTTP_400_BAD_REQUEST)
        entries = Entry.objects.filter(pdb_id=pdb_id.lower())
        if not entries:
            return Response("No entry found for PDB id %s" % pdb_id, status=status.HTTP_404_NOT_FOUND)
        serializer = EntrySerializer(entries, many=True)
        return Response(serializer.data)


class EntryDetailByResource(APIView):
    """
    These views either display one specific entry based on resource name
    and PDB id (GET), or remove one specific entry (DELETE)
    """

    def get(self, request, resource, pdb_id):
        """
        This view can:
        * work OK (200)
        * fail with bad request (400) when the PDB id has an invalid reg.ex. pattern
        * fail with bad request (400) when the resource name is invalid
        * fail with not found (404)
        :param request: Request
        :param resource: String, resource name provided by the user
        :param pdb_id: String, pattern: ^[0-9][A-Za-z][A-Za-z0-9]{2}$
        :return: Response
        """
        if not re.match("^[0-9][A-Za-z][A-Za-z0-9]{2}$", pdb_id):
            return Response("Invalid PDB id pattern", status=status.HTTP_400_BAD_REQUEST)
        for RESOURCE in RESOURCES:
            if resource in RESOURCE:
                entries = Entry.objects.filter(data_resource=resource).filter(pdb_id=pdb_id.lower())
                if entries:
                    serializer = EntrySerializer(entries, many=True)
                    return Response(serializer.data)
                else:
                    return Response("Entry not found", status=status.HTTP_404_NOT_FOUND)
        return Response("Invalid data resource", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, resource, pdb_id):
        """
        This view can:
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
        if not re.match("[0-9][A-Za-z][A-Za-z0-9]", pdb_id):
            return Response("Invalid PDB id pattern", status=status.HTTP_400_BAD_REQUEST)
        for RESOURCE in RESOURCES:
            if resource in RESOURCE:
                user = request.user
                user_groups = []
                for group in user.groups.all():
                    user_groups.append(str(group))
                if resource not in user_groups:
                    return Response("User does not have permission to DELETE from this resource", status=status.HTTP_403_FORBIDDEN)
                entries = Entry.objects.filter(pdb_id=pdb_id.lower()).filter(data_resource=resource)
                if entries:
                    for entry in entries:
                        entry.delete()
                        return Response("Deleted entry of %s with PDB id %s" % (user, pdb_id), status=status.HTTP_301_MOVED_PERMANENTLY)
                else:
                    return Response("Entry not found", status=status.HTTP_404_NOT_FOUND)
        return Response("Invalid data resource", status=status.HTTP_400_BAD_REQUEST)
