# Generated by Django 4.0.6 on 2022-08-21 18:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clashdata', '0011_alter_clanmemberhistory_clandestiny'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoyaleApiConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=255)),
                ('key', models.TextField()),
            ],
        ),
        migrations.AlterModelOptions(
            name='clanmemberhistory',
            options={'ordering': ['-date']},
        ),
        migrations.AlterField(
            model_name='clanmemberhistory',
            name='clanDestiny',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_clan_destiny', to='clashdata.clan'),
        ),
        migrations.AlterField(
            model_name='clanmemberhistory',
            name='clanMember',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_histories', to='clashdata.clanmember'),
        ),
        migrations.AlterField(
            model_name='clanmemberhistory',
            name='clanSource',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='member_clan_source', to='clashdata.clan'),
        ),
    ]
