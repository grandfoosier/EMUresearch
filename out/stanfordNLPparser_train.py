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
def train(args):
    utils.ensure_dir(args['save_dir'])
    model_file = args['save_dir'] + '/' + args['save_name'] if args['save_name'
        ] is not None else '{}/{}_parser.pt'.format(args['save_dir'], args[
        'shorthand'])
    vec_file = utils.get_wordvec_file(args['wordvec_dir'], args['shorthand'])
    pretrain_file = '{}/{}.pretrain.pt'.format(args['save_dir'], args[
        'shorthand'])
    pretrain = Pretrain(pretrain_file, vec_file, args['pretrain_max_vocab'])
    print('Loading data with batch size {}...'.format(args['batch_size']))
    train_batch = DataLoader(args['train_file'], args['batch_size'], args,
        pretrain, evaluation=False)
    vocab = train_batch.vocab
    dev_batch = DataLoader(args['eval_file'], args['batch_size'], args,
        pretrain, vocab=vocab, evaluation=True)
    system_pred_file = args['output_file']
    gold_file = args['gold_file']
    if len(train_batch) == 0 or len(dev_batch) == 0:
        print('Skip training because no data available...')
        sys.exit(0)
    print('Training parser...')
    trainer = Trainer(args=args, vocab=vocab, pretrain=pretrain, use_cuda=
        args['cuda'])
    global_step = 0
    max_steps = args['max_steps']
    dev_score_history = []
    best_dev_preds = []
    current_lr = args['lr']
    global_start_time = time.time()
    format_str = '{}: step {}/{}, loss = {:.6f} ({:.3f} sec/batch), lr: {:.6f}'
    using_amsgrad = False
    last_best_step = 0
    train_loss = 0
    while True:
        do_break = False
        for i, batch in enumerate(train_batch):
            start_time = time.time()
            global_step += 1
            loss = trainer.update(batch, eval=False)
            train_loss += loss
            if global_step % args['log_step'] == 0:
                duration = time.time() - start_time
                print(format_str.format(datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S'), global_step, max_steps, loss,
                    duration, current_lr))
            if global_step % args['eval_interval'] == 0:
                print('Evaluating on dev set...')
                dev_preds = []
                for batch in dev_batch:
                    preds = trainer.predict(batch)
                    dev_preds += preds
                dev_batch.conll.set(['head', 'deprel'], [y for x in
                    dev_preds for y in x])
                dev_batch.conll.write_conll(system_pred_file)
                _, _, dev_score = scorer.score(system_pred_file, gold_file)
                train_loss = train_loss / args['eval_interval']
                print('step {}: train_loss = {:.6f}, dev_score = {:.4f}'.
                    format(global_step, train_loss, dev_score))
                train_loss = 0
                if len(dev_score_history) == 0 or dev_score > max(
                    dev_score_history):
                    last_best_step = global_step
                    trainer.save(model_file)
                    print('new best model saved.')
                    best_dev_preds = dev_preds
                dev_score_history += [dev_score]
                print('')
            if global_step - last_best_step >= args['max_steps_before_stop']:
                if not using_amsgrad:
                    print('Switching to AMSGrad')
                    last_best_step = global_step
                    using_amsgrad = True
                    trainer.optimizer = optim.Adam(trainer.model.parameters
                        (), amsgrad=True, lr=args['lr'], betas=(0.9, args[
                        'beta2']), eps=1e-06)
                else:
                    do_break = True
                    break
            if global_step >= args['max_steps']:
                do_break = True
                break
        if do_break:
            break
        train_batch.reshuffle()
    print('Training ended with {} steps.'.format(global_step))
    best_f, best_eval = max(dev_score_history) * 100, np.argmax(
        dev_score_history) + 1
    print('Best dev F1 = {:.2f}, at iteration = {}'.format(best_f, 
        best_eval * args['eval_interval']))
