import casadi as cas
import math

def main(boat_speed, hrs_sun, battery_hours, solar=True):
    opti = cas.Opti()

    ### CONSTANTS
    p_water = 1000 ### kg / m^3
    p_solar = 0.4 ### kg / m^2
    p_foam = 3 ### kg/m^2
    g = 9.81  # m/s^2
    pi = math.pi
    viscosity_water = 10**(-6) ### m^2 / s
    battery_specific_energy = 183 ### Wh / kg
    mass_payload = 30000
    
    ### VARIABLES
    L = 10*opti.variable()
    W = 1*opti.variable()
    x = 0.1*opti.variable()
    B = 5*opti.variable()
    opti.set_initial(L, 10)  # Initial guess for L
    opti.set_initial(W, 1)   # Initial guess for W
    opti.set_initial(x, 0.1) # Initial guess for x
    opti.set_initial(B, 5)   # Initial guess for B

    ### x is the height of the wetted portion of the hull

    ### COMPUTE SURFACE AREA, PERIMETER, approximate as ellipses
    a = L/2
    b = W/2

    hull_face_area = pi*a*b
    hull_face_area_total = 2 * hull_face_area

    hull_perimeter = pi*(3 * (a + b) - ((3*a + b) * (a + 3*b))**0.5 ) ### Ramanujan's Approximation

    S_hull_wetted = hull_face_area + hull_perimeter*x

    S_2hulls_wetted = 2*S_hull_wetted

    ### DRAG COEFFICIENT (C_t = C_f)
    Re_num = boat_speed * L / viscosity_water

    C_f = 0.075 / (cas.log10(Re_num) - 2)**2
    C_t = C_f

    # C_t = C_f = 0.014

    ### F_drag
    F_drag = 0.5 * p_water * C_t * S_2hulls_wetted * (boat_speed**2) 

    starlink_power = 25 + 300

    ## POWER CONSTANTS
    eta_charging = 0.98
    eta_propulsion = 0.7
    eta_solar = 0.20
    starlink_mass = 3 ### kg

    ### Power required
    power = F_drag * boat_speed / eta_propulsion + starlink_power

    solar_intensity = 1000 ### W/m^2, note that the average day in boston has 4.91 kWh / m2
    ### Nov/Dec/Jan/Feb have about 2 kWh / m2, summer months have 5 - 6 kWh/m2
    ### We put in 3 hrs_sun as the average


    ### COMPUTING REQ MASS
    ### Energy required
    energy_req = (power * battery_hours) / eta_propulsion / eta_charging

    ### Solar + Batteries required
    # Enough battery to last battery_hours without recharge
    # Enough solar to recharge the full battery in hrs_sun
    battery_mass = energy_req / battery_specific_energy

    battery_energy = battery_mass * battery_specific_energy

    if solar:
        solar_area = energy_req / (solar_intensity * hrs_sun * eta_solar)

        solar_mass = p_solar * solar_area
    else:
        solar_area = 0
        solar_mass = 0

    ### Foam mass
    foam_mass = hull_face_area_total*p_foam*(0.5 + x)

    ### COMPUTE REQUIRED HEIGHT OF WETTED SURFACE AREA
    mass_total = battery_mass + solar_mass + foam_mass + starlink_mass + mass_payload
    buoyant_force_mass = (p_water - p_foam) * (2 * hull_face_area) * x

    # (p_water - p_foam) * g * (2 * hull_face_area) * x = (battery_mass + solar_mass + foam_mass + starlink_mass) * g

    Fr_num = boat_speed / (g * L)**0.5

    opti.subject_to([
        L / W >= 6
    ])

    opti.subject_to([
        L/B > 1
    ])

    if solar:
        opti.subject_to([
            solar_area / (L*B) < 1
            ]
        )

    opti.subject_to(L > 0)  # Ensure L is positive
    opti.subject_to(W > 0.1)
    opti.subject_to(B > 0.01)
    opti.subject_to(x > 0.01)
    opti.subject_to(buoyant_force_mass == mass_total)
    opti.subject_to(Re_num > 1e3)  # Typical lower limit for turbulent flow
    # opti.subject_to(solar_area >= 0.01)
    # opti.subject_to(solar_mass >= 0.01)
    opti.subject_to(mass_total > 0.01)
    opti.subject_to(battery_mass > 0.01)
    opti.subject_to(energy_req > 0.01)


    opti.minimize(mass_total)

    p_opts = {}
    s_opts = {}
    s_opts["max_iter"] = 1e3
    s_opts["mu_strategy"] = "monotone"
    # s_opts["start_with_resto"] = "yes"
    s_opts["required_infeasibility_reduction"] = 0.1
    s_opts["expect_infeasible_problem"] = "yes"
    opti.solver('ipopt', p_opts, s_opts)

    try:
        sol = opti.solve()
    except:
        sol = opti.debug



    ##### Text output
    # out = lambda x, val: print("%s: %f" % (x, val))  # input a variable name as a string
    # print("xs is: ", xs)
    print_title = lambda s: print("\n********** %s **********" % s.upper())

    vars_of_interest = ["L", "W", "B", "Re_num", "S_hull_wetted", "x", "hull_perimeter", "hull_face_area", "buoyant_force_mass", "hull_face_area", "mass_total", "battery_mass", "solar_mass", "foam_mass", "mass_payload", "starlink_mass", "power", "F_drag", "C_f", "energy_req", "solar_area", "Fr_num", "battery_energy"]
    print_title("Results")

    # for var_name in vars_of_interest:
    #     print(f"{var_name}: {sol.value(eval(var_name, locals()))}")
    results_dict = {}

    for var_name in vars_of_interest:
        results_dict[var_name] = sol.value(eval(var_name, locals()))


    ### COST ESTIMATION
    V_foam = (0.5 + x) * results_dict['hull_face_area'] * 2

    cost_battery = 30 ### $ / kg
    cost_solar = 200 ### $ / m2
    cost_foam = 35 ### $ / m3
    cost_starlink = 600 ### $
    cost_MPPT = 100
    cost_motors = 150
    cost_electronics = 200
    cost_sensors = 200

    total_cost = cost_battery * results_dict['battery_mass'] + cost_solar * results_dict['solar_area'] + cost_foam * V_foam + cost_starlink + cost_MPPT + cost_electronics+ cost_sensors
    results_dict['total_cost'] = sol.value(total_cost)

    results_dict["boat_speed"] = boat_speed
    results_dict["hrs_sun"] = hrs_sun
    results_dict["battery_hours"] = results_dict
    results_dict["solar"] = solar

    return results_dict


output = main(5, 5, 10, solar=True)
print(output)