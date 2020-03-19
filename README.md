# CEITBA

Proyecto para la administración de la facturación del CEITBA.

    $ virtualenv path-to-env
    $ source path-to-env/bin/activate
    $ pip install -r requirements.txt
    $ pip install -r requirements-dev.txt
    $ ./manage.py migrate
    $ ./manage.py runserver

Comando para ver cuantos certificados validos hay

    SportCertificate.objects.filter(date_emitted__gt=date.today() - datetime.timedelta(days=365))
        .filter(member__enrollment__service__name__exact=config.CEITBA_SERVICE_NAME, member__enrollment__date_removed__isnull=True)
        .count()
