#!/usr/bin/env python

import os
import sys
import traceback

from pyrosetta import *
from pyrosetta.rosetta import *

import numpy as np
from collections import OrderedDict
import time
import argparse
import subprocess
import glob
import random
import torch
import json

import util_protein_mpnn as mpnn_util

parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(parent, "include"))
from silent_tools import silent_tools


def cmd(command, wait=True):
    the_command = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )
    if not wait:
        return
    the_stuff = the_command.communicate()
    return str(the_stuff[0]) + str(the_stuff[1])


def range1(iterable):
    return range(1, iterable + 1)


#################################
# Parse Arguments
#################################

parser = argparse.ArgumentParser()
script_dir = os.path.dirname(os.path.realpath(__file__))

# I/O Arguments
parser.add_argument("-pdbdir", type=str, default="", help="The name of a directory of pdbs to run through the model")
parser.add_argument("-silent", type=str, default="", help="The name of a silent file to run through the model")
parser.add_argument(
    "-outpdbdir",
    type=str,
    default="outputs",
    help="The directory to which the output PDB files will be written, used if the -pdbdir arg is active",
)
parser.add_argument(
    "-outsilent",
    type=str,
    default="out.silent",
    help="The name of the silent file to which output structs will be written, used if the -silent arg is active",
)
parser.add_argument(
    "-runlist",
    type=str,
    default="",
    help="The path of a list of pdb tags to run, only active when the -pdbdir arg is active (default: ''; Run all PDBs)",
)
parser.add_argument(
    "-checkpoint_name",
    type=str,
    default="check.point",
    help="The name of a file where tags which have finished will be written (default: check.point)",
)

parser.add_argument(
    "-debug",
    action="store_true",
    default=False,
    help="When active, errors will cause the script to crash and the error message to be printed out (default: False)",
)

# Design Arguments
parser.add_argument(
    "-relax_cycles", type=int, default=1, help="The number of relax cycles to perform on each structure (default: 1)"
)
parser.add_argument(
    "-output_intermediates",
    action="store_true",
    help="Whether to write all intermediate sequences from the relax cycles to disk (default: False)",
)
parser.add_argument(
    "-seqs_per_struct",
    type=int,
    default="1",
    help="The number of sequences to generate for each structure (default: 1)",
)

# ProteinMPNN-Specific Arguments
parser.add_argument(
    "-checkpoint_path",
    type=str,
    default=os.path.join(script_dir, "ProteinMPNN/vanilla_model_weights/v_48_020.pt"),
    help=f"The path to the ProteinMPNN weights you wish to use, default {os.path.join(script_dir, 'ProteinMPNN/vanilla_model_weights/v_48_020.pt')}",
)
parser.add_argument(
    "-temperature",
    type=float,
    default=0.000001,
    help="The sampling temperature to use when running ProteinMPNN (default: 0.000001)",
)
parser.add_argument(
    "-augment_eps",
    type=float,
    default=0,
    help="The variance of random noise to add to the atomic coordinates (default 0)",
)
parser.add_argument(
    "-protein_features",
    type=str,
    default="full",
    help="What type of protein features to input to ProteinMPNN (default: full)",
)
parser.add_argument(
    "-omit_AAs",
    type=str,
    default="CX",
    help="A string of all residue types (one letter case-insensitive) that you would not like to use for design. Letters not corresponding to residue types will be ignored (default: CX)",
)
parser.add_argument(
    "-bias_AA_jsonl",
    type=str,
    default="",
    help="The path to a JSON file containing a dictionary mapping residue one-letter names to the bias for that residue eg. {A: -1.1, F: 0.7} (default: "
    "; no bias)",
)
parser.add_argument(
    "-bias_AA",
    type=str,
    default="",
    help="String representation mapping residue one-letter names to the bias for that residue eg. A:-1.1,F:0.7 (default: no bias)",
)
parser.add_argument(
    "-num_connections",
    type=int,
    default=48,
    help="Number of neighbors each residue is connected to. Do not mess around with this argument unless you have a specific set of ProteinMPNN weights which expects a different number of connections. (default: 48)",
)
parser.add_argument("-seed", type=int, default=None, help="Random seed - DANGER - will produce same output each time")

args = parser.parse_args(sys.argv[1:])

init_args = "-beta_nov16 -in:file:silent_struct_type binary -mute basic.io.database core.scoring"

if not args.debug:
    init_args += " -mute all"

xml_path = os.path.join(script_dir, "RosettaFastRelaxUtil.xml")
init_args += " -use_terminal_residues true"

if args.seed:
    # Deterministic mode using a fixed random seed
    torch.manual_seed(args.seed)
    random.seed(args.seed)
    np.random.seed(args.seed)
    init_args += f" -constant_seed -jran {args.seed}"

# Initialize PyRosetta
init(init_args)


class sample_features:
    """
    This is a struct which keeps all the features related to a single sample together
    """

    def __init__(self, pose, tag):
        self.pose = pose
        self.tag = os.path.basename(tag).split(".")[0]

    def parse_fixed_res(self):
        """
        Parse which residues are fixed from the residue remarks
        """

        # Iterate over the residue positions in this pose and check if they are fixed
        fixed_list = []

        endA = self.pose.split_by_chain()[1].total_residue()
        for resi in range1(endA):
            reslabels = self.pose.pdb_info().get_reslabels(resi)

            if len(reslabels) == 0:
                continue

            if str(self.pose.pdb_info().get_reslabels(resi)[1]).strip() == "FIXED":
                fixed_list.append(resi)
        # Get ordered unique chainIDs for the pose
        # The last chain (B) is the target and will have a fixed sequence
        self.chains = list(
            OrderedDict.fromkeys([self.pose.pdb_info().chain(i) for i in range1(self.pose.total_residue())])
        )

        # Create the fixed res dict, this will be input to ProteinMPNN
        self.fixed_res = {self.chains[0]: fixed_list, self.chains[1]: []}

    def thread_mpnn_seq(self, binder_seq):
        """
        Thread the binder sequence onto the pose being designed
        """
        rsd_set = self.pose.residue_type_set_for_pose(core.chemical.FULL_ATOM_t)

        for resi, mut_to in enumerate(binder_seq):
            resi += 1  # 1 indexing
            name3 = mpnn_util.aa_1_3[mut_to]
            new_res = core.conformation.ResidueFactory.create_residue(rsd_set.name_map(name3))
            self.pose.replace_residue(resi, new_res, True)


class ProteinMPNN_runner:
    """
    This class is designed to run the ProteinMPNN model on a single input. This class handles
    the loading of the model, the loading of the input data, the FastRelax cycles, and the processing of the output
    """

    def __init__(self, args, struct_manager):
        self.struct_manager = struct_manager

        if torch.cuda.is_available():
            print("Found GPU will run ProteinMPNN on GPU")
            self.device = "cuda:0"
        else:
            print("No GPU found, running ProteinMPNN on CPU")
            self.device = "cpu"

        self.mpnn_model = mpnn_util.init_seq_optimize_model(
            self.device,
            hidden_dim=128,
            num_layers=3,
            backbone_noise=args.augment_eps,
            num_connections=args.num_connections,
            checkpoint_path=args.checkpoint_path,
        )

        alphabet = "ACDEFGHIKLMNPQRSTVWYX"

        self.debug = args.debug

        self.temperature = args.temperature
        self.seqs_per_struct = args.seqs_per_struct
        self.omit_AAs = [letter for letter in args.omit_AAs.upper() if letter in list(alphabet)]

        # Parse AA bias settings from json
        if args.bias_AA_jsonl or args.bias_AA:
            if args.bias_AA_jsonl:
                assert not args.bias_AA, "Cannot use both -bias_AA_jsonl and -bias_AA at the same time"
                print(f"Found AA bias json file at {args.bias_AA_jsonl}")
                with open(args.bias_AA_jsonl, "r") as json_file:
                    json_list = list(json_file)
                for json_str in json_list:
                    bias_AA_dict = json.loads(json_str)
            else:
                print(f"Parsing AA bias from string {args.bias_AA}")
                bias_AA_dict = {}
                for entry in args.bias_AA.split(","):
                    if len(entry.split(":")) != 2:
                        raise Exception(f"Expected bias format: A:-1.1,F:0.7 but got {entry}")
                    AA, bias = entry.split(":")
                    if AA not in list(alphabet):
                        raise Exception(f"AA {AA} in -bias_AA argument is not a valid amino acid")
                    try:
                        bias = float(bias)
                    except:
                        raise Exception(f"Cannot convert bias {bias} to float in -bias_AA argument")
                    bias_AA_dict[AA] = bias

            self.bias_AAs_np = np.zeros(len(alphabet))
            for n, AA in enumerate(alphabet):
                if AA in list(bias_AA_dict.keys()):
                    self.bias_AAs_np[n] = bias_AA_dict[AA]
        else:
            # Not using AA bias
            self.bias_AAs_np = np.zeros(len(alphabet))

        # Configs for the FastRelax cycles
        self.relax_cycles = args.relax_cycles

    def relax_pose(self, mover, sample_feats):
        """
        Run FastRelax on the current pose
        """

        relaxT0 = time.time()

        print("Running FastRelax")

        mover.apply(sample_feats.pose)

        print(f"Completed one cycle of FastRelax in {int(time.time()) - relaxT0} seconds")

    def sequence_optimize(self, sample_feats):
        mpnn_t0 = time.time()

        # Once we have figured out pose I/O without Rosetta this will be easy to swap in
        pdbfile = "temp.pdb"
        sample_feats.pose.dump_pdb(pdbfile)

        feature_dict = mpnn_util.generate_seqopt_features(pdbfile, sample_feats.chains)

        os.remove(pdbfile)

        arg_dict = mpnn_util.set_default_args(self.seqs_per_struct, omit_AAs=self.omit_AAs)
        arg_dict["temperature"] = self.temperature

        masked_chains = sample_feats.chains[:-1]
        visible_chains = [sample_feats.chains[-1]]

        fixed_positions_dict = {pdbfile[: -len(".pdb")]: sample_feats.fixed_res}

        if self.debug:
            print(f"Fixed positions dict: {fixed_positions_dict}")

        sequences = mpnn_util.generate_sequences(
            self.mpnn_model,
            self.device,
            feature_dict,
            arg_dict,
            masked_chains,
            visible_chains,
            bias_AAs_np=self.bias_AAs_np,
            fixed_positions_dict=fixed_positions_dict,
        )

        if self.debug:
            print(f"Generated sequence(s): {sequences}")

        print(f"ProteinMPNN generated {len(sequences)} sequences in {int(time.time() - mpnn_t0)} seconds")

        return sequences

    def proteinmpnn(self, sample_feats):
        """
        Run ProteinMPNN sequence optimization on the pose, this does not use FastRelax
        """
        seqs_scores = self.sequence_optimize(sample_feats)

        # Iterate though each seq score pair and thread the sequence onto the pose
        # Then write each pose to a pdb file
        prefix = f"{sample_feats.tag}_dldesign"
        for idx, (seq, score) in enumerate(seqs_scores):
            sample_feats.thread_mpnn_seq(seq)

            outtag = f"{prefix}_{idx}"

            self.struct_manager.dump_pose(sample_feats.pose, outtag)

    def proteinmpnn_fastrelax(self, sample_feats):
        """
        Run ProteinMPNN plus FastRelax on the pose being designed
        """
        tot_t0 = time.time()
        design_counter = 0

        # We re-initialize the mover for each PDB to avoid remembering stuff from previous peptides, like peptide length
        objs = protocols.rosetta_scripts.XmlObjects.create_from_file(xml_path)
        # ParsedProtocol corresponds to PROTOCOLS block in the XML
        mover = objs.get_mover("ParsedProtocol")

        prefix = f"{sample_feats.tag}_dldesign"

        for cycle in range(args.relax_cycles):
            seqs_scores = self.sequence_optimize(sample_feats)

            seq, mpnn_score = seqs_scores[0]  # We know there is only one entry
            sample_feats.thread_mpnn_seq(seq)

            self.relax_pose(mover, sample_feats)

            if args.output_intermediates:
                tag = f"{prefix}_0_cycle{cycle}"
                self.struct_manager.dump_pose(sample_feats.pose, tag)

        # NOTE this is a change compared to the dl_binder_design repository
        # We do not perform this last sequence design - this ensures all designs are relaxed,
        # which enables running ddG calculation directly on the designed structure
        # Designs from intermediate cycles were already relaxed so this ensures consistency.
        #
        # seqs_scores = self.sequence_optimize(sample_feats)
        #
        # seq, mpnn_score = seqs_scores[0]  # We know there is only one entry
        # sample_feats.thread_mpnn_seq(seq)
        #
        # tag = f"{prefix}_0_cycle{args.relax_cycles}"
        # self.struct_manager.dump_pose(sample_feats.pose, tag)

    def run_model(self, tag, args):
        t0 = time.time()

        # Load the pose
        pose = self.struct_manager.load_pose(tag)

        # Initialize the features
        sample_feats = sample_features(pose, tag)

        # Parse the fixed residues from the pose remarks
        sample_feats.parse_fixed_res()

        # Now determine which type of run we are doing and execute it
        if args.relax_cycles > 0:
            if args.seqs_per_struct > 1:
                raise Exception("Cannot use -seqs_per_struct > 1 with -relax_cycles > 0")

            self.proteinmpnn_fastrelax(sample_feats)

        else:
            self.proteinmpnn(sample_feats)

        seconds = int(time.time() - t0)

        print(f"Struct: {pdb} reported success in {seconds} seconds")


class StructManager:
    """
    This class handles all of the input and output for the ProteinMPNN model. It deals with silent files vs. pdbs,
    checkpointing, and writing of outputs

    Note: This class could be moved to a separate file
    """

    def __init__(self, args):
        self.args = args

        self.silent = False
        if not args.silent == "":
            self.silent = True

            self.struct_iterator = silent_tools.get_silent_index(args.silent)["tags"]

            self.sfd_in = rosetta.core.io.silent.SilentFileData(rosetta.core.io.silent.SilentFileOptions())
            self.sfd_in.read_file(args.silent)

            self.sfd_out = core.io.silent.SilentFileData(
                args.outsilent, False, False, "binary", core.io.silent.SilentFileOptions()
            )

            self.outsilent = args.outsilent

        self.pdb = False
        if not args.pdbdir == "":
            self.pdb = True

            self.pdbdir = args.pdbdir
            self.outpdbdir = args.outpdbdir

            self.struct_iterator = sorted(glob.glob(os.path.join(args.pdbdir, "*.pdb")))

            if not os.path.exists(self.outpdbdir):
                os.makedirs(self.outpdbdir)

            # Parse the runlist and determine which structures to process
            if args.runlist != "":
                with open(args.runlist, "r") as f:
                    self.runlist = set([line.strip() for line in f])

                    # Filter the struct iterator to only include those in the runlist
                    self.struct_iterator = [
                        struct
                        for struct in self.struct_iterator
                        if os.path.basename(struct).split(".")[0] in self.runlist
                    ]

                    print(f"After filtering by runlist, {len(self.struct_iterator)} structures remain")

        # Assert that either silent or pdb is true, but not both
        assert self.silent ^ self.pdb, (
            f"Both silent and pdb are set to {args.silent} and {args.pdb} respectively. Only one of these may be active at a time"
        )

        # Setup checkpointing
        self.chkfn = args.checkpoint_name
        self.finished_structs = set()

        if os.path.isfile(self.chkfn):
            with open(self.chkfn, "r") as f:
                for line in f:
                    self.finished_structs.add(line.strip())

    def record_checkpoint(self, tag):
        """
        Record the fact that this tag has been processed.
        Write this tag to the list of finished structs
        """
        with open(self.chkfn, "a") as f:
            f.write(f"{tag}\n")

    def iterate(self):
        """
        Iterate over the silent file or pdb directory and run the model on each structure
        """

        # Iterate over the structs and for each, check that the struct has not already been processed
        for i, struct in enumerate(self.struct_iterator, start=1):
            tag = os.path.basename(struct).split(".")[0]
            if tag in self.finished_structs:
                print(f"{tag} has already been processed. Skipping")
                continue
            print(f"Processing PDB {i:,}/{len(self.struct_iterator):,}: {tag}")

            yield struct

    def dump_pose(self, pose, tag):
        """
        Dump this pose to either a silent file or a pdb file depending on the input arguments
        """
        if self.pdb:
            pdbfile = os.path.join(self.outpdbdir, tag + ".pdb")
            pose.dump_pdb(pdbfile)

        if self.silent:
            struct = self.sfd_out.create_SilentStructOP()
            struct.fill_struct(pose, tag)

            self.sfd_out.add_structure(struct)
            self.sfd_out.write_silent_struct(struct, self.outsilent)

    def load_pose(self, tag):
        """
        Load a pose from either a silent file or a pdb file depending on the input arguments
        """

        if not self.pdb and not self.silent:
            raise Exception("Neither pdb nor silent is set to True. Cannot load pose")

        if self.pdb:
            pose = pose_from_pdb(tag)

        if self.silent:
            pose = Pose()
            self.sfd_in.get_structure(tag).fill_pose(pose)

        return pose


####################
####### Main #######
####################

struct_manager = StructManager(args)
proteinmpnn_runner = ProteinMPNN_runner(args, struct_manager)

# Number of structures processed in this run, structures already listed in the checkpoint are not counted
num_processed = 0
num_failed = 0

for pdb in struct_manager.iterate():
    num_processed += 1
    if args.debug:
        proteinmpnn_runner.run_model(pdb, args)

    else:  # When not in debug mode the script will continue to run even when some poses fail
        t0 = time.time()

        try:
            proteinmpnn_runner.run_model(pdb, args)

        except KeyboardInterrupt:
            sys.exit("Script killed by Control+C, exiting")

        except:
            num_failed += 1
            seconds = int(time.time() - t0)
            print("Struct with tag %s failed in %i seconds:" % (pdb, seconds))
            # Print the full traceback, the failures are tolerated so this is the only record of what went wrong
            traceback.print_exc()

    # We are done with one pdb, record that we finished
    # Note that failed structures are checkpointed as well, so they are not retried when the script is rerun
    struct_manager.record_checkpoint(pdb)

if num_processed and num_failed == num_processed:
    raise ValueError("All structures failed to process, please check the error messages above for more information")
elif num_failed > 0:
    print(f"Finished processing {num_processed} structures with {num_failed} failures")
