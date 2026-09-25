import os

from django.contrib.auth.models import Group, Permission, User

from allianceauth.authentication.models import State
from allianceauth.eveonline.models import EveCharacter

members, _ = Group.objects.get_or_create(name="AA-Members")
members.permissions.add(
    Permission.objects.get(content_type__app_label="wikijs", codename="access_wikijs"),
    Permission.objects.get(content_type__app_label="allianceauth_oidc", codename="access_oidc"),
    Permission.objects.get(content_type__app_label="groupmanagement", codename="request_groups"),
)
admins, _ = Group.objects.get_or_create(name="AA-Admins")
admins.permissions.add(
    Permission.objects.get(content_type__app_label="auth", codename="group_management"),
)
admins.authgroup.restricted = True
admins.authgroup.save(update_fields=["restricted"])

username = os.getenv("AA_ADMIN_USERNAME", "admin")
password = os.getenv("AA_ADMIN_PASSWORD", "local-development-password")
character_id = int(os.getenv("AA_CHARACTER_ID", "90000001"))

user, _ = User.objects.get_or_create(
    username=username,
    defaults={"email": "local-admin@example.invalid"},
)
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()

character, _ = EveCharacter.objects.update_or_create(
    character_id=character_id,
    defaults={
        "character_name": "Local Wiki Admin",
        "corporation_id": 98000001,
        "corporation_name": "Local Development Corporation",
        "corporation_ticker": "DEV",
    },
)
user.profile.main_character = character
user.profile.save()
member_characters = [character]

wiki_admin, _ = Group.objects.get_or_create(name="Wiki-Admin")
wiki_admin.permissions.add(Permission.objects.get(codename="access_wikijs"))
user.groups.add(wiki_admin)
user.groups.add(members, admins)

print(f"Local Alliance Auth user ready: {username}")
print(f"Main character ID: {character_id}")
print("Wiki.js group: Wiki-Admin -> Administrators")

for username, character_id, character_name, group_name in (
    ("wiki_reader", 90000002, "Local Wiki Reader", "Wiki-Reader"),
    ("wiki_editor", 90000003, "Local Wiki Editor", "Wiki-Editor"),
):
    user, _ = User.objects.get_or_create(username=username)
    user.set_password("local-development-password")
    user.save()

    character, _ = EveCharacter.objects.update_or_create(
        character_id=character_id,
        defaults={
            "character_name": character_name,
            "corporation_id": 98000001,
            "corporation_name": "Local Development Corporation",
            "corporation_ticker": "DEV",
        },
    )
    user.profile.main_character = character
    user.profile.save()
    member_characters.append(character)

    group, _ = Group.objects.get_or_create(name=group_name)
    group.permissions.add(Permission.objects.get(codename="access_wikijs"))
    user.groups.add(group, members)
    print(f"Local Alliance Auth user ready: {username} ({character_name}, {character_id}, {group_name})")

State.objects.get(name="Member").member_characters.add(*member_characters)