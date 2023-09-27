import csv
import os

import chardet as chardet
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


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'csv'


def is_valid_link(user_link):
    link = UserValidationLink.query.get_or_404(link=user_link)
    if not link or link.is_used:
        return False
    return True


def process_csv_water(file_path):
    try:
        with open(file_path, 'r') as file:
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
    try:
        with open(file_path, 'r') as file:
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

    for index, row in df.iterrows():
        try:
            radio_number = int(row.get('Nr radiowy'))
            if not pd.isna(radio_number):
                meter = Meter.query.filter_by(radio_number=radio_number).first()

                if not meter:
                    meter = Meter(radio_number=radio_number, type='heat')
                    db.session.add(meter)
                    db.session.commit()

                # Przypisz adres tylko jeśli masz odpowiednie dane
                street_value, building_value, apartment_value = None, None, None

                for column in df.columns:
                    if "Budynek" in row:
                        building_value = row.get(column)
                    if "Klatka" in row:
                        street_value = row.get(column)
                    if "Lokal" in row:
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
