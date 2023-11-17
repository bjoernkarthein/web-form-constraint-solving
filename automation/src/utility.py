import math
import requests
import time

"""
Utility module

Provides helper functions and variables that are used throughout the project
"""

instrumentation_service_base_url = 'http://localhost:4000'


def record_trace(action, args=None):
    url = f'{instrumentation_service_base_url}/record'
    requests.post(url, data={'action': action, 'args': str(args),
                             'time': math.floor(time.time() * 1000), 'pageFile': 0})
