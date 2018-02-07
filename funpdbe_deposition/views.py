from django.contrib.auth.models import User, Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from funpdbe_deposition.serializers import UserSerializer
from funpdbe_deposition.models import Entry
from funpdbe_deposition.models import RESOURCES
from funpdbe_deposition.serializers import EntrySerializer
from funpdbe_deposition.permissions import IsOwnerOrReadOnly


class EntryList(APIView):
    """
    List all funsite entries, or post a new entry.
    """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get(self, request):
        entries = Entry.objects.all()
        serializer = EntrySerializer(entries, many=True)
        return Response(serializer.data)


class EntryListByResource(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get(self, request, resource):
        for RESOURCE in RESOURCES:
            if resource in RESOURCE:
                entries = Entry.objects.filter(data_resource=resource)
                serializer = EntrySerializer(entries, many=True)
                return Response(serializer.data)
        return Response("Invalid data resource", status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, resource):
        serializer = EntrySerializer(data=request.data)
        resource_according_to_json = request.data["data_resource"]
        if resource != resource_according_to_json:
            return Response("User provided resource name and JSON does not match", status=status.HTTP_400_BAD_REQUEST)
        user_groups = []
        for group in request.user.groups.all():
            user_groups.append(str(group))
        if resource not in user_groups:
            return Response("User does not have permission to POST to this resource", status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EntryDetail(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get(self, request, pdb_id):
        entries = Entry.objects.filter(pdb_id=pdb_id)
        serializer = EntrySerializer(entries, many=True)
        return Response(serializer.data)


class EntryDetailByResource(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get(self, request, resource, pdb_id):
        for RESOURCE in RESOURCES:
            if resource in RESOURCE:
                entries = Entry.objects.filter(data_resource=resource).filter(pdb_id=pdb_id)
                if entries:
                    serializer = EntrySerializer(entries, many=True)
                    return Response(serializer.data)
                else:
                    return Response("Entry not found", status=status.HTTP_404_NOT_FOUND)
        return Response("Invalid data resource", status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, resource, pdb_id):
        for RESOURCE in RESOURCES:
            if resource in RESOURCE:
                user = request.user
                user_groups = []
                for group in user.groups.all():
                    user_groups.append(str(group))
                if resource not in user_groups:
                    return Response("User does not have permission to DELETE from this resource", status=status.HTTP_403_FORBIDDEN)
                entries = Entry.objects.filter(pdb_id=pdb_id).filter(data_resource=resource)
                if entries:
                    for entry in entries:
                        entry.delete()
                        return Response("Deleted entry of %s with PDB id %s" % (user, pdb_id), status=status.HTTP_301_MOVED_PERMANENTLY)
                else:
                    return Response("Entry not found", status=status.HTTP_404_NOT_FOUND)
        return Response("Invalid data resource", status=status.HTTP_400_BAD_REQUEST)


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer