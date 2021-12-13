from enum import Enum


class Actions(Enum):
    # General.
    OFF = "3301000000000000000000000000000000000032"
    ON = "3301010000000000000000000000000000000033"
    KEEP_ALIVE = "3301010000000000000000000000000000000033"

    # Colors.
    # TODO: Test other colors w/ and w/o gradients.
    MODE_COLOR = "3305150100000000000000000000000000000022"

    # Scenes.
    # TODO: Test other scenes and DIY mode.
    MODE_SCENE = "3305040500000000000000000000000000000037"
    SCENE_NIGHTLIGHT = "3305040200000000000000000000000000000030"
    SCENE_ROMANTIC = "3305040700000000000000000000000000000035"

    def __str__(self):
        return self.name

    def get_bytes(self) -> bytearray:
        return bytearray(bytes.fromhex(self.value))

    @staticmethod
    def from_string(s):
        try:
            return Actions[s]
        except KeyError:
            raise ValueError()
