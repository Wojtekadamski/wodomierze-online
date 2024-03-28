import calendar
import csv
import os
import random

import chardet as chardet
from dateutil.relativedelta import relativedelta
from sqlalchemy import extract, func
from sqlalchemy.exc import NoResultFound
from src.models import db, Meter, MeterReading, UserValidationLink, Event, Address, UserReportMonth
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
            radio_number = str(row.get('Nr radiowy'))
            if not pd.isnull(radio_number):
                meter = Meter.query.filter_by(radio_number=radio_number).first()

                if not meter:
                    meter = Meter(radio_number=radio_number, type='water')
                    db.session.add(meter)
                    db.session.commit()

                device_number = str(row.get('Nr wodomierza', None))  # Zakładamy, że kolumna nazywa się "Uwagi"
                if pd.isnull(device_number):
                    device_number = str(row.get('Uwagi', None))
                if pd.isnull(device_number):
                    device_number = None  # lub użyj domyślnej wartości, np. ""
                if device_number:
                    meter.device_number = device_number

                street_value, building_value, apartment_value = None, None, None

                current_year = datetime.now().year
                current_month = datetime.now().month
                current_day = datetime.now().day

                for column in df.columns:
                    if "udynek" in column:
                        street_value = row.get(column)
                    if "latka" in column:
                        building_value = row.get(column)
                    apartment_value = row.get('Lokal', None)

                    if "Objętość [m3]" in column:
                        month_and_year = column.split()[-2:]  # Ostatnie dwa elementy: "czerwiec 2020"

                        month_str, year_str = month_and_year

                        month_num = month_mapping.get(month_str.lower())
                        if month_num is None:
                            return f"Nieznany miesiąc: {month_str}"

                            # Sprawdź, czy odczyt jest z obecnego miesiąca i roku
                        if month_num == current_month and int(year_str) == current_year:
                            # Ustaw dzień odczytu na obecny dzień
                            date = datetime(int(year_str), month_num, current_day)
                        else:
                            # Ustaw dzień odczytu na ostatni dzień miesiąca
                            last_day_of_month = calendar.monthrange(int(year_str), month_num)[1]
                            date = datetime(int(year_str), month_num, last_day_of_month)
                        reading_value = row.get(column)
                        if not pd.isna(reading_value):
                            # Sprawdź, czy pomiar już istnieje
                            existing_reading = MeterReading.query.filter(
                                MeterReading.meter_id == meter.id,
                                extract('year', MeterReading.date) == int(year_str),
                                extract('month', MeterReading.date) == month_num
                            ).first()

                            if existing_reading:
                                # Aktualizuj istniejący pomiar
                                existing_reading.reading = reading_value
                                existing_reading.date = date
                            else:
                                # Dodaj nowy pomiar
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
            radio_number = row.get('Nr radiowy')
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
                    apartment_value = row.get('Lokal', None)

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


def create_report_data(selected_meters, report_period):
    end_date = datetime.now().replace(day=1) - relativedelta(days=1)
    start_date = end_date - relativedelta(months=report_period)

    report_data = []
    for meter_radio_number in selected_meters:
        meter = Meter.query.filter_by(radio_number=meter_radio_number).first()
        if meter and meter.user:

            allowed_months = [rm.month for rm in meter.user.report_months]


            if meter.address:
                address_parts = [
                    meter.address.street,
                    meter.address.building_number,
                    meter.address.apartment_number
                ]
                address_str = ', '.join(filter(None, address_parts))
            else:
                address_str = 'N/A'

            if meter.type == 'water':
                meter_type = 'wodomierz'
            else:
                meter_type = meter.type

            if meter.device_number:
                device_number=meter.device_number
            else:
                device_number='N/A'

            meter_data = {
                'user_email': meter.user.email if meter.user else 'N/A',
                'meter_number': meter.radio_number,
                'device_number': device_number,
                'meter_type': meter_type,
                'meter_address': address_str,  # Użyj utworzonego ciągu adresu
            }

            # Dodajemy kolumny dla każdego miesiąca
            for month in range(report_period):
                month_date = end_date - relativedelta(months=month)
                if month_date.month in allowed_months:
                    month_name = month_date.strftime('%B %Y')
                    meter_data[month_name] = ''

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


def generate_random_password():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(random.choice(chars) for _ in range(8))


def remove_duplicate_readings():
    meters = Meter.query.all()
    total_removed_duplicates = 0
    for meter in meters:
        # Pobierz odczyty i zgrupuj je po roku i miesiącu
        readings_by_month = db.session.query(
            extract('year', MeterReading.date).label('year'),
            extract('month', MeterReading.date).label('month'),
            func.max(MeterReading.reading).label('max_reading'),
            func.count(MeterReading.id).label('count')
        ).filter_by(meter_id=meter.id).group_by(
            extract('year', MeterReading.date),
            extract('month', MeterReading.date)
        ).having(func.count(MeterReading.id) > 1).all()

        # Dla każdej grupy z duplikatami
        for year, month, max_reading, count in readings_by_month:
            # Znajdź wszystkie odczyty w danej grupie
            readings = MeterReading.query.filter(
                MeterReading.meter_id == meter.id,
                extract('year', MeterReading.date) == year,
                extract('month', MeterReading.date) == month
            ).order_by(MeterReading.reading.desc()).all()

            # Usuń wszystkie odczyty oprócz tego z największą wartością
            for reading in readings[1:]:  # Pomijamy pierwszy odczyt, bo jest to ten z największą wartością
                db.session.delete(reading)
                total_removed_duplicates += 1

    db.session.commit()
    return total_removed_duplicates


def update_user_report_months(user_id, selected_months):
    # Usunięcie istniejących rekordów
    UserReportMonth.query.filter_by(user_id=user_id).delete()

    # Dodanie nowych rekordów dla zaznaczonych miesięcy
    for month in selected_months:
        new_month = UserReportMonth(user_id=user_id, month=month)
        db.session.add(new_month)

    db.session.commit()


# def fetch_data_from_db(start_date, end_date):
#     # Użyj konfiguracji połączenia z aplikacji Flask
#     connection_url = current_app.config['SQLALCHEMY_BINDS']['emitel_db']
#
#     query = f"""
#     SELECT m.DeviceEui, r.PayloadDate AS 'Data odczytu', r.ReadingValue1 AS 'Odczyt'
#     FROM emitel.Meters m
#     JOIN emitel.Readings r ON m.Id = r.MeterId
#     WHERE Type = 1 AND PayloadDate BETWEEN '{start_date} 00:00:00' AND '{end_date} 23:59:59'
#     ORDER BY m.DeviceEui, PayloadDate
#     """
#
#     engine = create_engine(connection_url)
#     data = pd.read_sql_query(query, engine)
#     print("sukces")
#     return data
#
#
# def check_and_email_meters():
#     # Przykładowa lista wszystkich numerów liczników
#     all_meters = ["0a640f1e837e2e71",
# "0f2b5549d32e7883",
# "226dc99eb72e932e",
# "438d50ae4c514bdf",
# "5005f04b603f4042",
# "52eb7932b654b6a8",
# "5d807c297dc53e66",
# "60bc4d5ef53efb1c",
# "6101bc313f439b2f",
# "6b6b15401096b3d4",
# "86322af7630aa5fd",
# "8b5f1386c5c361aa",
# "8d506dad5e28882f",
# "8e471ea668225eec",
# "989b7a62bffd1680",
# "a60fa717a75acb6d",
# "c4230443f36fb37a",
# "dd0a01f759f08904",
# "e20f730d59484ebe",
# "e636791287f0ba5a",
# "e7d7c33fba50b8d8",
# "eb370e5d72b78529",
# "ef722ec5f98e0f6c",
# "ef7387cf2a9e6f89",
# "fcbb14f41687168a"
# ]  # Uzupełnij tę listę
#
#     # Pobierz dane za ostatnie 2 i 3 dni
#     today = datetime.now()
#     data_2_days = fetch_data_from_db((today - timedelta(days=2)).strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
#     data_3_days = fetch_data_from_db((today - timedelta(days=3)).strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d'))
#
#     # Znajdź unikalne numery liczników, które się odezwały
#     meters_2_days = set(data_2_days['DeviceEui'].unique())
#     meters_3_days = set(data_3_days['DeviceEui'].unique())
#
#     # Znajdź liczniki, które się nie odezwały
#     missing_meters_2_days = set(all_meters) - meters_2_days
#     missing_meters_3_days = set(all_meters) - meters_3_days
#
#     # Przygotuj treść e-maila
#     email_body = f"Liczba unikalnych liczników, które odezwały się w ciągu ostatnich 2 dni: {len(meters_2_days)}\n"
#     email_body += f"Liczba unikalnych liczników, które odezwały się w ciągu ostatnich 3 dni: {len(meters_3_days)}\n\n"
#     email_body += "Liczniki, które nie odezwały się w ciągu ostatnich 2 dni:\n" + ", ".join(missing_meters_2_days) + "\n\n"
#     email_body += "Liczniki, które nie odezwały się w ciągu ostatnich 3 dni:\n" + ", ".join(missing_meters_3_days)
#
#     print(email_body)
#     # Wysyłanie e-maila (użyj funkcji send_email zdefiniowanej wcześniej)
#     success = send_email("wwadamski@gmail.com", f"Podsumowanie wodomierzy na dzień {today}", email_body)
#     if success:
#         return True
#     else:
#         return False
#
#
#
# def send_email(to_address, subject, body):
#
#
#     # Dane serwera SMTP
#     smtp_server = "smtp-mail.outlook.com"
#     smtp_port = 587
#     smtp_user = "wojciech.adamski@smartbits.pl"
#     smtp_password = os.environ.get('EMAIL_PASS')
#     print(smtp_password)
#
#     # Tworzenie wiadomości
#     msg = MIMEText(body)
#     msg["Subject"] = subject
#     msg["From"] = smtp_user
#     msg["To"] = to_address
#
#     # Logowanie do serwera i wysyłanie
#     try:
#         server = smtplib.SMTP(smtp_server, smtp_port)
#         server.starttls()
#         server.login(smtp_user, smtp_password)
#         server.sendmail(smtp_user, to_address, msg.as_string())
#         print("E-mail wysłany pomyślnie.")
#     except Exception as e:
#         print(f"Wystąpił błąd: {e}")
#     finally:
#         server.quit()
#
#     return True