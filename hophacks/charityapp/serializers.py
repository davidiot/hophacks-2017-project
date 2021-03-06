from django.contrib.auth.models import User, Group
from .models import *
from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ('customer_id', 'charity_account_id')


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
        profile.charity_account_id = profile_data.get(
            'charity_account_id',
            profile.charity_account_id
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
        fields = ('url', 'id', 'name', 'national_average')


class CharitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Charity
        fields = ('url', 'id', 'merchant_id', 'picture', 'description', 'link', 'email',
                  'name', 'sector')


class LinkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Link
        fields = ('url', 'id', 'purchase_id', 'transfer_id', 'sector',
                  'merchant', 'date', 'purchase_amount', 'transfer_amount')


class RuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rule
        fields = ('url', 'id', 'user', 'sector', 'rate')


class SuggestionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Suggestion
        fields = ('url', 'id', 'name', 'sector', 'picture', 'description',
                  'rule_creator',
                  'threshold')


class DonationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Donation
        fields = ('url', 'id', 'user', 'charity', 'purchase_id')
