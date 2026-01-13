from feast import Entity, ValueType

camera = Entity(
    name="id_camera", 
    join_keys=["id_camera"],
    value_type=ValueType.STRING, 
    description="ID of the camera device",
)