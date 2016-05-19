from django.db import models

class MetaData(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class CardSet(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.SmallIntegerField()

    def __str__(self):
        return self.name

class CardType(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.SmallIntegerField()

    def __str__(self):
        return self.name

class Faction(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.SmallIntegerField()

    def __str__(self):
        return self.name

class Rarity(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.SmallIntegerField()

    def __str__(self):
        return self.name

class Race(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.SmallIntegerField()

    def __str__(self):
        return self.name

class Mechanic(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.SmallIntegerField()

    def __str__(self):
        return self.name

class CharacterClass(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.SmallIntegerField()

    def __str__(self):
        return self.name

class Card(models.Model):
    cardSet = models.ForeignKey(CardSet, on_delete=models.CASCADE)
    cardType = models.ForeignKey(CardType, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    rarity = models.ForeignKey(Rarity, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    #character_class = models.ForeignKey(CharacterClass, on_delete=models.CASCADE)

    cardId = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=64)

    cost = models.SmallIntegerField()
    value = models.SmallIntegerField()

    attack = models.SmallIntegerField()
    health = models.SmallIntegerField()

    text = models.CharField(max_length=124)
    mechanics = models.ManyToManyField(Mechanic)

    def __str__(self):
        return self.name
