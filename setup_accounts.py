# coding: utf-8
# Author: Sebastian Dirk Lumpp
# Date: 08/07/2019
# Chair of Energy Economics and Application Technology
# Technical University of Munich

# import libraries, importantly web3
import json, math, random, time, func_fileIO, pause, web3
from web3 import Web3, IPCProvider, HTTPProvider

web3 = Web3(HTTPProvider("http://localhost:8501 "))
coinbase = web3.eth.coinbase

# paths
chain_name = "test_chain_01"
chain_location = "C:/Users/ga59zah/"
relative_path_to_key = "chain-data/keys/" + chain_name

# account details
num_acc_smgw = 20
num_acc_owners = 20
perc_pv = 80

password = "reghee"

gen_new_acc = input("Do you wish to generate a new list of SMGW and owner accounts? (y/n)")
# generate list of smart meter gateways, each with a generation type
if gen_new_acc == "y":
    list_new_acc_owner = []

    for i in range(num_acc_owners):
        list_new_acc_owner.append([web3.personal.newAccount(password), "owner"])

    file_owner = open(chain_location + chain_name + "/py_script_info/list_owner.csv","w")
    func_fileIO.writeStringArrayToNewFile(file_owner, list_new_acc_owner)
    file_owner.close()

    list_new_acc_smgw = []
    for i in range(num_acc_smgw):
        type = "pv" if random.randint(1,100) < perc_pv else "chp"
        # monte carlo over size here
        owner_index = random.randint(1,num_acc_owners)
        owner_account = list_new_acc_owner[owner_index][0]
        list_new_acc_smgw.append([web3.personal.newAccount(password), "smgw", type, str(random.randint(1,10)), owner_account, owner_index])

    file_smgw = open(chain_location + chain_name + "/py_script_info/list_smgw.csv","w")
    func_fileIO.writeStringArrayToNewFile(file_smgw, list_new_acc_smgw)
    file_smgw.close()

