import pandas as pd
import design
import matplotlib.pyplot as plt

def main(specifications, solar_data):
    power = float(specifications['power'])

    battery_energy = float(specifications['battery_energy'])

    solar_area = float(specifications['solar_area'])

    battery_energy_over_time = [battery_energy]
    
    eta_charging = 0.98
    eta_solar = 0.20

    for i in range(len(solar_data)):
        GHI = solar_data['GHI'].iloc[i]
        # Assuming there's a maximum capacity for the battery, for example, `max_battery_energy`.
        max_battery_energy = float(specifications['battery_energy'])

        # Compute the new battery energy and ensure it does not exceed the max capacity.
        new_battery_energy = battery_energy_over_time[-1] + GHI * solar_area * eta_charging * eta_solar - power

        # Limit to max capacity.
        new_battery_energy = max(min(new_battery_energy, max_battery_energy), 0)

        battery_energy_over_time.append(new_battery_energy)
    
    return battery_energy_over_time

def plot_hours(battery_energy_over_time):
    time_index = list(range(len(battery_energy_over_time)))

    # Plot the data
    plt.figure(figsize=(12, 6))
    plt.plot(time_index, battery_energy_over_time, label='Battery Energy (Wh)')
    plt.title('Battery Energy Over Time')
    plt.xlabel('Time (hours)')
    plt.ylabel('Battery Energy (Wh)')
    plt.grid(True)
    plt.legend()
    plt.show()

def plot_days(battery_energy_over_time):
    # Convert time index to days
    time_index_days = [t / 24 for t in range(len(battery_energy_over_time))]

    # Plot the data
    plt.figure(figsize=(12, 6))
    plt.plot(time_index_days, battery_energy_over_time, label='Battery Energy (Wh)')
    plt.title('Battery Energy Over Time')
    plt.xlabel('Time (days)')
    plt.ylabel('Battery Energy (Wh)')
    plt.grid(True)
    plt.legend()
    plt.show()


import matplotlib.pyplot as plt

def plot_days(battery_energy_over_time, start_day, end_day):
    # Convert time index to days
    time_index_days = [t / 24 for t in range(len(battery_energy_over_time))]
    
    # Filter data for the specified day range
    start_index = int(start_day * 24)  # Convert days to hours (index)
    end_index = int(end_day * 24)     # Convert days to hours (index)
    
    filtered_time = time_index_days[start_index:end_index + 1]
    filtered_energy = battery_energy_over_time[start_index:end_index + 1]
    
    # Plot the data
    plt.figure(figsize=(12, 6))
    plt.plot(filtered_time, filtered_energy, label='Battery Energy (Wh)')
    plt.title(f'Battery Energy Over Time (Days {start_day} to {end_day})', fontsize=18)
    plt.xlabel('Time (days)', fontsize=16)
    plt.ylabel('Battery Energy (Wh)', fontsize=16)
    plt.ylim(bottom=0)  # Set the y-axis to start at zero
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == '__main__':
    df_solar = pd.read_csv('Boston_GHI.csv')

    specifications = design.main(1.5, 6, 48, solar=True)
    print(specifications)

    battery_energy_over_time = main(specifications, df_solar)

    plot_days(battery_energy_over_time, start_day=60, end_day=330)

# if __name__ == '__main__':
#     df_solar = pd.read_csv('Boston_GHI.csv')

#     for a in range(20, 60, 1):
#         for b in range(20, 60, 1):
#             a_new = a / 10
#             specifications = design.main(1.5, a_new, b, solar=True)

#             L_val = specifications['L']
#             battery_energy = specifications['energy_req']

#             if abs(L_val - 2.25) < 0.1 and abs(battery_energy - 2100) < 100:
#                 print(a_new, b)
#                 battery_energy_over_time = main(specifications, df_solar)
#                 plot_days(battery_energy_over_time, start_day=60, end_day=330)