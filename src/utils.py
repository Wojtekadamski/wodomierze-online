import csv
import os

import chardet as chardet
from dateutil.relativedelta import relativedelta
from sqlalchemy.exc import NoResultFound
from src.models import db, Meter, MeterReading, UserValidationLink, Event, Address
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from datetime import datetime
import pandas as pd


def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Nie masz uprawnień do tej strony.', 'danger')
            return redirect(url_for('main_routes.home'))
        return func(*args, **kwargs)

    return decorated_function


def superuser_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (current_user.is_admin or current_user.is_superuser):
            flash('Brak uprawnień do tej strony.', 'danger')
            return redirect(url_for('main_routes.home'))
        return f(*args, **kwargs)

    return decorated_function


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


def is_valid_link(user_link):
    link = UserValidationLink.query.get_or_404(link=user_link)
    if not link or link.is_used:
        return False
    return True


def process_csv_water(file_path):
    # Wykryj kodowanie pliku
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
        file_encoding = result['encoding']

    # Przekonwertuj plik do UTF-8, jeśli nie jest już w tym formacie
    if file_encoding != 'utf-8':
        with open(file_path, 'r', encoding=file_encoding) as file, \
                open(file_path + '_utf8.csv', 'w', encoding='utf-8') as new_file:
            new_file.write(file.read())
        file_path = file_path + '_utf8.csv'

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        if ';' in content:
            # Jeżeli średniki są w zawartości pliku, zamień przecinki na kropki i średniki na przecinki
            content = content.replace(',', '.')
            content = content.replace(';', ',')

            # Zapisz przekształconą zawartość do pliku tymczasowego
            temp_file_path = os.path.splitext(file_path)[0] + '_temp.csv'
            with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
                temp_file.write(content)

            # Odczytaj przekształcony plik CSV
            df = pd.read_csv(temp_file_path, sep=',', encoding='utf-8')
        else:
            # Jeżeli średniki nie występują, załóż, że plik jest już poprawnym plikiem CSV
            df = pd.read_csv(file_path, sep=',', encoding='utf-8')
    except pd.errors.ParserError as e:
        # Handle the error, e.g., by skipping lines with incorrect field counts
        print(f"Error parsing CSV: {e}")
        return "Problem w odczytaniu pliku CSV. Upewniej się, że format pliku jest prawidłowy."

    month_mapping = {
        "styczeń": 1,
        "luty": 2,
        "marzec": 3,
        "kwiecień": 4,
        "maj": 5,
        "czerwiec": 6,
        "lipiec": 7,
        "sierpień": 8,
        "wrzesień": 9,
        "październik": 10,
        "listopad": 11,
        "grudzień": 12
    }

    for index, row in df.iterrows():
        try:
            radio_number = int(row.get('Nr radiowy'))
            print(int(row.get('Nr radiowy')))
            if not pd.isna(radio_number):
                meter = Meter.query.filter_by(radio_number=radio_number).first()

                if not meter:
                    meter = Meter(radio_number=radio_number, type='water')
                    db.session.add(meter)
                    db.session.commit()

                street_value, building_value, apartment_value = None, None, None

                for column in df.columns:
                    if "udynek" in column:
                        street_value = row.get(column)
                    if "latka" in column:
                        building_value = row.get(column)
                    if "okal" in column:
                        apartment_value = row.get(column)

                    if "Objętość [m3]" in column:
                        month_and_year = column.split()[-2:]  # Ostatnie dwa elementy: "czerwiec 2020"

                        month_str, year_str = month_and_year

                        month_num = month_mapping.get(month_str.lower())
                        if month_num is None:
                            return f"Nieznany miesiąc: {month_str}"

                        date = datetime(int(year_str), month_num, 1)
                        reading_value = row.get(column)
                        if not pd.isna(reading_value):
                            reading = MeterReading(date=date, reading=reading_value, meter_id=meter.id)
                            db.session.add(reading)

                    if not meter.address:
                        address = Address(street=street_value, building_number=building_value,
                                          apartment_number=apartment_value)
                        meter.address = address
                        db.session.add(address)
                        db.session.commit()
                    else:
                        # Jeśli miernik ma już przypisany adres, zaktualizuj go
                        address = meter.address
                        address.street = street_value
                        address.building_number = building_value
                        address.apartment_number = apartment_value


        except (ValueError, TypeError) as e:
            return redirect(url_for('main_routes.home'))

    db.session.commit()
    return "Plik wczytany pomyślnie"


def get_or_create_meter(session, radio_number):
    try:
        meter = session.query(Meter).filter_by(radio_number=radio_number).one()
        return meter, False  # Zwracamy istniejący licznik i False (nie tworzymy nowego)
    except NoResultFound:
        meter = Meter(radio_number=radio_number, type='heat')
        session.add(meter)
        return meter, True  # Zwracamy nowy licznik i True (tworzymy nowy)


def process_csv_heat(file_path):
    # Sprawdzenie kodowania pliku
    with open(file_path, 'rb') as file:
        result = chardet.detect(file.read())
        file_encoding = result['encoding']

    try:
        if file_encoding != 'utf-8':
            # Konwersja pliku do UTF-8, jeśli to konieczne
            with open(file_path, 'r', encoding=file_encoding) as file, \
                    open(file_path + '_utf8.csv', 'w', encoding='utf-8') as new_file:
                new_file.write(file.read())
            file_path_utf8 = file_path + '_utf8.csv'
        else:
            file_path_utf8 = file_path

        with open(file_path_utf8, 'r') as file:
            content = file.read()

        if ';' in content:
            # Zamiana separatorów
            content = content.replace(',', '.').replace(';', ',')
            temp_file_path = os.path.splitext(file_path_utf8)[0] + '_temp.csv'
            with open(temp_file_path, 'w', encoding='utf-8') as temp_file:
                temp_file.write(content)
            df = pd.read_csv(temp_file_path, sep=',', encoding='utf-8')
        else:
            df = pd.read_csv(file_path_utf8, sep=',', encoding='utf-8')

    except pd.errors.ParserError as e:
        print(f"Error parsing CSV: {e}")
        return "Problem w odczytaniu pliku CSV. Upewniej się, że format pliku jest prawidłowy."

    for index, row in df.iterrows():
        try:
            radio_number = int(row.get('Nr radiowy'))
            if not pd.isna(radio_number):
                meter = Meter.query.filter_by(radio_number=radio_number).first()

                if not meter:
                    meter = Meter(radio_number=radio_number, type='heat')
                    db.session.add(meter)
                    db.session.commit()

                street_value, building_value, apartment_value = None, None, None

                for column in df.columns:
                    if "Budynek" in column:
                        building_value = row.get(column)
                    if "Klatka" in column:
                        street_value = row.get(column)
                    if "Lokal" in column:
                        apartment_value = row.get(column)

                    if "Energia [GJ]" in column:
                        date_str = row.get("Data odczytu")
                        if date_str:
                            date = datetime.strptime(date_str, "%m/%d/%Y %H:%M")
                        else:
                            return f"Brak daty odczytu w wierszu {index + 1}."

                        reading_value = row.get(column)
                        if not pd.isna(reading_value):
                            reading = MeterReading(date=date, reading=reading_value, meter_id=meter.id)
                            db.session.add(reading)

                    if not meter.address:
                        address = Address(street=street_value, building_number=building_value,
                                          apartment_number=apartment_value)
                        meter.address = address
                        db.session.add(address)
                    else:
                        address = meter.address
                        address.street = street_value
                        address.building_number = building_value
                        address.apartment_number = apartment_value
        except (ValueError, TypeError) as e:
            return f"Problem w odczytaniu wiersza {index + 1}: {e}"

    db.session.commit()
    return "Plik wczytany pomyślnie"


def process_csv_events(file_path, type):
    df = pd.read_csv(file_path)
    for index, row in df.iterrows():
        radio_number = row['Nr radiowy']
        if pd.isna(radio_number):
            continue
        meter = Meter.query.filter_by(radio_number=radio_number).first()

        if not meter:
            # Tworzymy nowy licznik
            meter = Meter(radio_number=radio_number, type=type)
            db.session.add(meter)
            db.session.commit()

        # Przetwarzanie kolumn i dodawanie zdarzeń do licznika
        event_type = row['Typ alarmu']
        reading_time = datetime.datetime.strptime(row['Data i godzina odczytu'], '%m/%d/%Y %H:%M')
        value = row['Wartość']
        first_occurrence = datetime.datetime.strptime(row['Pierwsze wystąpienie'], '%m/%d/%Y %H:%M')
        last_occurrence = datetime.datetime.strptime(row['Ostatnie wystąpienie'], '%m/%d/%Y %H:%M')
        number_of_occurrences = int(row['Liczba wystąpień'])
        is_active = row['Aktywny'] == 'True'
        duration = row['Czas trwania']

        event = Event(
            device_type='events',
            event_type=event_type,
            reading_time=reading_time,
            value=value,
            first_occurrence=first_occurrence,
            last_occurrence=last_occurrence,
            meter_id=meter.id,
            number_of_occurrences=number_of_occurrences,
            is_active=is_active,
            duration=duration
        )
        db.session.add(event)

    db.session.commit()


from datetime import datetime, timedelta


# def create_report_data(selected_meters, report_period):
#     end_date = datetime.now()
#     start_date = end_date - relativedelta(months=report_period)
#     print(start_date, end_date)
#     report_data = []
#     for meter_radio_number in selected_meters:
#         meter = Meter.query.filter_by(radio_number=meter_radio_number).first()
#         if meter:
#             readings = MeterReading.query.filter(
#                 MeterReading.meter_id == meter.id,
#                 MeterReading.date >= start_date,
#
#                 MeterReading.date <= end_date
#             ).all()
#             print(meter.readings)
#
#             if not readings:
#                 report_data.append({
#                     'user_email': meter.user.email if meter.user else 'N/A',
#                     'meter_number': meter.radio_number,
#                     'meter_type': meter.type,
#                     'reading': 'Brak odczytów',
#                     'reading_date': 'N/A'
#                 })
#             else:
#                 for reading in readings:
#                     report_data.append({
#                         'user_email': meter.user.email if meter.user else 'N/A',
#                         'meter_number': meter.radio_number,
#                         'meter_type': meter.type,
#                         'reading': reading.reading,
#                         'reading_date': reading.date.strftime('%Y-%m-%d')
#                     })
#
#     return report_data


def create_report_data(selected_meters, report_period):
    end_date = datetime.now().replace(day=1) - relativedelta(days=1)
    start_date = end_date - relativedelta(months=report_period)

    report_data = []
    for meter_radio_number in selected_meters:
        meter = Meter.query.filter_by(radio_number=meter_radio_number).first()
        if meter:
            # Tworzenie reprezentacji adresu jako ciągu znaków
            if meter.address:
                address_parts = [
                    meter.address.street,
                    meter.address.building_number,
                    meter.address.apartment_number
                ]
                address_str = ', '.join(filter(None, address_parts))
            else:
                address_str = 'N/A'

            meter_data = {
                'user_email': meter.user.email if meter.user else 'N/A',
                'meter_number': meter.radio_number,
                'meter_type': meter.type,
                'meter_address': address_str,  # Użyj utworzonego ciągu adresu
            }

            # Dodajemy kolumny dla każdego miesiąca
            for month in range(report_period):
                month_date = end_date - relativedelta(months=month)
                month_name = month_date.strftime('%B %Y')
                meter_data[month_name] = 'Brak odczytów'

                # Znajdź odczyt dla danego miesiąca
                reading = MeterReading.query.filter(
                    MeterReading.meter_id == meter.id,
                    MeterReading.date >= month_date - relativedelta(months=1),
                    MeterReading.date < month_date
                ).order_by(MeterReading.date.desc()).first()  # Pobierz najnowszy odczyt w miesiącu

                if reading:
                    meter_data[month_name] = reading.reading

            report_data.append(meter_data)

    return report_data
