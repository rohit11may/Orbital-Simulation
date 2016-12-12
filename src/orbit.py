from src.vector import Vector
from src.body import Body
force = Vector()
force.set(20, 4)

Earth = Body()
Earth.id = 1
Earth.name = "Earth"
Earth.mass = 5.98 * (10 ** 24)
Earth.position.set(150*(10**9), 0)
Earth.velocity.set(0, 29.8 * (10 ** 3))
Earth.type = "Planet"

Earth.updateSelf(force)

