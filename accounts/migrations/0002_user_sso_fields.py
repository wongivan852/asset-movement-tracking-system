# Generated migration for SSO integration fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sso_user',
            field=models.BooleanField(default=False, help_text='User authenticated via SSO'),
        ),
        migrations.AddField(
            model_name='user',
            name='sso_provider',
            field=models.CharField(blank=True, help_text='SSO provider name (SAML, OAuth, LDAP)', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='sso_id',
            field=models.CharField(blank=True, help_text='Unique identifier from SSO provider', max_length=255, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='last_sso_login',
            field=models.DateTimeField(blank=True, help_text='Last successful SSO login', null=True),
        ),
    ]
