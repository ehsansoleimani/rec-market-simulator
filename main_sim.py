coding: utf - 8

# Author: Sebastian Dirk Lumpp
# Date: 08/07/2019
# Chair of Energy Economics and Application Technology
# Technical University of Munich

# import libraries

import json
import pause
import web3
import random
import func_BC
import abi_smartcert
import func_fileIO
from web3 import Web3, IPCProvider, HTTPProvider

# paths
chain_name = "test_chain_01"
chain_location = "C:/Users/ga59zah/"
relative_path_to_key = "chain-data/keys/" + chain_name

# load all accounts
file_acc = open(chain_location + chain_name + "/py_script_info/list_smgw.csv", "r")
list_acc = func_fileIO.readStringArrayFromFile(file_acc)
file_acc.close()

# load all owners
file_owner = open(chain_location + chain_name + "/py_script_info/list_owner.csv", "r")
list_owner = func_fileIO.readStringArrayFromFile(file_owner)
file_owner.close()

# load generation curves
file_gen = open(chain_location + chain_name + "/py_script_info/input_gen.csv", "r")
list_gen = func_fileIO.readFloatArrayFromFile(file_gen)
file_gen.close()
pv_curve, chp_curve = list_gen[0], list_gen[1]

# connect to chain
# Establish RPC connection with running node.

web3 = Web3(HTTPProvider("http://localhost:8501"))
pw = "reghee"

# configure smart contract (already deployed on chain manually)

contract_address = web3.toChecksumAddress(0x82b8e36739ce115e6b8b1102a61d9f223209fab2)
contract_abi = json.loads(abi_smartcert.returnABIstr())
contract = web3.eth.contract(abi=contract_abi, address=contract_address)

for entry in list_acc:
    func_BC.py_addSMGW(web3, contract, web3.toChecksumAddress(entry[0]), web3.toChecksumAddress(entry[4]), pw)

# wait for new block before beginning simulation
func_BC.py_waitForNextBlock(web3, "Wait for new block before beginning simulation...")
smgw_cum_energy = [0] * 100

# define "cycle" and "hour" variable
# as this chain will run in accelerated time, each cycle(block) will represent 15 minutes
cycle = 1
hour, hour_previous, day = 0, 0, 0
step_min = 15

n = int(60 / step_min)
sim_days = 2
# define certificate size (in kWh)
cert_size = 1

cert = []
owner_cert_total = [0] * len(list_owner)

energy_bill = [0] * len(list_owner)
fl_energy = [0] * len(list_owner)
int_energy = [0] * len(list_owner)

for step in range(sim_days * 24 * n):
    temp_counter = 0
    for smgw in list_acc:
        power_inst = pv_curve[hour] if smgw[2] == "pv" else chp_curve[hour]
        # 0.25 is the quarter hour, smgw[3] is the size of the plant
        smgw_cum_energy[temp_counter] += power_inst * float(step_min / 60) * float(smgw[3])
        temp_counter += 1

    for i in range(len(smgw_cum_energy)):
        while smgw_cum_energy[i] >= cert_size:
            smgw_cum_energy[i] -= cert_size
            # creat a certificate energy(cert_size), owner, cert_id
            func_BC.py_createCert(web3, contract, list_acc[i][0], list_acc[i][4], pw)
            owner_index = list_acc[i][6]
            cert.append([cert_size, owner_index, 1])
            owner_cert_total[owner_index] += cert_size

    for i in range(len(list_owner)):
        energy_bill[i] += float(step_min / 60) * float(random.randint(1, 10) / 10)

    cycle += 1
    if cycle == n:
        hour += 1
        cycle = 1
    if hour == 24:
        day += 1
        hour = 0

    if hour == 12 or hour == 0:
        for i in range(len(list_owner)):
            if energy_bill[i] > 0:
                fl_energy[i] = energy_bill[i] % cert_size
                int_energy[i] = energy_bill[i] - fl_energy[i]
                while int_energy[i] > 0:
                    if owner_cert_total[i] > cert_size:
                        for k in range(len(cert)):
                            if cert[k][0] == cert_size and cert[k][1] == i and cert[k][2] == 1:
                                # invalidate the cert id(k)

                                owner_cert_total[i] -= cert_size
                                energy_bill[i] -= cert_size
                                cert[k][2] = 0
                                int_energy[i] -= cert_size
                if owner_cert_total[i] > 0:
                    for k in range(len(cert)):
                        if cert[k][0] < cert_size and cert[k][1] == i & cert[k][2] == 1:
                            if cert[k][0] <= fl_energy[i]:
                                # invalidate the cert[k]
                                owner_cert_total[i] -= cert[k][0]
                                energy_bill[i] -= cert[k][0]
                                cert[k][2] = 0
                                fl_energy[i] -= cert[k][0]
                            else:
                                # splt cert[k] into cert[k][energy-fl_energy][i][1] & cert[len(cert)+1][fl_energy][i][1]
                                # invalidate cert[len(cert)+1][fl_energy][i][1]
                                owner_cert_total[i] -= fl_energy[i]
                                energy_bill[i] -= fl_energy[i]
                                cert[k][0] -= fl_energy[i]
                                cert.append([fl_energy[i], i, 0])
                                fl_energy[i] = 0
                if owner_cert_total[i] > 0:
                    for k in range(len(cert)):
                        if cert[k][0] == cert_size and cert[k][1] == i and cert[k][2] == 1:
                            # split cert[k] into cert[k][cert_size - fl_energy][owner][1] & cert[len(cert)+1][fl_energy][i][1]
                            # invalidate cert[len(cert)+1][fl_energy][i][1]
                            owner_cert_total[i] -= fl_energy[i]
                            energy_bill[i] -= fl_energy[i]
                            cert[k][0] -= fl_energy[i]
                            cert.append([fl_energy[i], i, 1])
        for i in range(len(list_owner)):
            if energy_bill[i] > 0:
                fl_energy[i] = energy_bill[i] % cert_size
                int_energy[i] = energy_bill[i] - fl_energy[i]
                while int_energy[i] > 0:
                    for l in range(len(list_owner)):
                        if owner_cert_total[l] > cert_size:
                            for k in range(len(cert)):
                                if cert[k][0] == cert_size and cert[k][1] == l and cert[k][2] == 1:
                                    owner_cert_total[l] -= cert_size
                                    energy_bill[i] -= cert_size
                                    cert[k][2] = 0
                                    # transfer cert[k][cert_size][l][1] to owner i
                                    # invalidate the cert[k]
                                    int_energy[i] -= cert_size

                for k in range(len(cert)):
                    if fl_energy[i] > 0:
                        if cert[k][0] < cert_size and cert[k][1] != i and cert[k][2] == 1:
                            if cert[k][0] <= fl_energy[i]:
                                # transfer cert[k][owner][1] to owner i
                                # invalidate the cert[k]
                                owner_cert_total[cert[k][1]] -= cert[k][0]
                                energy_bill[i] -= cert[k][0]
                                cert[k][2] = 0
                                fl_energy[i] -= cert[k][0]
                            else:
                                # splt cert[k] into cert[k][energy-fl_energy][owner][1] & cert[len(cert)+1][fl_energy][owner][1]
                                # transfer cert[len(cert)+1][fl_energy][owner][1] to i
                                # invalidate cert[len(cert)+1][fl_energy][i][1]
                                owner_cert_total[cert[k][1]] -= fl_energy
                                energy_bill[i] -= fl_energy
                                cert[k][0] -= fl_energy
                                cert.append([fl_energy[i], cert[k][1], 0])
                                fl_energy[i] = 0
                if fl_energy[i] > 0:
                    for k, certificate in enumerate(cert):
                        if certificate[0] == cert_size and certificate[1] != 1 and certificate[2] == 1:
                            # split cert[k] into cert[k][energy-fl_energy][owner][1] & cert[len(cert)+1][fl_energy][owner][1]
                            # transfer cert[len(cert)+1][fl_energy][owner][1] to i
                            # invalidate cert[len(cert)+1][fl_energy][i][1]
                            owner_cert_total[certificate[1]] -= fl_energy[i]
                            energy_bill[i] -= fl_energy[i]
                            cert.append([fl_energy[i], i, 0])
                            fl_energy[i] = 0

    # if smgw surpasses threshold, generate certificate for owner(TX), decrement energy "account"
    for i, cum_energy in enumerate(smgw_cum_energy):
        while cum_energy >= cert_size:
            smgw_cum_energy[i] -= cert_size
            cum_energy -= cert_size
            print("Generating certificate for owner # " + str(i) + ". " + str(smgw_cum_energy[i]) + " kWh remaining.")
            func_BC.py_createCert(web3, contract, list_acc[i][0], list_acc[i][4], pw)
            owner_index = list_acc[i][6]
            owner_cert[owner_index] += cert_size

    cycle += 1
    if cycle == n:
        hour += 1
        cycle = 1
    if hour == 24:
        day += 1
        hour = 0

    for i, cert in enumerate(owner_cert):
        cert_consume = float(random.randint(1, 10) / 10)
        owner_cert[i] -= cert_consume

    for i, cert in enumerate(owner_cert):
        if cert < 0:
    # buy certificate from another owner

for sim_step in range(100):
    # for each smgw, calculate generation in this time step, increment energy

    temp_counter = 0
    for smgw in list_acc:
        power_inst = pv_curve[hour] if smgw[2] == "pv" else chp_curve[hour]
        # 0.25 is the quarter hour, smgw[3] is the size of the plant
        smgw_cum_energy[temp_counter] += power_inst * float(step_min / 60) * float(smgw[3])
        temp_counter += 1

    # if smgw surpasses threshold, generate certificate for owner(TX), decrement energy "account"
    for i, cum_energy in enumerate(smgw_cum_energy):
        while cum_energy >= cert_size:
            smgw_cum_energy[i] -= cert_size
            cum_energy -= cert_size
            print("Generating certificate for owner # " + str(i) + ". " + str(smgw_cum_energy[i]) + " kWh remaining.")
            func_BC.py_createCert(web3, contract, list_acc[i][0], list_acc[i][4], pw)

    # for each owner, read all valid certificates off blockchain
    list_cert_by_owner = []
    for account in list_acc:
        list_cert_by_owner.append(func_BC.py_returnValCertByOwner(web3, contract, account[4], pw))

    # for each owner, at end of day transfer all valid certificates to next participant on the list
    if hour_previous > hour:
        for i, account in enumerate(list_acc):
            for cert_id in list_cert_by_owner[i]:
                if i < len(list_acc) - 1:
                    func_BC.py_transferCert(web3, contract, account[4], list_acc[i + 1][4], cert_id, pw)
                else:
                    func_BC.py_transferCert(web3, contract, account[4], list_acc[0][4], cert_id, pw)
    # send out transactions transferring all valid certificates to next participant on list

    # for each owner, invalidate all existing, valid certificates
    # if cycle == 1:
    #     for i, sublist in enumerate(list_cert_by_owner):
    #         for cert_id in sublist:
    #             func_BC.py_invalidateCert(web3, contract, list_acc[i][4], cert_id, pw)
    #     pass
    # invalidate all existing certificates in transactions

    func_BC.py_waitForNextBlock(web3,
                                "Wait for new block before beginning simulation step " + str(sim_step + 1) + "...")
    print(list_cert_by_owner)
    # prepare for next step
    cycle = cycle + 1 if cycle < 95 else 0  # 95 else 0
    hour, hour_previous = int(cycle / 4), hour
    print(cycle)
    print(hour)
    print(hour_previous)
