#!/usr/bin/python

import sys, os
sys.path.append(os.path.realpath('../modules'))
sys.path.append(os.path.realpath('./modules'))

import argparse

def parse_args(args):
    mode = args.pop(0)
    parser = argparse.ArgumentParser()

    if mode == 'rate':
        parser.add_argument('-i', '--input')
        parser.add_argument('-r', '--reference')
        parser.add_argument('-o', '--output')
        parser.add_argument('-rl', '--rate_list')
        parser.add_argument('-ptp', '--run_ptp')
        parser.add_argument('-z', '--randomisations')
        parser.add_argument('-p', '--p_value', default=0.05)
        parser.add_argument('-pl', '--pval_list')

    elif mode == 'index':
        parser.add_argument('-i', '--input')
        parser.add_argument('-s', '--split')
        parser.add_argument('-o', '--output')
        parser.add_argument('-u', '--unknowns', default='?')

    elif mode == 'output':
        parser.add_argument('-i', '--input')
        parser.add_argument('-fa', '--fasta')
        parser.add_argument('-o', '--output')
        parser.add_argument('-f', '--format', default='0')
        parser.add_argument('-inc', '--include_only')
        parser.add_argument('-exc', '--exclude_only')
        parser.add_argument('-m', '--mask', default=False)
        parser.add_argument('-b', '--bins', default=10)
        

    else:
        print "'%s' is not a valid mode.\n\n" % mode
        die_with_help()

    opts = parser.parse_args(args)
    return (mode, opts)

def die_with_help():
    print """
****************
TIGER  v2.0 Help:
****************

TIGER: Tree-Independent Generation of Evolutionary Rates

TIGER v2.0 is split into 3 modes, allowing for comparisons to be run concurrently.
First, the input file needs to be broken down and indexed (index mode). It can be broken into many
pieces, all of which can be compared on seperate processors. Next, the rate must be
calculated for all sites (usually across multiple index files). Finally, the data can 
be combined and output in a number of formats with masking options.

Modes:
    index:    prepare the data for rate calculation, generate tiger index (.ti) file(s).
    rate:     preform calculation of tiger rate for each site, generate generated rates (.gr) file(s).
    output:   write sequence files based on .gr files, integrate rates from a split analysis into a 
              single file, mask and edit alignment based on tiger rates.

1. tiger index Options:

    -i|input    Specify input file. File must be in FastA format and must be aligned prior.
                Datasets with uneven sequence lengths will return an error.

    -s|split    Split dataset across multiple files to run simultaneously. Takes int argument.

    -o|output   Specify the prefix name of output files.

    -u|unknowns Specify unknown characters in the alignment. Unknown characters are omitted from 
                site patterns and so are not considered in the analysis.
                -u ?,-,*: defines ?, - and * as unknown characters. (*Be sure to put only a comma
                between characters, NO SPACE!!)
         
                Default is ? only

    Examples:
        1. Generate a .ti file for complete sequence named full_seq.ti & set unknowns to ? and - :
                tiger index -i my_file.aln -o full_seq -u ?,-

        2. Generate 10 subsets of the data with an output prefix of tiger_split and a reference:
                tiger index -i my_file.aln -o tiger_split -s 10
            ** Results in files named tiger_split.0.ti, tiger_split.1.ti, and so on, along with
               tiger_split.ref.ti

2. tiger rate Options:

    -i|input            Specify input file. File should be in .ti format.

    -r|reference        Specify reference sequence (.ti). -i file is used as default if none is provided.

    -o|output           Specify prefix name for output files.
    
    -rl|rate_list       A list of the rate at each site may be optionally written to a specified
                        file. 
                        -rl <file.txt> : writes list of the rates at each site to file.txt.

                        Default is <input_file_prefix>.rates if no filename is specified

    -ptp                Specifies that a PTP test should be run. 
                        * Note * this option has a huge effect on running time!

    -z|randomisations   Number of randomisations to be used for the PTP test. 
                        -z <int>: each site will be randomised <int> times. <int> is a whole number.

	                    Default is 100

    -p|p_value          Specify p-value which denotes significance in PTP test.
                        -p <float>: site will be denoted as significant if p-value is better than <float>.
                        <float> is a floating point number.

                        Default is 0.05

    -pl|pval_list       Write a list of p-values to a specified file.
                        -pl <file.txt>: writes list of p-values for each site to file.txt.

                        Default is <input_file_prefix>.pval

    Examples:
        1. Calculate rates for file test.ref.ti against itself and create a file containing a list of rates:
            tiger rate -i test.ref.ti -rl
        2. Calculate rates for file test.0.ti against test.ref.ti with a PTP test and a list of p values
            tiger rate -i test.0.ti -r test.ref.ti -ptp -pl

3. tiger output Options:
    
    -i|input            Specify input file. Must be in .gr format.

    -c|combine          Specify input file. This file should contain a list of .gr files to be combined.

    -fa|fasta           Provide original .fa file for sequence data.

    -o|output           Specify prefix name for output files.

    -f|format           Changes formatting options.
                        NEXUS, with comments:
                        -f 0: output bin numbers, sites unsorted (default)
                        -f 1: output bin number, sites sorted on rank
                        -f 2: displays rank values rather than bin numbers
                        -f 3: displays rank values and sites sorted on rank
                        FastA:
                        -f 4

    -inc|include_only   Give list of charsets to include
                        -inc Bin3,Bin4,Bin5,Bin6 (Note: No spaces, just commas)

    -exc|exclude_only   Give list of charsets to exclude
                        -exc Bin1,Bin2,Bin9,Bin10

    -m|mask             Mask -inc/-exc sites rather than removing them (default)

    -b|bins             Set the number of bins to be used.
                        -b <int>: Sites will be placed into <int> number of bins. <int> is a whole number.

                        Default is 10.
    Examples:
        1.  Write a FastA file, masking site that fall into Bin1, Bin2, Bin9 and Bin10 of 10 bins:
            tiger output -i sample.gr -fa my_data.fa -exc Bin1,Bin2,Bin9,Bin10 -b 10 --mask

        2. Write a NEXUS file combining test.0.gr, test.1.gr, test.2.gr with sites sorted on rank
            tiger output -c list_of_gr_files.txt -fa my_data.fa -f 3
   
     """
    sys.exit(1)

def die_with_message(message):
	print message
	sys.exit(1)


## MAIN ##
if len(sys.argv) < 2:
	die_with_help()

args = sys.argv[1:]
(mode, opts) = parse_args(args)

if mode == 'index':
    from biotiger import index
    index.run(opts)
elif mode == 'rate':
    from biotiger import rate
    rate.run(opts)
elif mode == 'output':
    from biotiger import output
    output.run(opts)

# seq_data = biotiger.parse_fasta(opts.input_file)
# seq_len = check_aln(seq_data)
# patterns = biotiger.patterns(seq_data)

# start = 0
# end = seq_len

# # single CPU for now..
# rates = biotiger.rate(patterns)

# # To think about: how to split tiger jobs into pieces...
# #rates = biotiger.rate(patterns, start, end) ??

# # prepare info for printing
# formatted_pats = patterns[:]
# formatted_comm = rates[:]
# bins = biotiger.bin(opts.bins, formatted_comm)

# if opts.formatting in ['1', '3']: #i.e. needs sorting
# 	[formatted_comm, formatted_pats] = biotiger.sort(formatted_comm, formatted_pats)

# if opts.formatting in ['0', '1']:
# 	formatted_comm = bins


# histogram = biotiger.histogram(num_list, name_list)


# print_nexus(taxon_names, formatted_pats, formatted_comm)





