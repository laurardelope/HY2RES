from src.base_module import *
import os
import datetime
import numpy as np
import pandas as pd
from statistics import mean
import math
#import matplotlib as mpl
#import matplotlib.pyplot as plt
from tqdm import tqdm
from datetime import datetime
from keras.models import load_model
import tensorflow as tf
tf.debugging.experimental.disable_dump_debug_info()

class Module:
    def __init__(self, param):

        print("Init module")
        self.name = "Hy2Res module"

    def reset(self):
        print(f"Reset module {self.name}")

    def run(self):
        print("Run module")


