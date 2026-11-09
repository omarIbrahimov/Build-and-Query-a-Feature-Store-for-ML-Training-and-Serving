from feast import Entity
from feast.value_type import ValueType
customer = Entity(name='customer', join_keys=['customer_id'], value_type=ValueType.STRING,
                  description='PaySim sender nameOrig; no invented ordering within a simulated hour')
