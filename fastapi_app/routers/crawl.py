import os
import json
import requests

from urllib import request, parse
from bs4 import BeautifulSoup
from fastapi import Response, status

from variables import config

