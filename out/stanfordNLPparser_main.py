import sys
import os
import shutil
import time
from datetime import datetime
import argparse
import numpy as np
import random
import torch
from torch import nn, optim
from stanfordnlp.models.depparse.data import DataLoader
from stanfordnlp.models.depparse.trainer import Trainer
from stanfordnlp.models.depparse import scorer
from stanfordnlp.models.common import utils
from stanfordnlp.models.common.pretrain import Pretrain
def main():
    args = parse_args()
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)
    if args.cpu:
        args.cuda = False
    elif args.cuda:
        torch.cuda.manual_seed(args.seed)
    args = vars(args)
    print('Running parser in {} mode'.format(args['mode']))
    if args['mode'] == 'train':
        train(args)
    else:
        evaluate(args)
