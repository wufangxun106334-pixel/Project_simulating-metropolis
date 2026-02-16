# TODO: Task 1: Add location class here
class Serializable:
    @classmethod
    def from_dict(cls, data):
        raise NotImplementedError("Subclasses must implement from_dict")

    def to_dict(self):
        raise NotImplementedError("Subclasses must implement to_dict")

class Location(Serializable):
    def __init__(self, x, y):
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise TypeError("Coordinates must be numbers")
        if not (-100 <= x <= 100) or not (-100 <= y <= 100):
            raise ValueError("Coordinates must be between -100 and 100")
        self.__x = x
        self.__y = y

    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("X coordinate must be a number")
        if not (-100 <= value <= 100):
            raise ValueError("X coordinate must be between -100 and 100")
        self.__x = value

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Y coordinate must be a number")
        if not (-100 <= value <= 100):
            raise ValueError("Y coordinate must be between -100 and 100")
        self.__y = value

    def to_dict(self):
        return {"x": self.__x, "y": self.__y}

    @classmethod
    def from_dict(cls, data):
        return cls(data["x"], data["y"])

    def __str__(self):
        return f"X: {self.__x}, Y: {self.__y}"
# test code
if __name__ == "__main__":
    loc = Location(10, 15)
    print(loc)