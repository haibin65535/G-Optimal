import argparse
from model import Template, GINNet, GCNNet, GATNet
import numpy as np
import random
import torch
from itertools import product


def parse_args(jupyter = False):
    
    str2bool = lambda x: x.lower() == "true"
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--step_size', type=float, default=0.001)
    parser.add_argument('--min_lr', type=float, default=1e-6)
    #################### toy example #######################
    parser.add_argument('--pretrain', type=int, default=30)
    parser.add_argument('--data_num', type=int, default=2000)
    parser.add_argument('--node_num', type=int, default=15)
    parser.add_argument('--max_degree', type=int, default=10)
    parser.add_argument('--feature_dim', type=int, default=-1)
    parser.add_argument('--noise', type=float, default = 0.1)
    parser.add_argument('--num_classes', type=int, default=4)
    parser.add_argument('--shape_num', type=int, default=1)
    parser.add_argument('--bias', type=float, default=0.1)
    parser.add_argument('--penalty_weight', default=0.1, type=float, help='penalty weight')
    parser.add_argument('--train_type', type=str, default="base", help="irm, dro, base")
    parser.add_argument('--drop_out', type=float, default = 0.5, help="dopr in net")
    parser.add_argument('--tune_items', type=int, default = 70, help="tune iters")

    
    parser.add_argument('--epochs', type=int, default = 100)
    parser.add_argument('--batch_size', type=int, default=128)
    
    parser.add_argument('--the', type=int, default=0)
    parser.add_argument('--with_random', type=str2bool, default=True)
    parser.add_argument('--eval_random', type=str2bool, default=False)
    parser.add_argument('--normalize', type=str2bool, default=False)
    parser.add_argument('--save_model', type=str2bool, default=False)
    parser.add_argument('--inference', type=str2bool, default=False)
    parser.add_argument('--without_node_attention', type=str2bool, default=False)
    parser.add_argument('--without_edge_attention', type=str2bool, default=False)
    parser.add_argument('--stop_usemgda', type=str2bool, default=False)
    parser.add_argument('--k', type=int, default=3)

    #################### training method settings#######################
    parser.add_argument('--train_model', type=str, default="swl", help="swl, mgda")
    parser.add_argument('--weight_grad_modle', type=str, default="norm", help="norm, mean")
    parser.add_argument('--mgda_model', type=str, default="none", help="loss, loss+, l2")
    parser.add_argument('--mgda_with_double_co', type=str2bool, default= False)
    parser.add_argument('--mgda_with_loss_4', type=str2bool, default= False)
    parser.add_argument('--replace_co', type=str2bool, default= False)
    parser.add_argument('--double_co_use_mgda', type=str2bool, default= False)
    parser.add_argument('--accsave', type=str, default= "")

    #################### Causal GNN settings #######################
    parser.add_argument('--layers', type=int, default=3)
    parser.add_argument('--s', type=float, default = 0.5)
    parser.add_argument('--m', type=float, default=1)
    parser.add_argument('--ge', type=float, default=0.5)
    parser.add_argument('--harf_hidden', type=float, default=0.5)
    parser.add_argument('--cat_or_add', type=str, default="add")
    ##################### baseline training ######################
    parser.add_argument('--num_layers', type=int, default=3)

    parser.add_argument('--folds', type=int, default = 10)
    parser.add_argument('--fc_num', type=str, default="222")
    parser.add_argument('--data_root', type=str, default="/home/zz/wenhaibin/CAL/CAL-sp/data/MNISTSP/")
    parser.add_argument('--save_dir', type=str, default="debug")
    parser.add_argument('--dataset', type=str, default="MUTAG")
    parser.add_argument('--epoch_select', type=str, default='test_max')
    parser.add_argument('--model', type=str, default="CausalGCN", help="GCN, GIN")
    parser.add_argument('--hidden', type=int, default=128)

    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--lr', type=float, default=0.01)
    parser.add_argument('--lr_decay_factor', type=float, default=0.5)
    parser.add_argument('--lr_decay_step_size', type=int, default=500)
    parser.add_argument('--weight_decay', type=float, default=0)
    parser.add_argument('--global_pool', type=str, default="sum")
    parser.add_argument('--gpu_id', type=str, default="0")
    parser.add_argument('--tune',type=str2bool,default = False)
    args = parser.parse_args(args=[]) if jupyter else parser.parse_args()
    if not jupyter :
        print_args(args)
    setup_seed(args.seed)
    
    return args

def print_args(args, str_num=80):
    for arg, val in args.__dict__.items():
        print(arg + '.' * (str_num - len(arg) - len(str(val))) + str(val))
    print()


def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def get_model(args):

    def model_func1(num_features, num_classes):
        return GCNNet(args,num_features, num_classes, args.hidden,dropout = args.drop_out)  

    def model_func2(num_features, num_classes):
        return GINNet(args,num_features, num_classes, args.hidden,dropout = args.drop_out) 
    
    def model_func3(num_features, num_classes):
        return GATNet(args,num_features, num_classes, args.hidden,dropout = args.drop_out) 

    def model_func4(num_features, num_classes):
        return Template(num_features, num_classes, args,header_mdoe = 'GCN') 

    def model_func5(num_features, num_classes):
        return Template(num_features, num_classes, args,header_mdoe = 'GIN')

    def model_func6(num_features, num_classes):
        return Template(num_features, num_classes, args,header_mdoe = 'GAT')

    if args.model == "GCN":
        model_func = model_func1
    elif args.model == "GIN":
        model_func = model_func2
    elif args.model == "GAT":
        model_func = model_func3
    elif args.model == "CausalGCN":
        model_func = model_func4
    elif args.model == "CausalGIN":
        model_func = model_func5
    elif args.model == "CausalGAT":
        model_func = model_func6
    else:
        assert False
    return model_func

def create_n_filter_triples(datasets, 
                            feat_strs=['deg+odeg100'], 
                            nets=['ResGCN'], 
                            gfn_add_ak3=True,
                            gfn_reall=True, 
                            reddit_odeg10=True,
                            dd_odeg10_ak1=True):
    triples = [(d, f, n) for d, f, n in product(datasets, feat_strs, nets)]
    triples_filtered = []
    for dataset, feat_str, net in triples:
        # Replace degree feats for REDDIT datasets (less redundancy, faster).
        if reddit_odeg10 and dataset in ['REDDIT-BINARY', 'REDDIT-MULTI-5K', 'REDDIT-MULTI-12K']:
            feat_str = feat_str.replace('odeg100', 'odeg10')
        # Replace degree and akx feats for dd (less redundancy, faster).
        if dd_odeg10_ak1 and dataset in ['DD']:
            feat_str = feat_str.replace('odeg100', 'odeg10')
            feat_str = feat_str.replace('ak3', 'ak1')
        triples_filtered.append((dataset, feat_str, net))
    return triples_filtered