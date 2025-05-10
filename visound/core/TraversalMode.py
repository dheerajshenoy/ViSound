from enum import Enum

class TraversalMode(Enum):
    LeftToRight = 0,
    RightToLeft = 1,
    TopToBottom = 2,
    BottomToTop = 3,
    CircleInward = 4,
    CircleOutward = 5,
