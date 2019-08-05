# coding: utf-8
# Author: Sebastian Dirk Lumpp
# Date: 08/07/2019
# Chair of Energy Economics and Application Technology
# Technical University of Munich

# import libraries, importantly web3

import json, math, random, time, func_fileIO, pause, web3, func_BC, abi_smartcert
# from web3 import Web3, IPCProvider, HTTPProvider, personal


def py_addSMGW(web3_obj, contract, smgw, owner, password):
    web3_obj.personal.unlockAccount(smgw, password)
    contract.functions.addSMGW(smgw, owner).transact({"from": smgw})
    # function body to be filled


def py_createCert(web3_obj, contract, smgw, owner, password):
    web3_obj.personal.unlockAccount(smgw, password)
    contract.functions.createCert(owner).transact({"from": smgw})
    # function body to be filled

def py_waitForNextBlock(web3_obj, wait_msg):
    block_num_prev = web3_obj.eth.blockNumber
    while web3_obj.eth.blockNumber <= block_num_prev:
        pause.seconds(1)
        print(wait_msg)

def py_returnValCertByOwner(web3_obj, contract, owner, password):
    web3_obj.personal.unlockAccount(owner, password)
    list_valid_certs = contract.functions.returnValCertByOwner(owner).call({"from": owner})
    return list_valid_certs


def py_transferCert(web3_obj, contract, owner_old, owner_new, cert_id, password):
    web3_obj.personal.unlockAccount(owner_old, password)
    contract.functions.transferCert(owner_new, cert_id).transact({"from": owner_old})
    pass


def py_invalidateCert(web3_obj, contract, owner, cert_id, password):
    web3_obj.personal.unlockAccount(owner, password)
    contract.functions.invalidateCert(cert_id).transact({"from": owner})
    pass

def py_smart_cert(web3_obj, contract, sender, cert_id, password):
    web3_obj.personal.unlockAccount(sender, password)
    cert_details = contract.functions.smart_cert(cert_id).call({"from": sender})
    return cert_details
