# SolarPoweredBoat
design.py : Contains code to design a boat given inputs on required speed (v), solar hours available per day (n), and number of hours the battery can power the boat for (y)

backtest.py : Contains code to simulate the boat’s battery state of charge over time. Uses hourly resolution 2023 Global Horizontal Irradiance (GHI) data for Boston and assumes a constant boat velocity of 1.5 m/s

Boston_GHI.csv : Hourly level 2023 Global Horizontal Irradiance (GHI) data for Charles River near MIT’s campus. Pulled from NREL NSRDB (National Renewable Energy Laboratory’s National Solar Radiation Database)

See White Paper here: https://docs.google.com/document/d/1ULr5f7lZfxk9ESfFBOQ7HTKHdhNtNc0sHE-Q7hoRRn0/edit?tab=t.0
