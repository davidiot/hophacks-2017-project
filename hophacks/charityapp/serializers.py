from django.contrib.auth.models import User, Group
from .models import *
from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ('customer_id',)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ('url', 'id', 'username', 'password', 'email', 'is_staff',
                  'groups', 'profile')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data.get('username')
        password = validated_data.get('password')
        email = validated_data.get('email')
        is_staff = validated_data.get('is_staff')
        profile_data = validated_data.pop('profile')
        user = User.objects.create_superuser(
            username=username,
            password=password,
            email=email) \
            if is_staff else User.objects.create_user(
            username=username,
            password=password,
            email=email)
        Profile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        # Unless the application properly enforces that this field is
        # always set, the follow could raise a `DoesNotExist`, which
        # would need to be handled.
        profile = instance.profile

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.groups = validated_data.get('groups', instance.groups)
        instance.save()

        profile.customer_id = profile_data.get(
            'customer_id',
            profile.customer_id
        )
        profile.save()

        return instance


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')


class SectorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sector
        fields = ('name', 'national_average')