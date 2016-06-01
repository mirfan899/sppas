#!/bin/bash

# ---------------------------------------------------------------------------
# File:    test_bin.sh
# Author:  Brigitte Bigi
# Date:    December, 2014
# Brief:   Tests of the binaries included in SPPAS.
# ---------------------------------------------------------------------------

# ===========================================================================
# Fix global variables
# ===========================================================================

# Program to package
PROGRAM_DIR=".."
PROGRAM_NAME=$(grep -i program: $PROGRAM_DIR/README.txt | awk '{print $2}')
PROGRAM_AUTHOR=$(grep -i author: $PROGRAM_DIR/README.txt | awk -F":" '{print $2}')
PROGRAM_VERSION=$(grep -i version: $PROGRAM_DIR/README.txt | awk '{print $2}')
PROGRAM_COPYRIGHT=$(grep -i copyright: $PROGRAM_DIR/README.txt | awk -F":" '{print $2}')

# Files and directories to be used
BIN_DIR="$PROGRAM_DIR/sppas/bin"
SAMPLES_DIR="samples"
RESOURCES_DIR="$PROGRAM_DIR/resources"

# Test functions
TODO="wavsplit tokenize phonetize alignment syllabify annotation momelintsint repetition "

# User-Interface
MSG_HEADER="${PROGRAM_NAME} test_bin.sh, a program written by ${PROGRAM_AUTHOR}."
TODAY=$(date "+%Y-%m-%d")

BLACK='\e[0;30m'
WHITE='\e[1;37m'
LIGHT_GRAY='\e[0;37m'
DARK_GRAY='\e[1;30m'
BLUE='\e[0;34m'
DARK_BLUE='\e[1;34m'
GREEN='\e[0;32m'
LIGHT_GREEN='\e[1;32m'
CYAN='\e[0;36m'
LIGHT_CYAN='\e[1;36m'
RED='\e[0;31m'
LIGHT_RED='\e[1;31m'
PURPLE='\e[0;35m'
LIGHT_PURPLE='\e[1;35m'
BROWN='\e[0;33m'
YELLOW='\e[1;33m'
NC='\e[0m' # No Color

# ===========================================================================
# Functions generic
# ===========================================================================


# Print a title message on stdout
# Parameters:
#  $1: message to print
function fct_echo_title {
    echo -e "${LIGHT_GREEN}-----------------------------------------------------------------------"
    echo -e "${BROWN}$1"
    echo -e "${LIGHT_GREEN}-----------------------------------------------------------------------${NC}"
}


# Print a sub-title message on stdout
# Parameters:
#  $1: message to print
function fct_echo_subtitle {
    echo -e "${BROWN}$1"
    echo -e "${LIGHT_GREEN}-----------------------------------------------------------------------${NC}"
}


# Print the header message on stdout
function fct_echo_header {
    echo
    echo -e "${LIGHT_GREEN}-----------------------------------------------------------------------"
    echo -e "${LIGHT_RED}$MSG_HEADER"
    echo -e "${LIGHT_GREEN}-----------------------------------------------------------------------${NC}"
    echo
}


# Print an error message, then exit
# Parameters:
#   $1: error message
function fct_exit_error {
    fct_echo_header
    echo -e "${RED}Error: $1${NC}"
    echo
    exit 1
}

# ===========================================================================
# Functions to extract the command-line
# ===========================================================================


# Print the Usage message on stdout
function fct_echo_usage {
    fct_echo_header
    echo -e "${CYAN}Usage: $0 [functions]${NC}"
    echo -e "where:${LIGHT_CYAN}"
    echo -e "    [functions] name of functions to test, in:"
    for fct in $TODO; do
        echo -e "        * $fct";
    done
    echo -e "    -a: test all functions"
    echo -e "    -h: show this help and exit${NC}"
    echo
}

# Test if this scripts has the expected number of arguments
# Parameters:
#   $1: nb args
function fct_test_nb_args {
    local maxargs=10
    local minargs=1
    # The command is given without args: print usage
    if [ "$1" -eq 0 ]
    then
        echo -e "${DARK_BLUE}Help.${NC}"
        fct_echo_usage
        exit 0
    fi
    # Too many args: print error and usage
    if [ "$1" -gt $maxargs ]
    then
        echo -e "${DARK_BLUE}Too many arguments.${NC}"
        fct_echo_usage
        exit 1
    fi
    # Too few args: print error and usage
    if [ "$1" -lt $minargs ]
    then
        echo -e "${DARK_BLUE}Too few arguments.${NC}"
        fct_echo_usage
        exit 1
    fi

}

# Test if this scripts has the expected arguments
# Parameters:
#   $1: args
# return the list of functions
function fct_test_args {

    if [ "$1" == "-h" ];
    then
        fct_echo_usage
        exit 0
    fi
    if [ "$1" == "-a" ];
    then
        echo "$TODO"
        return
    fi

    # test if each args corresponds to a function name.
    # to do!

    echo "$@"
}

# ===========================================================================
# UTILS FUNCTIONS
# ===========================================================================

# Echo the status in a human-readable way!
# Parameters:
#   $1: status value
function fct_echo_status {
    if [ "$1" != "0" ]; then
        echo "error"
    else
        echo "ok"
    fi
}

# Echo the status in a human-readable way in reversed mode!
# Parameters:
#   $1: status value
function fct_echo_rstatus {
    if [ "$1" != "0" ]; then
        echo "ok"
    else
        echo "error"
    fi
}

# ===========================================================================
# TEST FUNCTIONS
# ===========================================================================

function wavsplit {

    fct_echo_subtitle "Test wavsplit.py (IPUs segmentation)"

    echo -n " ... command exists: "
    $BIN_DIR/wavsplit.py >> /dev/null &> /dev/null
    if [ $? != "0" ]; then
        echo "error"
        return
    fi
    echo "ok"

    echo -n " ... give only wav as input: "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV &> /dev/null
    fct_echo_status $?

    echo -n " ... give something wrong as input: "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.txt &> /dev/null
    fct_echo_rstatus $?

    echo -n " ... simple speech/silence segmentation with textgrid output: "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV -p oriana1.TextGrid &> /dev/null
    if [ -e oriana1.TextGrid ]; then
        rm oriana1.TextGrid;
        fct_echo_status 0
    else
        fct_echo_status 1
    fi

    echo -n " ... speech/silence segmentation, force 3 tracks: "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV -o oriana1 -N 3 &> /dev/null
    if [ -d oriana1 ]; then
        s=1
        if [ "`ls oriana1/*.wav | wc -l`" == "3" ]; then s=0; fi
        rm -rf oriana1;
        fct_echo_status $s
    else
        fct_echo_status 1
    fi

    echo -n " ... speech/silence segmentation, force 20 tracks: "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV -o oriana1 -N 20 &> /dev/null
    fct_echo_rstatus $?
    
    echo -n " ... simple speech/silence segmentation, -m and -s options (3 ipus): "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV -p oriana1.TextGrid -m 0.5 -s 0.4 &> /dev/null
    if [ -e oriana1.TextGrid ]; then
        s=1
        if [ "`grep ipu_3 oriana1.TextGrid | wc -l`" == "1" ]; then s=0; fi
        if [ "`grep ipu_4 oriana1.TextGrid | wc -l`" == "0" ]; then s=0; fi
        rm oriana1.TextGrid;
        fct_echo_status $s
    else
        fct_echo_status 1
    fi

    echo -n " ... simple speech/silence segmentation, -m and -s options (5 ipus): "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV -p oriana1.TextGrid -m 0.5 -s 0.2 &> /dev/null
    if [ -e oriana1.TextGrid ]; then
        s=1
        if [ "`grep ipu_5 oriana1.TextGrid | wc -l`" == "1" ]; then s=0; fi
        if [ "`grep ipu_6 oriana1.TextGrid | wc -l`" == "0" ]; then s=0; fi
        rm oriana1.TextGrid;
        fct_echo_status $s
    else
        fct_echo_status 1
    fi

    echo -n " ... speech/silence segmentation, align with transcription txt, output TextGrid: "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV -t $SAMPLES_DIR/oriana1.txt -p oriana1.TextGrid &> /dev/null
    if [ -e oriana1.TextGrid ]; then
        if [ "`grep ipu_3 oriana1.TextGrid | wc -l`" == "1" ]; then s=0; fi  # 3 IPUs exactly
        if [ "`grep ipu_4 oriana1.TextGrid | wc -l`" == "0" ]; then s=0; fi
        if [ "`grep the oriana1.TextGrid | wc -l`" == "3" ]; then s=0; fi    # with transcription filled
        rm oriana1.TextGrid;
        fct_echo_status $s
    else
        fct_echo_status 1
    fi

    echo -n " ... speech/silence segmentation, align with transcription txt, output xra: "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV -t $SAMPLES_DIR/oriana1.txt -p oriana1.xra &> /dev/null
    if [ -e oriana1.xra ]; then
        rm oriana1.xra;
        fct_echo_status 0
    else
        fct_echo_status 1
    fi

    echo -n " ... speech/silence segmentation, align with transcription txt, with dir output only: "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV -t $SAMPLES_DIR/oriana1.txt -o oriana1 &> /dev/null
    if [ -d oriana1 ]; then
        s=1
        if [ "`ls oriana1/track_000*.wav | wc -l`" == "3" ]; then s=0; fi
        if [ "`ls oriana1/index.txt | wc -l`" == "1" ]; then s=0; fi
        rm -rf oriana1;
        fct_echo_status $s
    else
        fct_echo_status 1
    fi

    echo -n " ... speech/silence segmentation, align with transcription txt, with dir output, with txt: "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV -t $SAMPLES_DIR/oriana1.txt -o oriana1 -e txt &> /dev/null
    if [ -d oriana1 ]; then
        s=1
        if [ "`ls oriana1/track_000*.wav | wc -l`" == "3" ]; then s=0; fi
        if [ "`ls oriana1/track_000*.txt | wc -l`" == "3" ]; then s=0; fi
        if [ "`ls oriana1/index.txt | wc -l`" == "1" ]; then s=0; fi
        rm -rf oriana1;
        fct_echo_status $s
    else
        fct_echo_status 1
    fi

    echo -n " ... speech/silence segmentation, align with transcription TextGrid, with tier Name and with dir output: "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV -t $SAMPLES_DIR/oriana1.TextGrid -o oriana1 &> /dev/null
    if [ -d oriana1 ]; then
        s=1
        if [ "`ls oriana1 | wc -l`" == "4" ]; then s=0; fi
        if [ "`ls oriana1/ipu_*.wav | wc -l`" == "3" ]; then s=0; fi
        if [ "`ls oriana1/index.txt | wc -l`" == "1" ]; then s=0; fi
        rm -rf oriana1;
        fct_echo_status $s
    else
        fct_echo_status 1
    fi

    echo -n " ... speech/silence segmentation, align with transcription TextGrid, with dir output and textgrid tracks: "
    $BIN_DIR/wavsplit.py -w $SAMPLES_DIR/oriana1.WAV -t $SAMPLES_DIR/oriana1.TextGrid -o oriana1 -e csv &> /dev/null
    if [ -d oriana1 ]; then
        s=1
        if [ "`ls oriana1 | wc -l`" == "7" ]; then s=0; fi
        if [ "`ls oriana1/ipu_*.csv | wc -l`" == "3" ]; then s=0; fi
        if [ "`ls oriana1/ipu_*.wav | wc -l`" == "3" ]; then s=0; fi
        if [ "`ls oriana1/index.txt | wc -l`" == "1" ]; then s=0; fi
        rm -rf oriana1;
        fct_echo_status $s
    else
        fct_echo_status 1
    fi

    echo
}

# ---------------------------------------------------------------------------

function tokenize {

    fct_echo_subtitle "Test tokenize.py (Tokenization)"

    echo -n " ... command exists: "
    $BIN_DIR/tokenize.py >> /dev/null &> /dev/null
    if [ $? != "0" ]; then
        echo "error"
        return
    fi
    echo "ok"

    echo -n " ... inline tokenization (1): "
    inline=`echo "This is my test number 1." | $BIN_DIR/tokenize.py -r $RESOURCES_DIR/vocab/eng.vocab`
    if [ "$inline" == "this is my test number one" ]; then
        fct_echo_status 0
    else
        fct_echo_status 1
    fi

    echo -n " ... inline tokenization (2): "
    inline=`echo "《干脆就把那部蒙人的闲法给废了拉倒！》RT @laoshipukong : 27日，全国人大常委会第三次审议侵权责任法草案，删除了有关医疗损害责任“举证倒置”的规定。" | $BIN_DIR/tokenize.py -r $RESOURCES_DIR/vocab/cmn.vocab`
    if [ "$inline" == "干脆 就 把 那 部 蒙 人 的 闲 法 给 废 了 拉倒 rt @ laoshipukong 二十七 日 全国人大常委会 第 三次 审议 侵权 责任 法 草案 删除 了 有关 医疗 损害 责任 举证 倒置 的 规定" ]; then
        fct_echo_status 0
    else
        fct_echo_status 1
    fi

    echo -n " ... tokenization of a file: "
    inline=`$BIN_DIR/tokenize.py -r $RESOURCES_DIR/vocab/eng.vocab -i $SAMPLES_DIR/oriana1.TextGrid -o oriana1-token.TextGrid`
    if [ -e oriana1-token.TextGrid ]; then
        rm oriana1-token.TextGrid
        fct_echo_status 0
    else
        fct_echo_status 1
    fi

    echo
}

# ---------------------------------------------------------------------------

function phonetize {

    fct_echo_subtitle "Test phonetize.py (Phonetization)"

    if [ "`uname | cut -f1 -d'_'`" == "CYGWIN" ]; then
        echo "cancelled (not available under cygwin)"
        return;
    fi

    echo -n " ... command exists: "
    $BIN_DIR/phonetize.py >> /dev/null &> /dev/null
    if [ $? != "0" ]; then
        echo "error"
        return
    fi
    echo "ok"

    echo -n " ... inline phonetization (1): "
    inline=`echo "test num one" | $BIN_DIR/phonetize.py -r $RESOURCES_DIR/dict/eng.dict --nounk`;
    if [ "$inline" == "t-E-s-t UNK w-V-n|h-w-V-n" ]; then
          fct_echo_status 0
    else
        fct_echo_status 1
    fi

    echo -n " ... inline phonetization (2): "
    inline=`echo "test num one" | $BIN_DIR/phonetize.py -r $RESOURCES_DIR/dict/eng.dict`;
    if [ "$inline" == "t-E-s-t n-V-m|n-u-m|n-u-@-m|E-n-V-m w-V-n|h-w-V-n" ]; then
          fct_echo_status 0
    else
        fct_echo_status 1
    fi

    echo -n " ... phonetization of a file: "
    $BIN_DIR/tokenize.py -r $RESOURCES_DIR/vocab/eng.vocab -i $SAMPLES_DIR/oriana1.TextGrid -o $SAMPLES_DIR/oriana1-token.TextGrid;
    inline=`$BIN_DIR/phonetize.py -r $RESOURCES_DIR/dict/eng.dict -i $SAMPLES_DIR/oriana1-token.TextGrid -o oriana1-phon.TextGrid`;
    if [ -e oriana1-phon.TextGrid ]; then
        rm oriana1-phon.TextGrid
        fct_echo_status 0
    else
        fct_echo_status 1
    fi

    echo
}

# ---------------------------------------------------------------------------

function alignment {

    fct_echo_subtitle "Test alignment.py (Alignment)"

    echo -n " ... command exists: "
    $BIN_DIR/alignment.py >> /dev/null &> /dev/null
    if [ $? != "0" ]; then
        echo "error"
        return
    fi
    echo "ok"

    $BIN_DIR/tokenize.py -r $RESOURCES_DIR/vocab/eng.vocab -i $SAMPLES_DIR/oriana1.TextGrid -o $SAMPLES_DIR/oriana1-token.TextGrid;
    $BIN_DIR/phonetize.py -r $RESOURCES_DIR/dict/eng.dict -i $SAMPLES_DIR/oriana1-token.TextGrid -o $SAMPLES_DIR/oriana1-phon.TextGrid;

    echo -n " ... simply align phonemes with julius: "
    $BIN_DIR/alignment.py -w $SAMPLES_DIR/oriana1.WAV -r $RESOURCES_DIR/models/models-eng -i $SAMPLES_DIR/oriana1-phon.TextGrid -o oriana1-palign.TextGrid >> /dev/null &> /dev/null
    if [ -e oriana1-palign.TextGrid ]; then
        size=`cat oriana1-palign.TextGrid | head -n 7 | tail -n 1`
        rm oriana1-palign.TextGrid
        if [ "$size" == "size = 1" ]; then
            fct_echo_status 0
        else
            fct_echo_status 1
        fi
    else
        fct_echo_status 1
    fi

    echo -n " ... align phonemes and tokens with julius: "
    $BIN_DIR/alignment.py -w $SAMPLES_DIR/oriana1.WAV -r $RESOURCES_DIR/models/models-eng -i $SAMPLES_DIR/oriana1-phon.TextGrid -I $SAMPLES_DIR/oriana1-token.TextGrid -o oriana1-palign.TextGrid >> /dev/null &> /dev/null
    if [ -e oriana1-palign.TextGrid ]; then
        size=`cat oriana1-palign.TextGrid | grep -c "^size = 3"`
        rm oriana1-palign.TextGrid
        if [ "$size" == "1" ]; then
            fct_echo_status 0
        else
            fct_echo_status 1
        fi
    else
        fct_echo_status 1
    fi

    echo -n " ... align phonemes and tokens with basic aligner: "
    $BIN_DIR/alignment.py -w $SAMPLES_DIR/oriana1.WAV -r $RESOURCES_DIR/models/models-eng -i $SAMPLES_DIR/oriana1-phon.TextGrid -I $SAMPLES_DIR/oriana1-token.TextGrid -o oriana1-palign.TextGrid -a basic >> /dev/null &> /dev/null
    if [ -e oriana1-palign.TextGrid ]; then
        size=`cat oriana1-palign.TextGrid | grep -c "^size = 3"`
        rm oriana1-palign.TextGrid
        if [ "$size" == "1" ]; then
            fct_echo_status 0
        else
            fct_echo_status 1
        fi
    else
        fct_echo_status 1
    fi

    echo
}

# ---------------------------------------------------------------------------

function syllabify {

    fct_echo_subtitle "Test syllabify.py (Syllabification)"

    echo -n " ... command exists: "
    $BIN_DIR/syllabify.py >> /dev/null &> /dev/null
    if [ $? != "0" ]; then
        echo "error"
        return
    fi
    echo "ok"

    echo -n " ... simple syllabification of a file: "
    inline=`$BIN_DIR/syllabify.py -r $RESOURCES_DIR/syll/syllConfig-ita.txt -i $SAMPLES_DIR/DGtdA05Np1_95-palign.TextGrid -o DGtdA05Np1_95-salign.TextGrid`
    if [ -e DGtdA05Np1_95-salign.TextGrid ]; then
        size=`cat DGtdA05Np1_95-salign.TextGrid | grep -c "size = 3"`
        rm DGtdA05Np1_95-salign.TextGrid
        if [ "$size" == "1" ]; then
            fct_echo_status 0
        else
            fct_echo_status 1
        fi
    else
        fct_echo_status 1
    fi

    echo -n " ... syllabification inside tokens: "
    inline=`$BIN_DIR/syllabify.py -r $RESOURCES_DIR/syll/syllConfig-ita.txt -i $SAMPLES_DIR/DGtdA05Np1_95-palign.TextGrid -t TokensAlign -o DGtdA05Np1_95-salign.TextGrid`
    if [ -e DGtdA05Np1_95-salign.TextGrid ]; then
        size=`cat DGtdA05Np1_95-salign.TextGrid | grep -c "size = 6"`
        rm DGtdA05Np1_95-salign.TextGrid
        if [ "$size" == "1" ]; then
            fct_echo_status 0
        else
            fct_echo_status 1
        fi
    else
        fct_echo_status 1
    fi

    echo -n " ... syllabification inside tokens with --nophn option: "
    inline=`$BIN_DIR/syllabify.py -r $RESOURCES_DIR/syll/syllConfig-ita.txt -i $SAMPLES_DIR/DGtdA05Np1_95-palign.TextGrid  -t TokensAlign --nophn -o DGtdA05Np1_95-salign.TextGrid`
    if [ -e DGtdA05Np1_95-salign.TextGrid ]; then
        size=`cat DGtdA05Np1_95-salign.TextGrid | grep -c "size = 3"`
        rm DGtdA05Np1_95-salign.TextGrid
        if [ "$size" == "1" ]; then
            fct_echo_status 0
        else
            fct_echo_status 1
        fi
    else
        fct_echo_status 1
    fi

    echo
}

# ---------------------------------------------------------------------------

function annotation {

    fct_echo_subtitle "Test annotation.py (All automatic annotations in 1 command line...)"

    if [ "`uname | cut -f1 -d'_'`" == "CYGWIN" ]; then
        echo "cancelled (not available under cygwin)"
        return;
    fi

    echo -n " ... command exists: "
    $BIN_DIR/annotation.py >> /dev/null &> /dev/null
    if [ $? != "0" ]; then
        echo "error"
        return
    fi
    echo "ok"

    echo -n " ... test ipu, tok, phon, align: "
    $BIN_DIR/annotation.py -w $SAMPLES_DIR/oriana1.WAV -l eng --ipu --tok --phon --align -e TextGrid >> /dev/null &> /dev/null
    if [ -e $SAMPLES_DIR/oriana1-merge.TextGrid ]; then
        rm $SAMPLES_DIR/oriana1-palign.TextGrid
        fct_echo_status 0
    else
        fct_echo_status 1
    fi

    echo -n " ... test all: "
    $BIN_DIR/annotation.py -w $SAMPLES_DIR/oriana1.WAV -l eng --all -e "xra" >> /dev/null &> /dev/null
    if [ -e $SAMPLES_DIR/oriana1-palign.xra ]; then
        rm $SAMPLES_DIR/oriana1*.xra
        fct_echo_status 0
    else
        fct_echo_status 1
    fi

    echo
}

# ---------------------------------------------------------------------------

function momelintsint {

    fct_echo_subtitle "Test momel-intsint.py (Momel and INTSINT)"

    if [ "`uname | cut -f1 -d'_'`" == "CYGWIN" ]; then
        echo "cancelled (not available under cygwin)"
        return;
    fi

    echo -n " ... command exists: "
    $BIN_DIR/momel-intsint.py >> /dev/null &> /dev/null
    if [ $? != "0" ]; then
        echo "error"
        return
    fi
    echo "ok"

    echo -n " ... only Momel, inline output: "
    inline=`$BIN_DIR/momel-intsint.py -i $SAMPLES_DIR/F_F_B003-P9.hz | wc -l`
    if [ "$inline" == "71" ]; then
          fct_echo_status 0
    else
        fct_echo_status 1
    fi

    echo -n " ... Momel and INTSINT, output file: "
    inline=`$BIN_DIR/momel-intsint.py -i $SAMPLES_DIR/F_F_B003-P9.hz -o F_F_B003-P9-momel.TextGrid | wc -l`
    if [ -e F_F_B003-P9-momel.TextGrid ]; then
        size=`cat F_F_B003-P9-momel.TextGrid | grep -c "^size = 2"`
        rm F_F_B003-P9-momel.TextGrid
        if [ "$size" == "1" ]; then
            fct_echo_status 0
        else
            fct_echo_status 1
        fi
    else
        fct_echo_status 1
    fi

    echo
}

# ---------------------------------------------------------------------------

function repetition {

    fct_echo_subtitle "Test repetition.py (Self- and Other- repetitions)"

    if [ "`uname | cut -f1 -d'_'`" == "CYGWIN" ]; then
        echo "cancelled (not available under cygwin)"
        return;
    fi

    echo -n " ... command exists: "
    $BIN_DIR/repetition.py >> /dev/null &> /dev/null
    if [ $? != "0" ]; then
        echo "error"
        return
    fi
    echo "ok"

    echo -n " ... self-repetition, language-independent: "
    $BIN_DIR/repetition.py -i $SAMPLES_DIR/DGtdA05Np1_95-palign.TextGrid -o DGtdA05Np1_95-ralign.TextGrid >> /dev/null &> /dev/null
    if [ -e DGtdA05Np1_95-ralign.TextGrid ]; then
        size=`cat DGtdA05Np1_95-ralign.TextGrid | grep -c "^size = 2"`
        rm DGtdA05Np1_95-ralign.TextGrid
        if [ "$size" == "1" ]; then
            fct_echo_status 0
        else
            fct_echo_status 1
        fi
    else
        fct_echo_status 1
    fi

    echo
}

# ---------------------------------------------------------------------------

# ===========================================================================
# MAIN
# ===========================================================================

fct_test_nb_args "$#"           # Test if this scripts has the expected number of arguments
todolist=$(fct_test_args "$@")  # Get functions from args
fct_echo_header                 # Print the header message on stdout
for arg in $todolist; do
    $arg                        # run the test (arg is a function to execute)
done
fct_echo_title "Terminated."    # Print the header message on stdout

# ===========================================================================
