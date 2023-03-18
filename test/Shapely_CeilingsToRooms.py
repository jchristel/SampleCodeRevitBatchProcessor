import sys
SAMPLES_PATH = r'C:\Users\jchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\duHast\src'
sys.path += [SAMPLES_PATH]

from duHast.DataSamples import ProcessCeilingsToRooms as magic

# files required
data_in = r'C:\Users\jchristel\Documents\DebugRevitBP\CeilingsVsRooms\jsonFromModel.json'
report_out = r'C:\Users\jchristel\Documents\DebugRevitBP\CeilingsVsRooms\ceilingsByRoom.csv'

print('Getting data from {}'.format(data_in))
ceilings_by_room = magic.get_ceilings_by_room(data_in)
print(ceilings_by_room.message)

print('writing data to file')
data_to_file = magic.write_data_to_file(
    ceilings_by_room.result, 
    report_out, room_instance_property_keys= ['Number', 'Name'], 
    ceiling_type_property_keys = ['Type Mark'], 
    ceiling_instance_property_keys =['Height Offset From Level'] )

print(data_to_file.message)

#CeilingsToRooms.GetCeilingsByRoom(data_in , report_out)