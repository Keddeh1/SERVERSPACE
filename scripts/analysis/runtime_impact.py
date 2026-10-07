#!/usr/bin/env python3
"""Illustrative marginal-energy scenarios; every input is an assumption, not a meter reading."""
import json
from decimal import Decimal as D


def scenario(name, devices, device_watts):
    retired=10;server_watts=D('250');standby=D('5');facility=D('1.3');added_server=D('300')
    endpoint=D(devices)*D(device_watts)
    server_facility_saving=(D(retired)*(server_watts-standby)-added_server)*facility
    net=server_facility_saving-endpoint
    annual=net*D(8760)/D(1000)
    return {'scenario':name,'assumptions':{'servers_power_reduced':retired,'prior_watts_each':str(server_watts),
      'standby_watts_each':str(standby),'facility_incremental_factor':str(facility),
      'additional_verification_server_watts':str(added_server),'average_active_devices':devices,
      'incremental_watts_per_device':str(device_watts),'electricity_price_per_kwh':'0.25',
      'emissions_kg_per_kwh':'0.4','annual_hours':8760},
      'results':{'server_facility_saving_watts':str(server_facility_saving),'endpoint_incremental_watts':str(endpoint),
       'net_saving_watts':str(net),'annual_net_saving_kwh':str(annual),
       'annual_electricity_saving_currency_units':str(annual*D('0.25')),
       'annual_operational_emissions_saving_kg':str(annual*D('0.4')),
       'break_even_incremental_endpoint_watts':str(server_facility_saving)}}


def report():
    rows=[scenario('lower client demand',200,'2'),scenario('moderate client demand',1000,'2'),scenario('higher client demand',1000,'5')]
    assert D(rows[0]['results']['net_saving_watts'])==D('2395.0')
    assert D(rows[1]['results']['net_saving_watts'])==D('795.0')
    assert D(rows[2]['results']['net_saving_watts'])==D('-2205.0')
    assert D(rows[1]['results']['annual_net_saving_kwh'])==D('6964.2')
    cloud={'assumed_removed_instances':10,'assumed_monthly_avoidable_price_each':'150',
      'assumed_incremental_monthly_delivery_verification_support':'400','assumed_one_time_integration':'10000',
      'monthly_net_saving':str(D(10)*D(150)-D(400)),
      'simple_payback_months':str(D(10000)/(D(10)*D(150)-D(400)))}
    return {'scope':'illustrative sensitivities, not measured KEX savings; energy and cloud cash models are separate',
      'measurement_required':['eligible-workload equivalence','marginal facility power','client-device incremental power',
        'standby draw','network/sync energy','regional marginal grid intensity','actual avoidable invoices'],
      'scenarios':rows,'cloud_cost_scenario':cloud,'checks':'energy accounting and positive/negative scenarios passed'}

if __name__=='__main__':print(json.dumps(report(),indent=2))
