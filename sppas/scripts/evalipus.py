#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    scripts.evalipus.py
    ~~~~~~~~~~~~~~~~~~~

    ... a script to evaluate an IPUs segmentation vs a reference segmentation.

    1. Evaluate the match of ref in hyp
    ------------------------------------

    No speech in ref has to be assigned to a silence in hyp => no need to
    listen the whole signal, only listen the ipus the system detected...

    For each IPU in the reference, an IPU in the hypothesis should exist.
    It's important because if not it means the user will have to listen
    the whole content of the audio file to add such missing ipus which is time
    consuming. If none of the ipus are missed by the system, the user will
    have only to listen the ipus the system found and to check boundaries
    of such ipus by moving or ignoring them and by adding some new ones.

    We check it with the middle position of the reference. An ipu in the hyp
    must exist at this position in time.

    Examples:

       ref:  #   |      ipu_1    |  #  |     ipu_2   |  #  |   ipu_3  |  #

    100% good are:
       hyp1: #     |    ipu_a   |  #    |     ipu_b  |  #    |  ipu_c |  #
       hyp2:    ipu_a        |  #    |     ipu_b                    |  #
       hyp3:    # |                           ipu_a                    |  #
       hyp4: #  |ipu_a |  #              |    ipu_c |      #   |  ipu_d |  #

    Not good are (implies the user must listen the whole audio to check):
       hyp5: #  |ipu_a |  # | ipu_b  | # |    ipu_c |      #   |  ipu_d |  #
       hyp6: #     |    ipu_a   |  #    |     ipu_b  |            #

    We'll find if some points in time of the ipus in the ref are matching
    an ipu in the hyp.

    Discussion:
    Clearly, this is not the best measure to evaluate the task but it
    gives an important information: how many ipus of the ref are missing in
    the hyp, so does the user will have to listen the whole audio to check
    the result or not!
    hyp6 is much more critical than hyp5: 2 different evals.

    But hyp3 is clearly problematic and other evaluation metrics must be
    analyzed!

    2. Evaluate the match of hyp in ref
    -----------------------------------

    how many manual corrections have to be applied on the ipus the system
    found?

        a. merge 2 ipus (hyp5)

            ref:     #    |         ipu        |    #
            hyp:     #    | ipu    |  #  | ipu |    #

        b. split an ipu (hyp6)

            ref:    #   |  ipu    |  #  |  ipu  |   #
            hyp:    #   |           ipu         |   #

        c. delete an ipu (false positive)

            ref:               #
            hyp:    #      | ipu  |    #

        d. move boundaries (start, end or both)

            ref:    #     |    ipu     |   #
            hyp:    #   |      ipu   |    #

"""
import sys
import codecs
import os.path
import logging
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas import sppasRW
from sppas import sppasTranscription, sppasTier
from sppas import sppasLocation, sppasInterval
from sppas import sppasLabel, sppasTag
from sppas import setup_logging
import sppas.src.anndata.aio


# ---------------------------------------------------------------------------
# Functions to manage input annotated files


def get_tier(filename, tier_idx):
    """Return the tier of the given index in an annotated file.

    :param filename: (str) Name of the annotated file
    :param tier_idx: (int) Index of the tier to get
    :returns: sppasTier or None

    """
    try:
        parser = sppasRW(filename)
        trs_input = parser.read(filename)
    except:
        return None
    if tier_idx < 0 or tier_idx >= len(trs_input):
        return None

    return trs_input[tier_idx]

# ---------------------------------------------------------------------------


def get_tiers(ref_filename, hyp_filename, ref_idx=0, hyp_idx=0):
    """Return a reference and an hypothesis tier from annotated files.

    :param ref_filename: Name of the annotated file with the reference
    :param hyp_filename: Name of the annotated file with the hypothesis
    :param ref_idx: (int)
    :param hyp_idx: (int)

    :returns: a tuple with sppasTier or None for both ref and hyp

    """
    ref_tier = get_tier(ref_filename, ref_idx)
    hyp_tier = get_tier(hyp_filename, hyp_idx)

    return ref_tier, hyp_tier


# ---------------------------------------------------------------------------


def is_silence(ann):
    """Check if the given annotation is a silence.

    :param ann: (sppasAnnotation)
    :returns: (bool)

    """
    stamp = ann.serialize_labels()
    if stamp == "#" or stamp == "silence" or "gpf_" in stamp:
        return True
    return False

# ---------------------------------------------------------------------------


def get_nb_ipus(tier):
    """Return the number of ipus of the given tier.

    :param tier: (sppasTier)
    :returns: (int)

    """
    return len([ann for ann in tier if is_silence(ann) is False])

# ---------------------------------------------------------------------------


def get_ann_infos(ann):
    """Return begin, end, serialized labels of an annotation."""
    begin = ann.get_location().get_best().get_begin().get_midpoint()
    end = ann.get_location().get_best().get_end().get_midpoint()
    stamp = ref_ann.serialize_labels(separator=" ", empty="", alt=False)

    return begin, end, stamp

# ---------------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------------


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s -fr ref -fh hyp [options]",
        description="Compare two IPUs segmentation, "
                    "in the scope of evaluating an hypothesis vs a reference.")

    verbosity = parser.add_mutually_exclusive_group()

    verbosity.add_argument(
        "--quiet",
        action='store_true',
        help="Disable the verbosity")

    verbosity.add_argument(
        "--debug",
        action='store_true',
        help="Highest level of verbosity")

    # Add arguments for input/output files
    # ------------------------------------

    parser.add_argument(
        "-fr",
        metavar="file",
        required=True,
        help='Input annotated file/directory name of the reference.')

    parser.add_argument(
        "-fh",
        metavar="file",
        required=True,
        help='Input annotated file/directory name of the hypothesis.')

    parser.add_argument(
        "-tr",
        metavar="file",
        type=int,
        default=1,
        required=False,
        help='Tier number of the reference (default=1).')

    parser.add_argument(
        "-th",
        metavar="file",
        type=int,
        default=1,
        required=False,
        help='Tier number of the hypothesis (default=1).')

    parser.add_argument(
        "-o",
        metavar="path",
        required=False,
        help='Path for the output files.')

    # Add arguments for the options
    # -----------------------------

    parser.add_argument(
        "-d",
        metavar="delta",
        required=False,
        type=float,
        default=0.2,
        help='Delta max value for the recall/precision estimation (default=0.2).')

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # Global variables
    # -----------------------------------------------------------------------

    idxref_tier = args.tr - 1
    idxhyp_tier = args.th - 1

    # Redirect all messages to logging
    # --------------------------------

    level = 15
    if args.quiet:
        level = 25
    elif args.debug:
        level = 0
    setup_logging(level, None)

    # -----------------------------------------------------------------------
    # Prepare file names to be analyzed, as a list of tuples (ref,hyp)
    # -----------------------------------------------------------------------

    files = []  # List of tuples: (ref_filename, hyp_filename)
    out_path = None
    if args.o:
        out_path = args.o
        if not os.path.exists(out_path):
            os.mkdir(out_path)

    if os.path.isfile(args.fh) and os.path.isfile(args.fr):
        hyp_filename, extension = os.path.splitext(args.fh)
        out_basename = os.path.basename(hyp_filename)
        if out_path is None:
            out_path = os.path.dirname(hyp_filename)
        out_name = os.path.join(out_path, out_basename)

        files.append((os.path.basename(args.fr), os.path.basename(args.fh)))
        ref_directory = os.path.dirname(args.fr)
        hyp_directory = os.path.dirname(args.fh)

    elif os.path.isdir(args.fh) and os.path.isdir(args.fr):
        if out_path is None:
            out_path = args.fh
        out_name = os.path.join(out_path, "ipus")

        ref_directory = args.fr
        hyp_directory = args.fh

        ref_files = []
        hyp_files = []
        for fr in os.listdir(args.fr):
            if os.path.isfile(os.path.join(ref_directory, fr)):
                ref_files.append(fr)
        for fh in os.listdir(args.fh):
            if os.path.isfile(os.path.join(hyp_directory, fh)):
                hyp_files.append(os.path.basename(fh))

        for fr in ref_files:
            base_fr, ext_fr = os.path.splitext(fr)
            if not ext_fr.lower() in sppas.src.anndata.aio.extensions:
                continue
            for fh in hyp_files:
                base_fh, ext_fh = os.path.splitext(fh)
                if not ext_fh.lower() in sppas.src.anndata.aio.extensions:
                    continue
                if fh.startswith(base_fr):
                    files.append((fr, fh))

    else:
        print("Both reference and hypothesis must be of the same type: "
              "file or directory.")
        sys.exit(1)

    if len(files) == 0:
        print("No matching hyp/ref files. Nothing to do!")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # Evaluation is here
    # -----------------------------------------------------------------------

    files_ok = []  # List of tuples: (ref_filename, hyp_filename)

    nb_ipus_ref_total = 0
    nb_ipus_hyp_total = 0

    nb_ref_perfect_match_total = 0
    nb_ref_not_match_total = 0
    nb_ref_several_match_total = 0
    
    nb_hyp_merge_ipus_total = 0
    nb_hyp_split_ipus_total = 0
    nb_hyp_not_match_total = 0
    nb_hyp_move_bounds_total = 0

    for f in files:

        logging.info(" * File: {:s}".format(os.path.basename(f[1])))

        # Get the hyp/ref tiers
        # ---------------------
        fr = os.path.join(ref_directory, f[0])
        fh = os.path.join(hyp_directory, f[1])
        ref_tier, hyp_tier = get_tiers(fr, fh, idxref_tier, idxhyp_tier)
        if ref_tier is None or hyp_tier is None:
            logging.error("No ipus found in tiers. Nothing to do. ")
            continue
        files_ok.append((f[0], f[1]))

        ref_tier.set_radius(0.001)
        hyp_tier.set_radius(0.001)

        # transcription to store the results of this file
        trs = sppasTranscription("eval-searchforipus")

        # ----------------------------------------------------------------------------
        # Number of ipus in ref and hyp

        nb_ipus_ref = get_nb_ipus(ref_tier)
        nb_ipus_ref_total += nb_ipus_ref
        logging.info('    - number of ipus in ref: {:d}'.format(nb_ipus_ref))

        nb_ipus_hyp = get_nb_ipus(hyp_tier)
        logging.info('    - number of ipus in hyp: {:d}'.format(nb_ipus_hyp))
        nb_ipus_hyp_total += nb_ipus_hyp

        # ----------------------------------------------------------------------------
        # Match ipus of ref in hyp

        logging.info('    - Match ipus of ref in hyp: ')

        nb_ref_not_match = 0
        nb_ref_several_match = 0
        nb_ref_perfect_match = 0
        tier_ref_result = ref_tier.copy()
        tier_ref_result.set_name('Ref-in-hyp')

        # we will also prepare the next evaluation (a. merge 2 ipus)
        to_merge_anns = dict()

        for result_ann, ref_ann in zip(tier_ref_result, ref_tier):
            if is_silence(ref_ann):
                continue
            rb, re, etiquette = get_ann_infos(ref_ann)

            hyp_anns = hyp_tier.find(rb, re, overlaps=True)
            if is_silence(hyp_anns[0]) is True:
                hyp_anns.pop(0)
            if len(hyp_anns) > 0 and is_silence(hyp_anns[-1]) is True:
                hyp_anns.pop(-1)
            ipus_hyp_anns = []
            for h in hyp_anns:
                if is_silence(h) is False:
                    # the middle of the hyp must be inside the ref
                    # or the contrary!
                    hb, he, hl = get_ann_infos(h)
                    hm = hb + (he-hb)/2.
                    rm = rb + (re-rb)/2.
                    if rb < hm < re or hb < rm < he:
                        ipus_hyp_anns.append(h)

            # the ipu of the ref does not match any ipu in the hyp.
            if len(ipus_hyp_anns) == 0:
                # this is the critical situation.
                nb_ref_not_match += 1
                logging.debug('        REF IPU: [ {:f} ; {:f} ; {:s} ] has no HYP.'
                              ''.format(rb, re, etiquette))
                result_ann.set_labels(sppasLabel(sppasTag('Missing')))

            # the ipu of the ref is matching only one ipu in the hyp
            elif len(ipus_hyp_anns) == 1:
                # this is a success.
                nb_ref_perfect_match += 1
                result_ann.set_labels(ipus_hyp_anns[0].get_labels())

            # the ipu of the ref is matching several ipus in the hyp.
            else:
                # This over-segmentation could correspond to a short-pause,
                # or a silence into a laugh. this is an error but not a critical one.
                nb_ref_several_match += len(ipus_hyp_anns) - 1
                logging.debug('        REF IPU: [ {:f} ; {:f} ; {:s} ] has several HYPs:'
                              ''.format(rb, re, etiquette))
                for i, h in enumerate(hyp_anns):
                    logging.debug('          HYP IPU: {:s}'.format(h.get_location().get_best()))
                    if i == 0:
                        to_merge_anns[h] = hyp_anns
                    else:
                        to_merge_anns[h] = None
                result_ann.set_labels(sppasLabel(sppasTag('Multi')))

        nb_ref_perfect_match_total += nb_ref_perfect_match
        nb_ref_not_match_total += nb_ref_not_match
        nb_ref_several_match_total += nb_ref_several_match

        # communicate this result:
        # ------------------------
        trs.append(tier_ref_result)
        logging.info('       ==> full success is {:.2f}%:'
                     ''.format((float(nb_ref_perfect_match) / float(nb_ipus_ref)) * 100.))
        logging.info('         - number of NOT matching ipus of ref in hyp: {:d}'
                     ''.format(nb_ref_not_match))
        logging.info('         - number of time several hyp are matching the ref: {:d}'
                     ''.format(nb_ref_several_match))
        logging.info('         + number of perfect match of ref in hyp: {:d}'
                     ''.format(nb_ref_perfect_match))

        # -------------------------------------------------------------------
        # Match ipus of hyp in ref

        logging.info('    - Match ipus of hyp in ref:')

        nb_hyp_merge_ipus = 0
        nb_hyp_not_match = 0
        nb_hyp_split_ipus = 0
        nb_hyp_move_one_bound = 0
        nb_hyp_move_two_bound = 0

        # Search for situation a.
        # -------------------------------

        if len(to_merge_anns) > 0:
            a_hyp_tier = sppasTier(hyp_tier.get_name())
            for hyp_ann in hyp_tier:
                if hyp_ann in to_merge_anns:
                    anns_to_merge = to_merge_anns[hyp_ann]
                    if anns_to_merge is not None:
                        # a. merge ipus (hyp5)
                        #    ref:     #    |         ipu        |    #
                        #    hyp:     #    | ipu    |  #  | ipu  |   #
                        nb_hyp_merge_ipus += len(anns_to_merge) - 1
                        labels = []
                        for h in anns_to_merge:
                            labels.extend(h.get_labels())
                        labels.append(sppasLabel(sppasTag('Merge')))
                        a = a_hyp_tier.create_annotation(
                            sppasLocation(
                                sppasInterval(
                                    to_merge_anns[hyp_ann][0].get_location().get_best().get_begin(),
                                    to_merge_anns[hyp_ann][-1].get_location().get_best().get_end())),
                            labels
                            )
                else:
                    a_hyp_tier.add(hyp_ann)
        else:
            a_hyp_tier = hyp_tier

        # Search for situations b. c. and d.
        # ----------------------------------
        prec_he = 0.
        hyp_tier_result = a_hyp_tier.copy()
        hyp_tier_result.set_name('Hyp-in-ref')

        for result_ann, hyp_ann in zip(hyp_tier_result, a_hyp_tier):
            if is_silence(hyp_ann):
                continue
            hb, he, etiquette = get_ann_infos(hyp_ann)

            # d. move bounds
            move_bounds = 0
            if prec_he >= hb:
                # we previously moved the end. now it is higher than our begin!
                hb = prec_he
                move_bounds = 1
                result_ann.append_label(sppasLabel(sppasTag('MoveBegin')))
                logging.debug('          BEGIN MOVED. HYP IPU: [ {:f} ; {:f} ; {:s} ].'
                              ''.format(hb, he, etiquette))

            ref_anns = ref_tier.find(hb, he, overlaps=True)
            ipus_ref_anns = []
            for h in ref_anns:
                if is_silence(h) is False:
                    ipus_ref_anns.append(h)
        
            if len(ipus_ref_anns) == 0:
                # c. delete an ipu (false positive)
                #    ref:               #
                #    hyp:    #      | ipu  |    #
                nb_hyp_not_match += 1
                result_ann.set_labels(sppasLabel(sppasTag('Delete')))
                logging.debug('          HYP IPU: [ {:f} ; {:f} ; {:s} ] has no REF.'
                              ''.format(hb, he, etiquette))

            else:  # if len(ipus_ref_anns)== 1:

                # d. move bounds
                rb, x, rl = get_ann_infos(ipus_ref_anns[0])
                x, re, rl = get_ann_infos(ipus_ref_anns[-1])

                if rb < (hb-0.045) or rb > (hb+0.090):
                    hb = rb
                    if move_bounds == 0:
                        move_bounds += 1
                        result_ann.append_label(sppasLabel(sppasTag('MoveBegin')))
                        logging.debug('          BEGIN MOVED. HYP IPU: [ {:f} ; {:f} ; {:s} ].'
                                      ''.format(hb, he, etiquette))

                    else:
                        logging.debug('             RE-BEGIN MOVED. HYP IPU: [ {:f} ; {:f} ; {:s} ].'
                                      ''.format(hb, he, etiquette))

                if re > (he+0.04) or re < (he-0.08):
                    move_bounds += 1
                    he = re
                    result_ann.append_label(sppasLabel(sppasTag('MoveEnd')))
                    logging.debug('          END MOVED. HYP IPU: [ {:f} ; {:f} ; {:s} ].'
                                  ''.format(hb, he, etiquette))

            # re-search for refs (in case hb/he modified)
            ref_anns = ref_tier.find(hb, he, overlaps=True)
            ipus_ref_anns = [h for h in ref_anns if is_silence(h) is False]
            if len(ipus_ref_anns) > 1:
                # b. split an ipu (hyp6)
                #    ref:    #   |  ipu    |  #  |  ipu  |   #
                #    hyp:    #   |           ipu         |   #
                _nb_splits = len(ipus_ref_anns) - 1
                nb_hyp_split_ipus += _nb_splits
                logging.debug('          HYP IPU: [ {:f} ; {:f} ; {:s} ] has several REFs:'
                              ''.format(hb, he, etiquette))
                result_ann.append_label(sppasLabel(sppasTag('Split{:d}'.format(_nb_splits))))
                for i, h in enumerate(ipus_ref_anns):
                    logging.debug('            REF IPU: {:s}'.format(h.get_location().get_best()))

            if move_bounds == 1:
                nb_hyp_move_one_bound += 1
            elif move_bounds == 2:
                nb_hyp_move_two_bound += 1

            # prepare for the analysis of the next hyp ann
            prec_he = he

        trs.append(hyp_tier_result)
        nb_hyp_split_ipus_total += nb_hyp_split_ipus
        nb_hyp_not_match_total += nb_hyp_not_match
        nb_hyp_move_bounds_total += (nb_hyp_move_one_bound+nb_hyp_move_two_bound)

        # communicate the results
        logging.info("        a. merge of ipus: {:d}. "
                     "({:.2f}% of the ipus of hyp are merged with another one)"
                     "".format(nb_hyp_merge_ipus,
                               (float(nb_hyp_merge_ipus) / float(nb_ipus_hyp)) * 100.))
        logging.info("        b. split ipus: {:d}. ({:.2f}% of the ipus of hyp)"
                     "".format(nb_hyp_split_ipus, (float(nb_hyp_split_ipus) / float(nb_ipus_hyp)) * 100.))
        logging.info("        c. delete an ipu: {:d}. ({:.2f}% of the ipus of hyp are false positives)"
                     "".format(nb_hyp_not_match, (float(nb_hyp_not_match) / float(nb_ipus_hyp)) * 100.))
        m = nb_hyp_move_one_bound+nb_hyp_move_two_bound
        logging.info("        d. move bounds of an ipu: {:d}. ({:.2f}% of the ipus of hyp)"
                     "".format(m, (float(m) / float(nb_ipus_hyp)) * 100.))

        p = sppasRW(os.path.join(out_name)+"-"+os.path.basename(fh))
        p.write(trs)

    # -----------------------------------------------------------------------
    # Write/save global results
    # -----------------------------------------------------------------------

    # Prepare summary messages
    # ------------------------
    r1 = '   - number of NOT matching ipus of ref in hyp: {:d}'.format(nb_ref_not_match_total)
    r2 = '   - number of time several hyp are matching the ref: {:d}'.format(nb_ref_several_match_total)
    r3 = '   - number of perfect match of ref in hyp: {:d}'.format(nb_ref_perfect_match_total)
    r = ' ==> full success is {:.2f}%. Details are:'.format(
        (float(nb_ref_perfect_match_total) / float(nb_ipus_ref_total)) * 100.)
    h1 = " a. merge of ipus: {:d}. ({:.2f}% of the ipus of hyp are merged with another one)" \
         "".format(nb_hyp_merge_ipus_total,
                   (float(nb_hyp_merge_ipus_total) / float(nb_ipus_hyp_total)) * 100.)
    h2 = " b. split ipus: {:d}. ({:.2f}% of the ipus of hyp)" \
         "".format(nb_hyp_split_ipus_total,
                   (float(nb_hyp_split_ipus_total) / float(nb_ipus_hyp_total)) * 100.)
    h3 = " c. delete an ipu: {:d}. ({:.2f}% of the ipus of hyp are false positives)" \
         "".format(nb_hyp_not_match_total,
                   (float(nb_hyp_not_match_total) / float(nb_ipus_hyp_total)) * 100.)
    h4 = " d. move bounds of an ipu: {:d}. ({:.2f}% of the ipus of hyp)" \
         "".format(nb_hyp_move_bounds_total,
                   (float(nb_hyp_move_bounds_total) / float(nb_ipus_hyp_total)) * 100.)

    # Print on stdout
    # ---------------
    logging.info('Number of ipus in ref: {:d}'.format(nb_ipus_ref_total))
    logging.info('Number of ipus in hyp: {:d}'.format(nb_ipus_hyp_total))
    logging.info('1. Match ipus of ref in hyp: ')
    for msg in (r, r1, r2, r3):
        logging.info(msg)
    logging.info('2. Match ipus of hyp in ref: ')
    for msg in (h1, h2, h3, h4):
        logging.info(msg)

    # Print in a file
    # ---------------

    with codecs.open(os.path.join(out_name)+"-summary.txt", "w", 'utf8') as fp:
        fp.write('---------------------------------------------------\n')
        fp.write('SPPAS version {:s}\n'.format(sg.__version__))
        fp.write('---------------------------------------------------\n')
        fp.write('Files: \n')
        for f in files_ok:
            fp.write(' - {:s}: {:s}\n'.format(f[0], f[1]))
        fp.write('\n')
        fp.write('Number of ipus in ref: {:d}'.format(nb_ipus_ref_total))
        fp.write('Number of ipus in hyp: {:d}'.format(nb_ipus_hyp_total))
        fp.write('\n')
        fp.write('Results: \n')
        fp.write('1. Match ipus of ref in hyp: \n')
        for msg in (r1, r2, r3):
            fp.write(msg)
            fp.write('\n')
        fp.write('2. Match ipus of hyp in ref: \n')
        for msg in (h1, h2, h3, h4):
            fp.write(msg)
            fp.write('\n')

        fp.close()
