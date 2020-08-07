owner: public(address)
contractor: public(address)
  
struct Coordinates:
   latitude: String[10]
   longitude: String[10]
  
struct ContractConditions:
   delivery_time_hours: int128
   maximal_temperature_milliC: int128
   maximal_overtemperature_exposure_minutes: int128
   nominal_payment: int128
   delay_hour_percentage_penalty: int128
   pickup_coordinates: Coordinates
   destination_coordinates: Coordinates
  
event LogConditions:
   owner: address
   delivery_time_hours: int128
   maximal_temperature_milliC: int128
   maximal_overtemperature_exposure_minutes: int128
   nominal_payment: int128
   delay_hour_percentage_penalty: int128
   
struct Measurement:
   temperature_milliC: int128
   time: uint256
   
conditions: public(ContractConditions)
measurement_storage: public(Measurement[30000])
measurement_counter: public(int128)
  
temperature_exceeded_time: public(uint256)
delivery_start: public(uint256)
delivery_end: public(uint256)
ended: public(bool)
voided: public(bool)
total_penalty: int128
final_payment: public(int128)
valid_approvers: constant(address[2]) = [0xafc7c956eBddcC50944047595b8857c6ACd6A7cA, 0xD253d1D2937E8FbCd0306B1b54f5607480837c2d]

@external
def __init__(_delivery_time_hours: int128, _maximal_temperature_milliC: int128, _maximal_overtemperature_exposure_minutes: int128, _nominal_payment: int128, _delay_hour_percentage_penalty: int128, _pickup_coordinates: Coordinates, _destination_coordinates: Coordinates):
   self.conditions = ContractConditions({delivery_time_hours: _delivery_time_hours,
   maximal_temperature_milliC: _maximal_temperature_milliC,
   maximal_overtemperature_exposure_minutes: _maximal_overtemperature_exposure_minutes,
   nominal_payment: _nominal_payment,
   delay_hour_percentage_penalty: _delay_hour_percentage_penalty,
   pickup_coordinates: _pickup_coordinates,
   destination_coordinates: _destination_coordinates})
   self.owner = msg.sender

   @external
def accept_conditions():
   self.contractor = msg.sender
   
@external
def log_conditions():
   log LogConditions(self.owner,
   self.conditions.delivery_time_hours,
   self.conditions.maximal_temperature_milliC,
   self.conditions.maximal_overtemperature_exposure_minutes,
   self.conditions.nominal_payment,
   self.conditions.delay_hour_percentage_penalty)

@external
def start_delivery():
   assert msg.sender in valid_approvers
   self.delivery_start = block.timestamp

@internal
def time_diff(t1: uint256, t2: uint256) -> uint256:
   return t2-t1
  
@internal
def check_contract_voiding_conditions():
   if (self.measurement_storage[self.measurement_counter-1].temperature_milliC > self.conditions.maximal_temperature_milliC):
       if (self.measurement_counter>1):
           self.temperature_exceeded_time += self.time_diff(self.measurement_storage[self.measurement_counter-2].time, self.measurement_storage[self.measurement_counter-1].time)
       else:
           self.temperature_exceeded_time = self.time_diff(self.delivery_start, self.measurement_storage[0].time)
       if (self.temperature_exceeded_time > convert(self.conditions.maximal_overtemperature_exposure_minutes*60, uint256)):
           self.voided = True
           self.ended = True
   else:
       self.temperature_exceeded_time = 0
       
@external
def store_measurements(_temperature: int128, _measurement_time: uint256):
   assert not self.ended
   assert self.delivery_start > 0
   assert _measurement_time >= self.delivery_start, "Measurement time must be greater than the delivery start time"
   self.measurement_storage[self.measurement_counter] = Measurement({
       temperature_milliC: _temperature,
       time: _measurement_time
   })
   self.measurement_counter += 1
   self.check_contract_voiding_conditions()

@internal
def finalize_contract():
   assert not self.ended
   delivery_duration: uint256 = self.time_diff(self.delivery_start, self.delivery_end)
   delivery_delay: int128 = convert(delivery_duration, int128) - self.conditions.delivery_time_hours*60*60
   if (delivery_delay > 0):
       self.total_penalty = self.conditions.delay_hour_percentage_penalty*(delivery_delay/60/60)
       if (self.total_penalty > 100):
           self.final_payment = 0
       else:
           self.final_payment = self.conditions.nominal_payment*(100-self.total_penalty)/100
   else:
       self.final_payment = self.conditions.nominal_payment
   self.ended = True
  
@external
def confirm_delivery():
   assert not self.voided, "The contract was voided!"
   self.delivery_end = block.timestamp
   self.finalize_contract()