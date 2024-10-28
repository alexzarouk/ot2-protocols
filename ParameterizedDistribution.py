from opentrons import protocol_api
from typing import List

metadata = {
    'protocolName': 'Parameterized Plate Distribution for up to 48 Factors',
    'author': 'Alexander Zarouk <alexzarouk@gmail.com>',
    'source': 'Perform a series of distributions with a configurable volume, set number of repetitions, and factors',
    'apiLevel': '2.20'
}

# Helper function to flatten the plate
def flatPlateR(rows_list):
    flattened_list = []
    for row in rows_list:
        flattened_list.extend(row)
    return flattened_list

# Function to distribute factors with variable volume
def distribute_factors(pipette: protocol_api.InstrumentContext, factors: List[str], destination_wells: List[str], volume: float):
    for factor_well, dest_well in zip(factors, destination_wells):
        pipette.transfer(volume, factor_well, dest_well, air_gap = 20, new_tip="never")

# Function to define runtime parameters
def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_float(
        variable_name="volume",
        display_name="Transfer Volume",
        description="Volume to transfer to each well in µL.",
        default=100.0,
        minimum=1.0,
        maximum=200.0,
        unit="µL"
    )
    parameters.add_int(
        variable_name="air_gap",
        display_name="Air Gap",
        description="Add a volume of air after aspiration to reduce risk of droplets and lost volume.",
        default=20,
        minimum=0,
        maximum=50,
        unit="µL air"
    )
    parameters.add_int(
        variable_name="factors",
        display_name="Number of Factors",
        description="The total number of factors to be used in treatments across the entire deck",
        default=5,
        minimum= 1,
        maximum= 48,
        unit="Epp 1.5"
    )
    parameters.add_int(
        variable_name="repeatsPerTreat",
        display_name="Repeats",
        description="how many repeats of each condition to perform across the plate",
        default=3,
        minimum= 1,
        maximum= 12
    )

# Main run function
def run(protocol: protocol_api.ProtocolContext):
    
    # Load labware
    tiprack200 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '8')
    p300 = protocol.load_instrument('p300_single_gen2', 'right', tip_racks=[tiprack200])
    
    plate = protocol.load_labware('corning_96_wellplate_360ul_flat', '5')
    tube_rack_1 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '1')
    tube_rack_2 = protocol.load_labware('opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap', '2')
    
    # Define wells in the tube racks
    factors_rack_1 = flatPlateR(tube_rack_1.rows())
    factors_rack_2 = flatPlateR(tube_rack_2.rows())

    numFactors = protocol.params.factors
    all_factors = factors_rack_1[:numFactors]
    
    # Define wells in the 96-well plate
    destination_wells = flatPlateR(plate.rows())

    # Retrieve the volume parameter defined by the technician at runtime
    volume = protocol.params.volume
    repeats = protocol.params.repeatsPerTreat
    
    # Distribute factors using the volume parameter
    for i, factor in enumerate(all_factors):
        p300.pick_up_tip()
        for j in range(repeats):
            dest_index = i * repeats + j
            distribute_factors(p300, [factor], [destination_wells[dest_index]], volume)
        p300.drop_tip()
