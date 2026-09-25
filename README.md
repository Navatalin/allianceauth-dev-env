# Alliance Auth Docker development environment

This repository runs Alliance Auth, Redis, Wiki.js, and its PostgreSQL database
in Docker. Alliance Auth installs plugins listed in [plugins.json](plugins.json);
the OIDC provider is included by default. Database and Redis data are stored in
Docker volumes; the local Django project is bind-mounted for settings edits.

## Quick start

Install Docker Desktop, start its engine, and run from this repository root:

```powershell
.\bootstrap.ps1
```

Bootstrap creates an ignored `.env` with a random Django secret and an ignored
OIDC signing key, builds the Alliance Auth image, runs migrations, and starts
both web services. On first run, choose an Alliance Auth superuser name and
password when prompted. Rerunning bootstrap preserves existing accounts and
data. For noninteractive setup, use `.\bootstrap.ps1 -SkipAdminSetup`; create an
admin later with `docker compose exec auth python manage.py createsuperuser`.

Open Alliance Auth at <http://192-168-0-170.sslip.io:8000/> and Wiki.js at
<http://192-168-0-170.sslip.io:3000/>. Sign in to Alliance Auth admin at
`<AA_SITE_URL>/admin/` with your new superuser account. Complete the Wiki.js
setup wizard on first launch using the Wiki.js URL as its site URL; keep the
local Wiki.js administrator account for recovery.

For EVE SSO, register a development application at
<https://developers.eveonline.com> with the `publicData` scope and exact
callback `<AA_SITE_URL>/sso/callback`. Set `AA_ESI_CLIENT_ID` and
`AA_ESI_CLIENT_SECRET` in the ignored `.env` and restart the auth container.
The superuser can use Alliance Auth admin without EVE SSO.

The default `AA_SITE_URL` uses `192-168-0-170.sslip.io`, which resolves to
`192.168.0.170`. Change it in `.env` if your host LAN IP changes and restart
the containers. The hostname must resolve from your browser and from the Wiki.js
container; use the same hostname and port in OIDC issuer settings. Allow inbound
ports 8000 and 3000 through the host firewall for other LAN devices. Redis and
Wiki.js's PostgreSQL stay internal. This plain-HTTP setup is for trusted local
development only; Celery tasks run eagerly without a worker.

## Plugins

Edit [plugins.json](plugins.json) to add or remove plugins. Each entry has a
`package` (a pip package name, optionally with a version constraint) and `app`
(the Django app config/import path). Add `url` for a Git repository instead of
installing the package from PyPI. Use a `git+https://` URL and pin a ref when
repeatable builds matter. For example:

```json
[
   {"package": "allianceauth-example==1.2.3", "app": "example"},
   {"package": "allianceauth-other", "app": "other.apps.OtherConfig", "url": "git+https://github.com/example/allianceauth-other.git@v1.0.0"}
]
```

Replace these placeholders with real packages and their documented Django app
paths. Dependencies are installed into the image; the manifest is also read by
Django at startup. After editing the manifest, run `.\bootstrap.ps1` again to
rebuild the image, run migrations, and restart. Removing a plugin does not undo
its database migrations; back up data before removing one with persistent data.
For active development of a local plugin checkout, use a Git URL or add a
project-specific bind mount and editable install to the Dockerfile.

## OIDC provider

The manifest installs the OIDC provider from
`Navatalin/allianceauth-oidc-provider` on `master` using `pip install --upgrade`.
Bootstrap generates an ignored `oidc-private.pem` signing key if needed; keep
this key private and retain it when rebuilding so existing tokens remain valid.
`ALLIANCEAUTH_OIDC_EMAIL_DOMAIN` defaults to `test.com`. To change it, set that
variable in `.env` before restarting. The `email` claim uses
`<main_character_id>@test.com` for accounts with a main character. These are
synthetic addresses; change the domain to one you control and disable mail to
these accounts before enabling real email delivery.

Wiki.js OIDC login requires manual configuration after bootstrap:

1. In Wiki.js **Administration > Authentication**, add **Generic OpenID Connect
   / OAuth2** and copy the callback URL it displays.
2. In Alliance Auth admin at `<AA_SITE_URL>/admin/allianceauth_oidc/`, create a
   confidential authorization-code application with that exact callback URL.
   Grant intended users `allianceauth_oidc.access_oidc` (for example, through
   an Alliance Auth group). Copy the plaintext client secret when creating the
   application. The `pbkdf2_...` value shown after saving is a hash, not the
   Wiki.js secret; if the plaintext was lost, set a new one and update Wiki.js.
3. In Wiki.js, enter the client ID and plaintext secret. Set the authorization
   endpoint to `<AA_SITE_URL>/o/authorize/`, token endpoint to
   `<AA_SITE_URL>/o/token/`, UserInfo endpoint to
   `<AA_SITE_URL>/o/userinfo/`, and issuer to `<AA_SITE_URL>/o/`. Use `email`
   for **Email Claim** and `name` for **Display Name Claim**; this fork does not
   emit `wiki_email` or `displayName`. Leave **Skip User Profile** off and
   enable self-registration for first-time users. Save the strategy.

The provider discovery URL is
`<AA_SITE_URL>/o/.well-known/openid-configuration/`. Check its issuer from
both the browser and Wiki.js container if login fails; all settings must use
the same reachable hostname and port. Existing Wiki.js users get their display
name updated at their next OIDC sign-in.

For group mapping, set **Map Groups** on and **Groups Claim** to `groups`.
Wiki.js only assigns groups whose names already exist there; it does not create
groups from the claim. Create the specific groups you want under Wiki.js
**Administration > Groups** and configure their page and action permissions
before signing in again. Names must match exactly: Alliance Auth currently
sends AA group names plus the user's state (for example, `users` and `Guest`),
and the built-in Wiki.js `Guests` group is not the same as `Guest`. Do not grant
privileged Wiki.js permissions to a group unless matching Alliance Auth groups
or states should receive them. Wiki.js refreshes group assignments at login.

## Daily use

```powershell
.\start-auth.ps1
docker compose logs -f auth wiki
.\stop.ps1
```

To run Django checks: `docker compose exec auth python manage.py check`.
To remove all local database and Redis data: `docker compose down --volumes`.
This permanently deletes the Alliance Auth, Wiki.js, and Redis volumes.
