#!/usr/bin/env python3

import json
import os
import sqlite3
import sys


##### Functions
def check_fuel_mileage():
    previous = None
    fuel_cursor = cursor.execute(select_fuel_all)
    for fuel in fuel_cursor:
        odometer = fuel[1]
        if previous:
            date                = fuel[0]
            calculated_mileage  = odometer - previous
            odometer_mileage    = fuel[2]
            if abs(calculated_mileage - odometer_mileage) > .5:
                print('{0} {1} calculated mileage is {2} instead of {3}'
                      .format(date, odometer,
                              calculated_mileage, odometer_mileage))
        previous = odometer

def check_payed_price():
    fuel_cursor = cursor.execute(select_fuel_all)
    for fuel in fuel_cursor:
        date        = fuel[0]
        odometer    = fuel[1]
        to_pay      = fuel[3] * fuel[4]
        payed       = fuel[5]
        if abs(to_pay - payed) > 0.005:
            print('{0} {1} you payed {2:.3f} instead of {3:.3f}'
                  .format(date, odometer, payed, to_pay))

# Create the table if it not exists
def create_table(table_name, create_statement):
    if not cursor.execute(select_table, [table_name]).fetchone():
        print('Going to create the table {0}'.format(table_name))
        cursor.execute(create_statement)

def deinit():
    conn.commit()
    conn.close()

def display_mileage_pro_liter():
    previous            = None
    previous_full_tank  = False

    fuel_cursor = cursor.execute(select_fuel_all)
    for fuel in fuel_cursor:
        date        = fuel[0]
        odometer    = fuel[1]
        full_tank   = fuel[6] == 1
        if previous and full_tank and previous_full_tank:
            liters              = fuel[3]
            mileage             = odometer - previous
            mileage_pro_liter   = mileage / liters
            liters_pro_100km    = liters / (mileage / 100)
            print('{0} {1} mileage pro liter: {2:5.2f}'
                  .format(date, odometer, mileage_pro_liter))
            print('{0} {1} liters pro 100 km: {2:5.2f}'
                  .format(date, odometer, liters_pro_100km))
        previous            = odometer
        previous_full_tank  = full_tank

def init():
    global conn
    global cursor

    # Go to the right directory
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    conn    = sqlite3.connect('car.sqlite')
    cursor  = conn.cursor()
    create_table('fuel', create_fuel_table)
    create_table('rides', create_rides_table)
    fill_tables()
    check_payed_price()
    check_fuel_mileage()
    display_mileage_pro_liter()

def fill_table(table_name, table_data, search_length, search_statement, insert_statement):
    for values in table_data:
        search_value    = values[0 : search_length]
        to_insert       = tuple(values[search_length : ])
        found           = cursor.execute(search_statement, search_value).fetchone()
        if not found:
            print('{0:5s}: adding {1}'.format(table_name, search_value))
            cursor.execute(insert_statement, values)
        else:
            if found != to_insert:
                print('For {0} found {1} instead of {2}'
                      .format(search_value, found, to_insert))

# When tableValues.json exist it is used to fill the tables
def fill_tables():
    filename = './tableValues.json'

    if os.path.exists(filename):
        with open(filename, 'r') as in_f:
            data = json.load(in_f)
        if 'fuel' in data:
            fill_table('fuel',  data['fuel'],  2, select_fuel, insert_fuel)
        if 'rides' in data:
            fill_table('rides', data['rides'], 2, select_ride, insert_ride)


##### Init

# variables
# SQL statements
create_fuel_table   = '''
                      CREATE TABLE fuel (
                      date        TEXT    NOT NULL,
                      odometer    INTEGER NOT NULL,
                      distance    REAL,
                      liters      REAL    NOT NULL,
                      unit_price  REAL    NOT NULL,
                      payed_price REAL    NOT NULL,
                      full_tank   INTEGER NOT NULL,
                      PRIMARY KEY (date, odometer)
                      )
                      '''
create_rides_table  = '''
                      CREATE TABLE rides (
                      date        text    NOT NULL,
                      odometer    INTEGER NOT NULL,
                      description text    NOT NULL,
                      PRIMARY KEY (date, odometer)
                      )
                      '''
insert_fuel         = '''
                      INSERT INTO fuel
                      (date, odometer, distance, liters, unit_price, payed_price, full_tank)
                      VALUES
                      (?, ?, ?, ?, ?, ?, ?)
                      '''
insert_ride         = '''
                      INSERT INTO rides
                      (date, odometer, description)
                      VALUES
                      (?, ?, ?)
                      '''
select_table        = '''
                      SELECT name
                      FROM sqlite_master
                      WHERE type = 'table' AND name = ?
                      '''
select_fuel         = '''
                      SELECT distance
                      ,      liters
                      ,      unit_price
                      ,      payed_price
                      ,      full_tank
                      FROM   fuel
                      WHERE  date       = ?
                         AND odometer   = ?
                      '''
select_fuel_all     = '''
                      SELECT   date
                      ,        odometer
                      ,        distance
                      ,        liters
                      ,        unit_price
                      ,        payed_price
                      ,        full_tank
                      FROM     fuel
                      ORDER BY date
                      ,        odometer
                      '''
select_ride         = '''
                      SELECT description
                      FROM   rides
                      WHERE  date       = ?
                         AND odometer   = ?
                      '''


# The program itself
# At the moment there is only init and deinit,
# because the functionalities have to be defined.
init()
deinit()
