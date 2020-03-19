from django.core.management.base import BaseCommand
from informacion.models import JournalEntry
from datetime import datetime
import csv


class Command(BaseCommand):
    help = 'Imports the students csv file the database.'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='?', type=str)

    def handle(self, *args, **options):
        with open(options['file'], 'r') as csvfile:
            entries = csv.reader(csvfile, delimiter=',')
            num = 0
            for entry in entries:

                db_entry = JournalEntry(id=entry[0])

                date = datetime.strptime(entry[1], "%d/%m/%y")

                if entry[4]:
                    db_entry.date_created = None
                    db_entry.date_paid = date

                if entry[5]:
                    db_entry.date_paid = None
                    db_entry.date_created = date

                db_entry.who = entry[2]
                db_entry.description = entry[3]
                db_entry.amount_in = entry[4] or 0
                db_entry.amount_out = entry[5] or 0

                db_entry.save()
                num += 1
                if num % 100 == 0:
                    self.stdout.write(self.style.NOTICE('Imported %d entries so far' % num))

            self.stdout.write(self.style.SUCCESS('Import finished!\n\tImported %d entries' % num))
