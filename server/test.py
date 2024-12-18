import ConfigManager
from enum import Enum

config = ConfigManager.loadConfig("config\config.json")

counters, data = ConfigManager.readCounterConfig(config)


print("Enum Members:")
for member in counters:
    print(f"{member.name} = {member.value}")

# Print the 2D array
print("\n2D Array:")
for row in data:
    print(row)