# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-19 13:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cardId', models.CharField(max_length=16, unique=True)),
                ('name', models.CharField(max_length=64)),
                ('cost', models.SmallIntegerField()),
                ('value', models.SmallIntegerField()),
                ('attack', models.SmallIntegerField()),
                ('health', models.SmallIntegerField()),
                ('text', models.CharField(max_length=124)),
            ],
        ),
        migrations.CreateModel(
            name='CardSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('value', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CardType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('value', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CharacterClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('value', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Faction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('value', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Mechanic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('value', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Race',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('value', models.SmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Rarity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('value', models.SmallIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='cardSet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cards.CardSet'),
        ),
        migrations.AddField(
            model_name='card',
            name='cardType',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cards.CardType'),
        ),
        migrations.AddField(
            model_name='card',
            name='faction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cards.Faction'),
        ),
        migrations.AddField(
            model_name='card',
            name='mechanics',
            field=models.ManyToManyField(to='cards.Mechanic'),
        ),
        migrations.AddField(
            model_name='card',
            name='race',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cards.Race'),
        ),
        migrations.AddField(
            model_name='card',
            name='rarity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cards.Rarity'),
        ),
    ]
