
from sqlalchemy.exc import NoResultFound
from src.models import db, Meter, MeterReading, UserValidationLink, Event
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
    df = pd.read_csv(file_path)

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
        radio_number = row['Nr radiowy']
        meter = Meter.query.filter_by(radio_number=radio_number).first()

        if not meter:
            # Jeśli licznik nie istnieje, tworzymy nowy
            meter = Meter(radio_number=radio_number, type='water')
            db.session.add(meter)
            db.session.commit()

        for column in df.columns:
            if "Objętość [m3]" in column:
                month_and_year = column.split()[-2:]  # Ostatnie dwa elementy: "czerwiec 2020"
                month_str, year_str = month_and_year

                month_num = month_mapping.get(month_str.lower())
                if month_num is None:
                    print(f"Nieznany miesiąc: {month_str}")
                    continue

                date = datetime(int(year_str), month_num, 1)
                reading = MeterReading(date=date, reading=row[column], meter_id=meter.id)
                db.session.add(reading)

    db.session.commit()


def get_or_create_meter(session, radio_number):
    try:
        meter = session.query(Meter).filter_by(radio_number=radio_number).one()
        return meter, False  # Zwracamy istniejący licznik i False (nie tworzymy nowego)
    except NoResultFound:
        meter = Meter(radio_number=radio_number, type='heat')
        session.add(meter)
        return meter, True  # Zwracamy nowy licznik i True (tworzymy nowy)

def process_csv_heat(file_path):
    df = pd.read_csv(file_path)

    for index, row in df.iterrows():
        radio_number = row['Nr radiowy']
        if pd.isna(radio_number):
            print("Pominięto wiersz z nieznanym 'Nr radiowy'")
            continue

        meter, created = get_or_create_meter(db.session, int(radio_number))

        db.session.commit()

        if not created:
            # Jeśli licznik istnieje, sprawdzamy datę odczytu
            reading_date_str = row['Data odczytu']
            energy = row['Energia [GJ]']

            if pd.isna(reading_date_str) or pd.isna(energy):
                print(f"Pominięto wiersz z brakującymi danymi: {row}")
                continue

            try:
                reading_date = datetime.strptime(reading_date_str, '%m/%d/%Y %H:%M')
                energy = float(energy)

                existing_reading = MeterReading.query.filter_by(date=reading_date, meter_id=meter.id).first()

                if existing_reading:
                    print(f"Odczyt już występuje w bazie danych {radio_number} on {reading_date_str}")
                else:
                    reading = MeterReading(date=reading_date, reading=energy, meter_id=meter.id)
                    db.session.add(reading)
                    print(f"Dodano odczyt dla licznika {radio_number} on {reading_date_str}")

                db.session.commit()
            except ValueError as e:
                print(f"Błąd w przetwarzaniu wiersza: {row}")
                print(f"Szczegóły błędu: {e}")

    db.session.commit()


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

