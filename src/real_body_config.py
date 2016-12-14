from src.body import Body
from src.vector import Vector
AU = 149598e6

# Body Config
# Configure Earth Body
Earth = Body()
Earth.id = 1
Earth.name = "Earth"
Earth.mass = 5.972e24
Earth.position.set(AU, 0)
Earth.velocity = Vector()
Earth.velocity.set(0, 29.8e3)
Earth.type = "Planet"

# Configure Sun Body
Sun = Body()
Sun.id = 2
Sun.name = "Sun"
Sun.mass = 1.989e30
Sun.position.set(0, 0)
Sun.velocity.set(0, 0)
Sun.type = "Star"

# Configure Mars Body
Mars = Body()
Mars.id = 3
Mars.name = "Mars"
Mars.mass = 4.02e22
Mars.position.set(227.9e9, 0)
Mars.velocity.set(0, 24.1308e3)
Mars.type = "Planet"

# Configure Halley's comet
Halley = Body()
Halley.id = 4
Halley.name = "Halley"
Halley.mass = 2.2e14
Halley.velocity.set(54.49e3, 0)
Halley.position.set(0, 88e9)
Halley.type = "Comet"

# Configure Jupiter Body
Jupiter = Body()
Jupiter.id = 5
Jupiter.name = "Jupiter"
Jupiter.mass = 1.90e27
Jupiter.position.set(5.455 * AU, 0)
Jupiter.velocity.set(0, 12.44e3)
Jupiter.type = "Planet"

# Configure Charon Body
Charon = Body()
Charon.id = 5
Charon.name = "Charon"
Charon.mass = 1.586e21
Charon.velocity.set(0, 0.21e3)
Charon.position.set(17536e3, 0)
Charon.type = "Moon"

# Configure Pluto Body
Pluto = Body()
Pluto.id = 6
Pluto.name = "Pluto"
Pluto.mass = 1.309e22
Pluto.velocity.set(0, 0)
Pluto.position.set(0, 0)
Pluto.type = "Planet"