from django.contrib.auth.models import User
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

    def post(self, request):
        # TODO consider moving to single entry view
        # print(request.data)
        serializer = EntrySerializer(data=request.data)
        # print(serializer)
        if serializer.is_valid():
            serializer.save(owner=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EntryListByResource(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get(self, request, resource):
        for RESOURCE in RESOURCES:
            if resource in RESOURCE:
                entries = Entry.objects.filter(data_resource=resource)
                serializer = EntrySerializer(entries, many=True)
                return Response(serializer.data)
        return Response("Invalid data resource", status=status.HTTP_400_BAD_REQUEST)


class EntryDetail(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)

    def get(self, request, pdb_id):
        entries = Entry.objects.filter(pdb_id=pdb_id)
        serializer = EntrySerializer(entries, many=True)
        return Response(serializer.data)

    def delete(self, request, pdb_id):
        user = request.user
        entries = Entry.objects.filter(pdb_id=pdb_id)
        if entries:
            for entry in entries:
                if entry.owner == user:
                    entry.delete()
                    return Response("Deleted entry of %s with PDB id %s" % (
                        user,
                        pdb_id), status=status.HTTP_200_OK)
                else:
                    return Response("User %s has not entry with PDB id %s" % (
                        user,
                        pdb_id
                    ), status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("Entry not found", status=status.HTTP_404_NOT_FOUND)


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


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer