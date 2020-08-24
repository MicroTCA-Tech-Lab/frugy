import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

import unittest             # noqa: E402
from test_types import *    # noqa: F401,F403,E402

if __name__ == '__main__':
    unittest.main()
