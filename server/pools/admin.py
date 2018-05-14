import csv
import io
import sys

from django.contrib import admin

from .forms import MultiplePool, MultiplePoolForm
from .models import Pool, Reservation


class MultiplePoolAdmin(admin.ModelAdmin):
    form = MultiplePoolForm

    def save_model(self, request, obj, form, change):
        if change or request.FILES is None:
            super(MultiplePoolAdmin, self).save_model(request, obj, form, change)
        else:
            print(request.FILES)
            self.save(request.FILES['pool_data_file'])

    def save(self, file):
        content = io.StringIO(file.read().decode('utf-8'))
        reader = csv.reader(content, delimiter=',')
        next(reader)
        pools = [self.process_row(row) for row in reader]
        to_add = []
        try:
            for pool in pools:
                p = Pool(pool_id=pool[0], displayName=pool[1], maximumCount=pool[2], enabled=pool[3],
                         description=pool[4])
                to_add.append(p)
        except Exception:
            print("Incorrect pools description", file=sys.stderr)
        Pool.objects.all().delete()
        for p in to_add:
            p.save()

    @staticmethod
    def process_row(row):
        for i in range(len(row)):
            row[i] = row[i].replace('\n', ' ')
        row[2] = int(row[2])
        row[3] = True if row[3] == "true" else False
        return tuple(row)


# Register your models here.
admin.site.register(Pool)
admin.site.register(MultiplePool, MultiplePoolAdmin)
admin.site.register(Reservation)
