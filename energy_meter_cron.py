from datetime import datetime, timezone
import sqlite3
import subprocess
import logging
from dotenv import dotenv_values

config = dotenv_values(".env")

local_db_path=config.get('local_db_path')
remote_db_path=config.get('remote_db_path')
local_logging_path=config.get('local_logging_path')


logging.basicConfig(filename=local_logging_path, level=logging.DEBUG, 
                    format='[%(levelname)s] %(asctime)s - %(message)s')

# List of public holidays in Poland besides weekends
holidays = ['2023-11-01', '2023-11-11', '2023-12-25', '2023-12-26', 
            '2024-01-01', '2024-01-06', '2024-04-01', '2024-05-01', 
            '2024-05-03', '2024-05-30', '2024-08-15', '2024-11-01', 
            '2024-11-11', '2024-12-25', '2024-12-26', '2025-01-01', 
            '2025-01-06', '2025-04-21', '2025-05-01', '2025-06-19',
            '2025-08-15', '2025-11-11', '2025-12-25', '2025-12-26']


# Function for setting a proper tariff (G12w) based on date and time
def set_tariff(date_time):
    if date_time.weekday() > 4:
        return 'night'
    elif date_time.date().strftime('%Y-%m-%d') in holidays:
        return 'night'
    elif date_time.hour >= 22 or date_time.hour < 6:
        return 'night'
    elif date_time.hour >= 13 and date_time.hour < 15:
        return 'night'
    else:
        return 'day'


def get_data():
    
    logging.info("iNode BT sensor - getting data...")
    try:
        output = subprocess.run(['sudo', 'bash' ,'scan_bt.sh'], capture_output=True)
            
        # decoding output from byte to string format
        output = output.stdout.decode().split()
        data = {'imp_total':int(output[0]), 'imp_minute':int(output[1])}
        
        logging.info(f"Data received from the iNode BT sensor: {data}")
        # returning total number of impulses and impulse number from last 1 minute
        return data
    
    except subprocess.SubprocessError as e:
        logging.error(f"Error getting data from the iNonde: {e}")


def transform(data: dict):
    total = data['imp_total']
    minute = data['imp_minute']

    energy_const = 2500    # adjust energy meter's constant here (number of impulses per 1 kWh)
    current_time = datetime.now()
    utc_now = datetime.now(timezone.utc)

    date_time = utc_now.strftime('%Y-%m-%dT%H:%M:%S')
    total_power = total / energy_const
    power_delta = minute / energy_const * 1000 * 60
    imp_total = total
    imp_minute = minute
    year = current_time.year
    month = current_time.month
    day = current_time.day
    time = current_time.strftime('%H:%M')
    tariff = set_tariff(current_time)

    return date_time, total_power, power_delta, imp_total, imp_minute, year, month, day, time, tariff


def load(data_to_sqlite: tuple, path_to_db: str):
    try:
        conn = sqlite3.connect(path_to_db)
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO energy_meter
        (date_time, total_power, power_delta, imp_total, imp_minute, year, month, day, time, tariff)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data_to_sqlite)

        conn.commit()
        conn.close()

        logging.info(f"Data added to database: {data_to_sqlite}")

    except sqlite3.Error as e:
        
        logging.error(f'Error inserting data into database: {e}')


# Besides storing the data in the local sqlite db that function synchronizes local db with the one located on my homelab
def rsync():

    try:
        # Construct the rsync command
        command_db = f"rsync -avz {local_db_path} {remote_db_path}"
        result_db = subprocess.run(command_db, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Log the success and details
        logging.info("Database on homelab synchronized successfully.")
        logging.info(result_db.stdout.decode('utf-8'))
    
    except subprocess.CalledProcessError as e:
        # Log any errors
        logging.error("Failed to synchronize database on homelab.")
        logging.error(e.stderr.decode('utf-8'))
    

def main():

    data = transform(get_data())
    load(data, local_db_path)
    rsync()


if __name__ == "__main__":
    main()