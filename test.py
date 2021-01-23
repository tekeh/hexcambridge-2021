from src.context import DataOwner, Computer
import tenseal as ts
import numpy as np

owner = DataOwner()
data = [0, 1, 2]
encrypted_data = owner.encrypt(data)
owner.make_package(encrypted_data, 'data')

rando = Computer()
tensor = rando.get_data('data')

owner.decrypt(tensor)
