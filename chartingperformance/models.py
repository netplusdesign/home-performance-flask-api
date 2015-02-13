""" SQLAlchemy models """
# pylint: disable=no-init
# pylint: disable=too-few-public-methods
# pylint: disable=missing-docstring
from sqlalchemy import Column, Integer, Date, DateTime, Numeric, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Houses(Base):
    __tablename__ = 'houses'
    house_id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(32))
    sname = Column(String(32))
    iga = Column(Numeric(precision=8, scale=2))
    ciga = Column(Numeric(precision=8, scale=2))
    ega = Column(Numeric(precision=8, scale=2))

class MonitorDevices(Base):
    __tablename__ = 'monitor_devices'
    device_id = Column(Integer, primary_key=True, autoincrement=False)
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    name = Column(String(32))

class Circuits(Base):
    __tablename__ = 'circuits'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    circuit_id = Column(String(32), primary_key=True, autoincrement=False)
    name = Column(String(32))
    description = Column(String(80))

class EnergyHourly(Base):
    __tablename__ = 'energy_hourly'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    device_id = Column(Integer, ForeignKey('monitor_devices.device_id'), primary_key=True)
    date = Column(DateTime, primary_key=True)
    adjusted_load = Column(Numeric(precision=14, scale=6))
    solar = Column(Numeric(precision=14, scale=6))
    used = Column(Numeric(precision=14, scale=6))
    water_heater = Column(Numeric(precision=14, scale=6))
    ashp = Column(Numeric(precision=14, scale=6))
    water_pump = Column(Numeric(precision=14, scale=6))
    dryer = Column(Numeric(precision=14, scale=6))
    washer = Column(Numeric(precision=14, scale=6))
    dishwasher = Column(Numeric(precision=14, scale=6))
    stove = Column(Numeric(precision=14, scale=6))
    refrigerator = Column(Numeric(precision=14, scale=6))
    living_room = Column(Numeric(precision=14, scale=6))
    aux_heat_bedrooms = Column(Numeric(precision=14, scale=6))
    aux_heat_living = Column(Numeric(precision=14, scale=6))
    study = Column(Numeric(precision=14, scale=6))
    barn = Column(Numeric(precision=14, scale=6))
    basement_west = Column(Numeric(precision=14, scale=6))
    basement_east = Column(Numeric(precision=14, scale=6))
    ventilation = Column(Numeric(precision=14, scale=6))
    ventilation_preheat = Column(Numeric(precision=14, scale=6))
    kitchen_recept_rt = Column(Numeric(precision=14, scale=6))

class EnergyDaily(Base):
    __tablename__ = 'energy_daily'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    device_id = Column(Integer, ForeignKey('monitor_devices.device_id'), primary_key=True)
    date = Column(Date, primary_key=True)
    adjusted_load = Column(Numeric(precision=14, scale=9))
    solar = Column(Numeric(precision=14, scale=9))
    used = Column(Numeric(precision=14, scale=9))
    water_heater = Column(Numeric(precision=14, scale=9))
    ashp = Column(Numeric(precision=14, scale=9))
    water_pump = Column(Numeric(precision=14, scale=9))
    dryer = Column(Numeric(precision=14, scale=9))
    washer = Column(Numeric(precision=14, scale=9))
    dishwasher = Column(Numeric(precision=14, scale=9))
    stove = Column(Numeric(precision=14, scale=9))
    refrigerator = Column(Numeric(precision=14, scale=9))
    living_room = Column(Numeric(precision=14, scale=9))
    aux_heat_bedrooms = Column(Numeric(precision=14, scale=9))
    aux_heat_living = Column(Numeric(precision=14, scale=9))
    study = Column(Numeric(precision=14, scale=9))
    barn = Column(Numeric(precision=14, scale=9))
    basement_west = Column(Numeric(precision=14, scale=9))
    basement_east = Column(Numeric(precision=14, scale=9))
    ventilation = Column(Numeric(precision=14, scale=9))
    ventilation_preheat = Column(Numeric(precision=14, scale=9))
    kitchen_recept_rt = Column(Numeric(precision=14, scale=9))

class EnergyMonthly(Base):
    __tablename__ = 'energy_monthly'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    device_id = Column(Integer, ForeignKey('monitor_devices.device_id'), primary_key=True)
    date = Column(Date, primary_key=True)
    adjusted_load = Column(Numeric(precision=14, scale=9))
    solar = Column(Numeric(precision=14, scale=9))
    used = Column(Numeric(precision=14, scale=9))
    water_heater = Column(Numeric(precision=14, scale=9))
    ashp = Column(Numeric(precision=14, scale=9))
    water_pump = Column(Numeric(precision=14, scale=9))
    dryer = Column(Numeric(precision=14, scale=9))
    washer = Column(Numeric(precision=14, scale=9))
    dishwasher = Column(Numeric(precision=14, scale=9))
    stove = Column(Numeric(precision=14, scale=9))
    refrigerator = Column(Numeric(precision=14, scale=9))
    living_room = Column(Numeric(precision=14, scale=9))
    aux_heat_bedrooms = Column(Numeric(precision=14, scale=9))
    aux_heat_living = Column(Numeric(precision=14, scale=9))
    study = Column(Numeric(precision=14, scale=9))
    barn = Column(Numeric(precision=14, scale=9))
    basement_west = Column(Numeric(precision=14, scale=9))
    basement_east = Column(Numeric(precision=14, scale=9))
    ventilation = Column(Numeric(precision=14, scale=9))
    ventilation_preheat = Column(Numeric(precision=14, scale=9))
    kitchen_recept_rt = Column(Numeric(precision=14, scale=9))

class HDDMonthly(Base):
    __tablename__ = 'hdd_monthly'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    date = Column(Date, primary_key=True)
    hdd = Column(Numeric(precision=7, scale=3))

class HDDDaily(Base):
    __tablename__ = 'hdd_daily'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    date = Column(Date, primary_key=True)
    hdd = Column(Numeric(precision=6, scale=3))

class HDDHourly(Base):
    __tablename__ = 'hdd_hourly'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    date = Column(DateTime, primary_key=True)
    hdd = Column(Numeric(precision=6, scale=3))

class EstimatedMonthly(Base):
    __tablename__ = 'estimated_monthly'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    date = Column(Date, primary_key=True)
    solar = Column(Numeric(precision=4))
    used = Column(Numeric(precision=4))
    hdd = Column(Numeric(precision=4))
    water = Column(Numeric(precision=4))

class TemperatureDaily(Base):
    __tablename__ = 'temperature_daily'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    device_id = Column(Integer, ForeignKey('monitor_devices.device_id'), primary_key=True)
    date = Column(Date, primary_key=True)
    temperature_min = Column(Numeric(precision=6, scale=3))
    temperature_max = Column(Numeric(precision=6, scale=3))
    humidity_min = Column(Numeric(precision=6, scale=3))
    humidity_max = Column(Numeric(precision=6, scale=3))

class TemperatureHourly(Base):
    __tablename__ = 'temperature_hourly'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    device_id = Column(Integer, ForeignKey('monitor_devices.device_id'), primary_key=True)
    date = Column(DateTime, primary_key=True)
    temperature = Column(Numeric(precision=6, scale=3))
    humidity = Column(Numeric(precision=6, scale=3))

class WaterMonthly(Base):
    __tablename__ = 'water_monthly'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    device_id = Column(Integer, ForeignKey('monitor_devices.device_id'), primary_key=True)
    date = Column(Date, primary_key=True)
    gallons = Column(Numeric(precision=7, scale=1))

class LimitsHourly(Base):
    __tablename__ = 'limits_hourly'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    used_max = Column(Numeric(precision=14, scale=9))
    solar_min = Column(Numeric(precision=14, scale=9))
    outdoor_deg_min = Column(Numeric(precision=6, scale=3))
    outdoor_deg_max = Column(Numeric(precision=6, scale=3))
    hdd_max = Column(Numeric(precision=4, scale=3))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
