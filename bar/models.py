from datetime import date

from django.db import models


class Menu(models.Model):
    name = models.CharField(
        verbose_name='nombre',
        max_length=200,
    )
    price = models.DecimalField(
        verbose_name='precio',
        max_digits=8,
        decimal_places=2
    )
    order = models.PositiveSmallIntegerField(
        verbose_name='orden',
        db_index=True
    )

    SEDE_MADERO = 1
    SEDE_POSTGRADO = 2
    SEDE_PATRICIOS = 3

    SEDE_CHOICES = (
        (SEDE_MADERO, 'Sede Madero'),
        (SEDE_PATRICIOS, 'Sede Parque Patricios'),
        (SEDE_POSTGRADO, 'Sede Postgrado')
    )

    sede = models.PositiveSmallIntegerField(
        verbose_name='sede',
        choices=SEDE_CHOICES,
        default=SEDE_MADERO,
        db_index=True
    )

    class Meta:
        verbose_name = 'Menú'
        verbose_name_plural = 'Menues'
        ordering = ['order']
        permissions = (
            ('save_menu', 'NEW: Can save changes made to the model'),
        )

    def __str__(self):
        return self.name


class MenuDescription(models.Model):
    menu = models.ForeignKey(
        to=Menu,
        verbose_name='menú'
    )
    description = models.TextField(
        verbose_name='descripción',
        max_length=1000,
    )
    for_date = models.DateField(
        verbose_name='para fecha',
        default=date.today,
        db_index=True
    )

    class Meta:
        verbose_name = 'Descripción de Menú'
        verbose_name_plural = 'Descripciones de Menú'
        get_latest_by = "for_date"
        # ordering = ['for_date']
        permissions = (
            ('save_menudescription', 'NEW: Can save changes made to the model'),
        )
        index_together = [
            ['for_date', 'menu']
        ]
        unique_together = [
            ['menu', 'for_date']
        ]

    def __str__(self):
        return "%s para el %s" % (self.menu.name, self.for_date)


class BarProduct(models.Model):
    name = models.CharField(
        verbose_name='nombre',
        max_length=200
    )

    SEDE_MADERO = 1
    SEDE_POSTGRADO = 2
    SEDE_PATRICIOS = 3

    SEDE_CHOICES = (
        (SEDE_MADERO, 'Sede Madero'),
        (SEDE_PATRICIOS, 'Sede Parque Patricios'),
        (SEDE_POSTGRADO, 'Sede Postgrado')
    )

    sede = models.PositiveSmallIntegerField(
        verbose_name='sede',
        choices=SEDE_CHOICES,
        default=SEDE_MADERO
    )
    price = models.DecimalField(
        verbose_name='precio',
        max_digits=8,
        decimal_places=2
    )
    important = models.BooleanField(
        verbose_name='importante',
        default=False,
        db_index=True
    )

    class Meta:
        verbose_name = 'producto del bar'
        verbose_name_plural = 'productos del bar'
        permissions = (
            ('save_barproduct', 'NEW: Can save changes made to the model'),
        )
