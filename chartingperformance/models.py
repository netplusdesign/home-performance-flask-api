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
    adjusted_load = Column(Numeric(precision=4))
    solar = Column(Numeric(precision=4))
    used = Column(Numeric(precision=4))
    water_heater = Column(Numeric(precision=4))
    ashp = Column(Numeric(precision=4))
    water_pump = Column(Numeric(precision=4))
    dryer = Column(Numeric(precision=4))
    washer = Column(Numeric(precision=4))
    dishwasher = Column(Numeric(precision=4))
    stove = Column(Numeric(precision=4))
    refrigerator = Column(Numeric(precision=4))
    living_room = Column(Numeric(precision=4))
    aux_heat_bedrooms = Column(Numeric(precision=4))
    aux_heat_living = Column(Numeric(precision=4))
    study = Column(Numeric(precision=4))
    barn = Column(Numeric(precision=4))
    basement_west = Column(Numeric(precision=4))
    basement_east = Column(Numeric(precision=4))
    ventilation = Column(Numeric(precision=4))
    ventilation_preheat = Column(Numeric(precision=4))
    kitchen_recept_rt = Column(Numeric(precision=4))

class EnergyDaily(Base):
    __tablename__ = 'energy_daily'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    device_id = Column(Integer, ForeignKey('monitor_devices.device_id'), primary_key=True)
    date = Column(DateTime, primary_key=True)
    adjusted_load = Column(Numeric(precision=5, scale=3))
    solar = Column(Numeric(precision=5, scale=3))
    used = Column(Numeric(precision=5, scale=3))
    water_heater = Column(Numeric(precision=5, scale=3))
    ashp = Column(Numeric(precision=5, scale=3))
    water_pump = Column(Numeric(precision=5, scale=3))
    dryer = Column(Numeric(precision=5, scale=3))
    washer = Column(Numeric(precision=5, scale=3))
    dishwasher = Column(Numeric(precision=5, scale=3))
    stove = Column(Numeric(precision=5, scale=3))
    refrigerator = Column(Numeric(precision=5, scale=3))
    living_room = Column(Numeric(precision=5, scale=3))
    aux_heat_bedrooms = Column(Numeric(precision=5, scale=3))
    aux_heat_living = Column(Numeric(precision=5, scale=3))
    study = Column(Numeric(precision=5, scale=3))
    barn = Column(Numeric(precision=5, scale=3))
    basement_west = Column(Numeric(precision=5, scale=3))
    basement_east = Column(Numeric(precision=5, scale=3))
    ventilation = Column(Numeric(precision=5, scale=3))
    ventilation_preheat = Column(Numeric(precision=5, scale=3))
    kitchen_recept_rt = Column(Numeric(precision=5, scale=3))

class EnergyMonthly(Base):
    __tablename__ = 'energy_monthly'
    house_id = Column(Integer, ForeignKey('houses.house_id'), primary_key=True)
    device_id = Column(Integer, ForeignKey('monitor_devices.device_id'), primary_key=True)
    date = Column(DateTime, primary_key=True)
    adjusted_load = Column(Numeric(precision=7, scale=3))
    solar = Column(Numeric(precision=7, scale=3))
    used = Column(Numeric(precision=7, scale=3))
    water_heater = Column(Numeric(precision=6, scale=3))
    ashp = Column(Numeric(precision=6, scale=3))
    water_pump = Column(Numeric(precision=5, scale=3))
    dryer = Column(Numeric(precision=6, scale=3))
    washer = Column(Numeric(precision=5, scale=3))
    dishwasher = Column(Numeric(precision=5, scale=3))
    stove = Column(Numeric(precision=6, scale=3))
    refrigerator = Column(Numeric(precision=6, scale=3))
    living_room = Column(Numeric(precision=6, scale=3))
    aux_heat_bedrooms = Column(Numeric(precision=6, scale=3))
    aux_heat_living = Column(Numeric(precision=6, scale=3))
    study = Column(Numeric(precision=6, scale=3))
    barn = Column(Numeric(precision=6, scale=3))
    basement_west = Column(Numeric(precision=6, scale=3))
    basement_east = Column(Numeric(precision=6, scale=3))
    ventilation = Column(Numeric(precision=6, scale=3))
    ventilation_preheat = Column(Numeric(precision=6, scale=3))
    kitchen_recept_rt = Column(Numeric(precision=6, scale=3))

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
    used_max = Column(Numeric(precision=4))
    solar_min = Column(Numeric(precision=4))
    outdoor_deg_min = Column(Numeric(precision=6, scale=3))
    outdoor_deg_max = Column(Numeric(precision=6, scale=3))
    hdd_max = Column(Numeric(precision=4, scale=3))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
