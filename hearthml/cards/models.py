from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save

class MetaData(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.FloatField()

    def __str__(self):
        return "[" + str(self.value) + "] " + self.name

class CardSet(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.FloatField()

    def __str__(self):
        return "[" + str(self.value) + "] " + self.name

class CardType(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.FloatField()

    def __str__(self):
        return "[" + str(self.value) + "] " + self.name

class Faction(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.FloatField()

    def __str__(self):
        return "[" + str(self.value) + "] " + self.name

class Rarity(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.FloatField()

    def __str__(self):
        return "[" + str(self.value) + "] " + self.name

class Race(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.FloatField()

    def __str__(self):
        return "[" + str(self.value) + "] " + self.name

class Mechanic(models.Model):
    name = models.CharField(max_length=128, unique=True)
    value = models.FloatField()

    def __str__(self):
        return "[" + str(self.value) + "] " + self.name

class CharacterClass(models.Model):
    name = models.CharField(max_length=32, unique=True)
    value = models.FloatField()

    def __str__(self):
        return "[" + str(self.value) + "] " + self.name

class Card(models.Model):
    cardSet = models.ForeignKey(CardSet, on_delete=models.CASCADE)
    cardType = models.ForeignKey(CardType, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, on_delete=models.CASCADE)
    rarity = models.ForeignKey(Rarity, on_delete=models.CASCADE)
    race = models.ForeignKey(Race, on_delete=models.CASCADE)
    character_class = models.ForeignKey(CharacterClass, on_delete=models.CASCADE)

    image = models.CharField(max_length=128)

    cardId = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=64)

    complex_value = models.FloatField()
    simple_value = models.FloatField()

    mana = models.SmallIntegerField()
    attack = models.SmallIntegerField()
    health = models.SmallIntegerField()

    text = models.CharField(max_length=124)
    card_mechanics = models.ManyToManyField(Mechanic, through='CardMechanic')

    def __str__(self):
        return self.name + " [" + str(self.mana) + ": " + str(self.attack) + "/" + str(self.health) + "]"

class CardMechanic(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    mechanic = models.ForeignKey(Mechanic, on_delete=models.CASCADE)
    effect_size = models.FloatField()

    class Meta:
        unique_together = ("card", "mechanic")

@receiver(post_save, sender=MetaData)
def update_simple_values_meta(sender, **kwargs):
    if not kwargs.get('created', False):
        for card in Card.objects.all():
            update_simple_value(card)
            card.save()

@receiver(post_save, sender=Mechanic)
def update_simple_values_mech(sender, instance, **kwargs):
    if not kwargs.get('created', False):
        for cm in CardMechanic.objects.filter(mechanic = instance):
            update_simple_value(cm.card)
            cm.card.save()


def update_simple_value(card):
    simple_value = card.cardType.value
    simple_value += card.health * MetaData.objects.get(name="health_coeff").value

    if card.cardType.name == "Minion":
        simple_value += card.attack * MetaData.objects.get(name="minion_attack_coeff").value
    elif card.cardType.name == "Weapon":
        simple_value += card.attack * MetaData.objects.get(name="weapon_attack_coeff").value

    for cm in CardMechanic.objects.filter(card = card):
        simple_value += cm.mechanic.value * cm.effect_size

    card.simple_value = simple_value
