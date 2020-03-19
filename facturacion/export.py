from datetime import date
from io import BytesIO

import xlsxwriter
from django.db.models import Subquery
from xlsxwriter.worksheet import Worksheet

from facturacion.models import *
from informacion.models import YMCAFamilyMember
from lockers.models import LockerAssignation, LockerSite

logger = logging.getLogger(__name__)


class XlsxTable:
    def __init__(self, worksheet: Worksheet, headers=None, header_format=None):
        if headers is None:
            raise Exception("Invalid headers. List expected!")

        if worksheet is None:
            raise Exception("Invalid worksheet")

        self._headers = headers

        self._header_length = [len(header) for header in headers]

        self._worksheet = worksheet

        for i, header in enumerate(headers):
            if header_format is not None:
            	worksheet.write(0, i, header, header_format)
            else:
                worksheet.write(0, i, header)

        self._next_row = 1

    def add_row(self, items=None):
        if items is None or len(items) != len(self._headers):
            raise Exception('Expected %d items' % len(self._headers))

        for i, col in enumerate(items):
            self._worksheet.write(self._next_row, i, col)

            col_length = len(str(col))

            if col_length > self._header_length[i]:
                self._header_length[i] = col_length

        self._next_row += 1

    def add_raw_row(self, *args):

        for i, col in enumerate(args):
            self._worksheet.write(self._next_row, i, col)

        self._next_row += 1

    def close(self):

        for i, col_length in enumerate(self._header_length):
            if self._worksheet.set_column(i, i, col_length + 1) != 0:
                raise Exception()


def write_charges(worksheet, for_student_type):
    ceitba_service = Service.objects.filter(name__exact=config.CEITBA_SERVICE_NAME).get()
    ymca_service = Service.objects.filter(name__exact=config.YMCA_SERVICE_NAME).get()

    enrollments_subtotal = Enrollment.objects.filter(
        student=OuterRef('pk'),
        date_removed__isnull=True,
        student__type__in=for_student_type
    ).exclude(
        service__in=[ceitba_service, ymca_service]
    ).values('student').annotate(
        subtotal=Coalesce(Sum('service__price', output_field=DecimalField(max_digits=8, decimal_places=2)), 0)
    ).values('subtotal')

    purchases_subtotal = Purchase.objects.filter(
        student=OuterRef('pk'),
        reported_in__isnull=True,
        student__type__in=for_student_type,
        billable=True
    ).values('student').annotate(
        subtotal=Coalesce(Sum(
            F('purchaseitem__product__price') * F('purchaseitem__quantity'),
            output_field=DecimalField(max_digits=8, decimal_places=2)
        ), 0)
    ).values('subtotal')

    special_purchases_subtotal = SpecialPurchase.objects.filter(
        member=OuterRef('pk'),
        reported_in__isnull=True,
        member__type__in=for_student_type,
        billable=True
    ).values('member').annotate(
        subtotal=Coalesce(Sum(
            F('amount') * F('quantity'),
            output_field=DecimalField(max_digits=8, decimal_places=2)
        ), 0)
    ).values('subtotal')

    students = Student.objects.filter(type__in=for_student_type).order_by('student_id').annotate(
        enrollments_subtotal=Coalesce(
            Subquery(enrollments_subtotal, output_field=DecimalField(max_digits=8, decimal_places=2)), 0)
    ).annotate(
        purchases_subtotal=Coalesce(
            Subquery(purchases_subtotal, output_field=DecimalField(max_digits=8, decimal_places=2)), 0)
    ).annotate(
        special_purchases_subtotal=Coalesce(
            Subquery(special_purchases_subtotal, output_field=DecimalField(max_digits=8, decimal_places=2)), 0)
    )

    table = XlsxTable(worksheet=worksheet, headers=['Legajo', 'Nombre', 'Monto'])

    for student in students.iterator():

        # enrollments_subtotal = student.enrollment_set.exclude(
        #     service__in=[ceitba_service, ymca_service]
        # ).filter(
        #     date_removed__isnull=True,
        #     student__type__in=for_student_type
        # ).aggregate(
        #     subtotal=Coalesce(Sum('service__price'), 0)
        # )['subtotal']

        # purchases = student.purchase_set.filter(
        #     reported_in__isnull=True,
        #     student__type__in=for_student_type,
        #     billable=True
        # )

        # purchases_subtotal = purchases.aggregate(
        #     subtotal=Coalesce(Sum(
        #         F('purchaseitem__product__price') * F('purchaseitem__quantity'),
        #         output_field=DecimalField(max_digits=8, decimal_places=2)
        #     ), 0)
        # )['subtotal']

        # purchases_subtotal += student.specialpurchase_set.filter(
        #     reported_in__isnull=True,
        #     member__type__in=for_student_type,
        #     billable=True
        # ).aggregate(
        #     subtotal=Coalesce(Sum(
        #         F('amount') * F('quantity'),
        #         output_field=DecimalField(max_digits=8, decimal_places=2)
        #     ), 0)
        # )['subtotal']

        # total = enrollments_subtotal + purchases_subtotal
        total = student.enrollments_subtotal + student.purchases_subtotal + student.special_purchases_subtotal

        if total > 0:
            table.add_row(items=[student.student_id, student.name, total])

    table.close()


def write_enrollments(worksheet, for_student_type):
    rows = Enrollment.active.filter(
        reported_in__isnull=True,
        service__name=config.CEITBA_SERVICE_NAME,
        student__type__in=for_student_type
    ).select_related('student', 'service').order_by('student__student_id')

    table = XlsxTable(worksheet=worksheet, headers=['Legajo', 'Nombre'])

    for row in rows.iterator():
        table.add_row(items=[row.student.student_id, row.student.name])

    table.close()


def write_unenrollments(worksheet, for_student_type):
    rows = Enrollment.objects.filter(
        date_removed__isnull=False,
        reported_in__isnull=False,
        reported_in2__isnull=True,
        service__name=config.CEITBA_SERVICE_NAME,
        student__type__in=for_student_type
    ).select_related('student', 'service').order_by('student__student_id')

    table = XlsxTable(worksheet=worksheet, headers=['Legajo', 'Nombre'])

    for row in rows.iterator():
        table.add_row(items=[row.student.student_id, row.student.name])

    table.close()


def write_ymca(worksheet, for_student_type):
    rows = Enrollment.active.filter(
        service__name=config.YMCA_SERVICE_NAME,
        student__type__in=for_student_type
    ).select_related('student', 'service').order_by('student__student_id')

    table = XlsxTable(worksheet=worksheet, headers=['Legajo', 'Nombre', 'Monto'])

    for row in rows.iterator():
        table.add_row(items=[row.student.student_id, row.student.name, row.service.price])

    table.close()


def write_reimbursements(worksheet, for_student_type):
    rows = Reimbursement.objects.filter(
        reported_in__isnull=True,
        student__type__in=for_student_type
    ).select_related('student').order_by('student__student_id')

    table = XlsxTable(worksheet=worksheet, headers=['Legajo', 'Nombre', 'Monto'])

    for row in rows.iterator():
        table.add_row(items=[row.student.student_id, row.student.name, row.amount])

    table.close()


MODELS = (('Debitos', write_charges),
          ('YMCA', write_ymca),
          ('Altas', write_enrollments),
          ('Bajas', write_unenrollments),
          ('Reembolsos', write_reimbursements)
          )


def generate_spreadsheet(for_student_type=None):
    if for_student_type is None:
        for_student_type = []

    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)

    for name, func in MODELS:
        worksheet = workbook.add_worksheet(name)
        func(worksheet, for_student_type)

    workbook.close()

    return output


def exportar_altas_y_bajas(service, start, end):
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)

    # Solapa altas

    worksheet_altas = workbook.add_worksheet('Altas')

    rows_altas = Enrollment.active.filter(
        service__name=service,
        date_created__range=[start, end],
        date_removed__isnull=True,
    ).order_by('student__student_id')

    table_altas = XlsxTable(worksheet=worksheet_altas, headers=['Legajo', 'Nombre', 'Fecha Alta'])

    for row in rows_altas.iterator():
        table_altas.add_row(items=[row.student.student_id, row.student.name, row.date_created.isoformat()])

    table_altas.close()

    # Solapa bajas

    worksheet_bajas = workbook.add_worksheet('Bajas')

    rows_bajas = Enrollment.objects.filter(
        service__name=service,
        date_removed__isnull=False,
        date_removed__range=[start, end],
    ).order_by('student__student_id')

    table_bajas = XlsxTable(worksheet=worksheet_bajas, headers=['Legajo', 'Nombre', 'Fecha Baja'])

    for row in rows_bajas.iterator():
        table_bajas.add_row(items=[row.student.student_id, row.student.name, row.date_removed.isoformat()])

    table_bajas.close()

    # Jarcodeado, porque no?
    if service == config.YMCA_SERVICE_NAME:
        # Solapa plan familiar

        worksheet_plan_familiar = workbook.add_worksheet('Planes Familiares')

        rows_plan_familiar = YMCAFamilyMember.objects.order_by('enrollment__student__student_id')

        table_plan_familiar = XlsxTable(worksheet=worksheet_plan_familiar, headers=['Legajo', 'Nombre', 'Familiar'])

        for row in rows_plan_familiar.iterator():
            for member in row.family_members.split('\r\n'):
                table_plan_familiar.add_row(
                    items=[row.enrollment.student.student_id, row.enrollment.student.name, member])

        table_plan_familiar.close()

    workbook.close()

    return output


def generate_totals(for_student_type=Student.STAFF):
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)

    bold = workbook.add_format({'bold': True})

    worksheet = workbook.add_worksheet("Totales")

    students = Student.objects.filter(type=for_student_type).order_by('student_id')

    table = XlsxTable(worksheet=worksheet, headers=[
            'Usuario',
            'DNI del Empleado',
            'Nombre del Empleado',
            'Nombre del Concepto',
            'Periodicidad',
            'Fecha movimiento',
            'Periodo inicio',
            'Periodo final',
            'Cantidad',
            'Valor $',
            'Centro de Costo'
        ], header_format=bold)

    today = date.today()

    for student in students.iterator():

        enrollments_subtotal = student.enrollment_set.filter(
            date_removed__isnull=True,
            student__type=for_student_type,
            billable=True,
        ).aggregate(
            subtotal=Coalesce(Sum('service__price'), 0)
        )['subtotal']

        purchases = student.purchase_set.filter(
            reported_in__isnull=True,
            student__type=for_student_type,
            billable=True
        )

        purchases_subtotal = purchases.aggregate(
            subtotal=Coalesce(Sum(
                F('purchaseitem__product__price') * F('purchaseitem__quantity'),
                output_field=DecimalField(max_digits=8, decimal_places=2)
            ), 0)
        )['subtotal']

        purchases_subtotal += student.specialpurchase_set.filter(
            reported_in__isnull=True,
            member__type=for_student_type,
            billable=True
        ).aggregate(
            subtotal=Coalesce(Sum(
                F('amount') * F('quantity'),
                output_field=DecimalField(max_digits=8, decimal_places=2)
            ), 0)
        )['subtotal']

        total = enrollments_subtotal + purchases_subtotal

        if total > 0:
            table.add_row(items=[
                    'ceitba',
                    student.dni,
                    student.name,
                    '2211 CUOTA CEITBA',
                    'U',
                    str(today),
                    "%s/%s" % (today.year, today.month),
                    "%s/%s" % (today.year, today.month),
                    '0',
                    total,
                    ''
                ])

    table.close()

    worksheet2 = workbook.add_worksheet("Reintegros")
    write_reimbursements(worksheet2, Student.STAFF)

    workbook.close()

    return output


def export_service(service):
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)

    enrollments = Enrollment.active.filter(
        service=service,
        billable=True
    ).select_related('student', 'service').order_by('student__student_id')
    _export_service(enrollments, workbook, "Facturados")

    enrollments = Enrollment.active.filter(
        service=service,
        billable=False
    ).select_related('student', 'service').order_by('student__student_id')
    _export_service(enrollments, workbook, "Efectivo")

    workbook.close()

    return output


def export_event(event):
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)

    worksheet = workbook.add_worksheet('Inscriptos a evento')

    table = XlsxTable(worksheet=worksheet,
                      headers=['Legajo', 'Nombre', 'Email', 'Fecha Inscripción', 'Informacion Extra'])

    for row in event.eventinscription_set.order_by('extra_info').iterator():
        table.add_row(
            items=[row.member.student_id, row.member.name, row.member.email, str(row.date_created), row.extra_info])

    table.close()

    workbook.close()

    return output


def _export_service(enrollments, workbook, worksheet_name):
    worksheet = workbook.add_worksheet(worksheet_name)

    table = XlsxTable(worksheet=worksheet, headers=['Legajo', 'Nombre', 'Email', 'Monto'])

    for row in enrollments.iterator():
        table.add_row(items=[row.student.student_id, row.student.name, row.student.email, row.service.price])

    table.close()


def export_lockersite(lockersite: LockerSite):
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)

    assignations = LockerAssignation.objects.filter(
        enrollment__service__lockersite=lockersite
    ).order_by('locker_id')

    _export_lockersite(assignations, lockersite, workbook, lockersite.service.name)

    workbook.close()

    return output


def _export_lockersite(assignations, lockersite: LockerSite, workbook, worksheet_name):
    worksheet = workbook.add_worksheet(worksheet_name)

    worksheet.write(0, 0, '# Locker')
    worksheet.write(0, 1, 'Estado')
    worksheet.write(0, 2, 'Legajo')
    worksheet.write(0, 3, 'Nombre')

    col1 = len('Nombre')

    r = 1

    for i in range(1, lockersite.count + 1):
        worksheet.write(r, 0, i)
        worksheet.write(r, 1, "Libre")

        r += 1

    for row in assignations.iterator():
        worksheet.write(row.locker_id, 1, "Ocupado")
        worksheet.write(row.locker_id, 2, row.enrollment.student.student_id)
        worksheet.write(row.locker_id, 3, row.enrollment.student.name)

        if len(row.enrollment.student.name) > col1:
            col1 = len(row.enrollment.student.name)

    worksheet.set_column(3, 3, col1 + 1)


def export_accounting_data():
    output = BytesIO()

    workbook = xlsxwriter.Workbook(output)

    # Reporte de Servicios
    worksheet = workbook.add_worksheet('Reporte Servicios')

    worksheet.write(0, 0, date.today().month)

    table = XlsxTable(worksheet=worksheet, headers=[])

    table.add_raw_row("Socios Activos", Student.active.count())

    for service in Service.active.all():
        inscriptos = Enrollment.active.filter(service=service).count()
        cuota = service.price

        table.add_raw_row("%s Inscriptos" % service.name, inscriptos)
        table.add_raw_row("%s Cuota" % service.name, cuota)
        table.add_raw_row("%s Ingreso" % service.name, inscriptos * cuota)

        table.add_raw_row()

    # Reporte de Productos

    worksheet = workbook.add_worksheet('Reporte Productos')

    table = XlsxTable(worksheet=worksheet, headers=[])

    for product in Product.active.all():
        price = product.price
        compras = PurchaseItem.objects.filter(
            product=product,
            purchase__reported_in__isnull=True
        ).aggregate(Sum('quantity'))['quantity__sum'] or 0

        table.add_raw_row("%s Compras" % product.name, compras)
        table.add_raw_row("%s Precio" % product.name, price)
        table.add_raw_row("%s Ingreso" % product.name, compras * price)

        table.add_raw_row()

    workbook.close()

    return output
