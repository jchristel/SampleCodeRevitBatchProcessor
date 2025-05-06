namespace duHastNet.PushIt.Utilities
{
    public class ConvertRevitRoomObjectToDataModelRoomObject
    {

        public static Models.RoomDataModel ConvertRevitRoomToDataModelRoom(
            Models.RoomsRevit revitRoom)
        {
            // create a new room data model object
            Models.RoomDataModel roomDataModel = new Models.RoomDataModel();

            // set the properties of the room data model object
            // start with the id
            Models.RoomDataProperty id = new Models.RoomDataProperty(
                name: revitRoom.Id.Name,
                parameterGUID: revitRoom.Id.ParameterGUID,
                parameterName: revitRoom.Id.ParameterName,
                value: revitRoom.Id.Value,
                showInUI: revitRoom.Id.ShowInUI,
                isReadOnly: revitRoom.Id.IsReadOnly);

            roomDataModel.Id = id;

            //convert all other properties
            foreach (var property in revitRoom.Properties)
            {
                Models.RoomDataProperty roomDataProperty = new Models.RoomDataProperty(
                    name: property.Name,
                    parameterGUID: property.ParameterGUID,
                    parameterName: property.ParameterName,
                    value: property.Value,
                    showInUI: property.ShowInUI,
                    isReadOnly: property.IsReadOnly);

                roomDataModel.Properties.Add(roomDataProperty);


            }

            return roomDataModel;
        }

    }
}
