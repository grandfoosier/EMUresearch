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

def evaluate(args):
    # file paths
    system_pred_file = args['output_file']
    gold_file = args['gold_file']
    model_file = args['save_dir'] + '/' + args['save_name'] if args['save_name'] is not None \
            else '{}/{}_parser.pt'.format(args['save_dir'], args['shorthand'])
    pretrain_file = '{}/{}.pretrain.pt'.format(args['save_dir'], args['shorthand'])

    # load pretrain
    pretrain = Pretrain(pretrain_file)

    # load model
    print("Loading model from: {}".format(model_file))
    use_cuda = args['cuda'] and not args['cpu']
    trainer = Trainer(pretrain=pretrain, model_file=model_file, use_cuda=use_cuda)
    loaded_args, vocab = trainer.args, trainer.vocab

    # load config
    for k in args:
        if k.endswith('_dir') or k.endswith('_file') or k in ['shorthand'] or k == 'mode':
            loaded_args[k] = args[k]

    # load data
    print("Loading data with batch size {}...".format(args['batch_size']))
    batch = DataLoader(args['eval_file'], args['batch_size'], loaded_args, pretrain, vocab=vocab, evaluation=True)

    if len(batch) > 0:
        print("Start evaluation...")
        preds = []
        for i, b in enumerate(batch):
            preds += trainer.predict(b)
    else:
        # skip eval if dev data does not exist
        preds = []

    # write to file and score
    batch.conll.set(['head', 'deprel'], [y for x in preds for y in x])
    batch.conll.write_conll(system_pred_file)

    if gold_file is not None:
        _, _, score = scorer.score(system_pred_file, gold_file)

        print("Parser score:")
        print("{} {:.2f}".format(args['shorthand'], score*100))
