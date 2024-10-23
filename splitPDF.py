#!/usr/bin/env -S nix develop . --command python


import sys
import os
import subprocess

def Usage():
  print("""
Usage: splitPDF.py inputFN splitPageNum1 splitPageNum2 ...

  - inputFN: the path to the input pdf file.

  - splitPageNum1, ...: each one is a positive integer; the numbers
    must not exceed the number of pages of the input file, and the
    entire sequence must be strictly increasing.

Example: splitPDF.py input.pdf 3 5

This will split file input.pdf into 3 files (assuming input.pdf is 10
pages long):

  - input.part1.1_3.pdf contains page 1-3;

  - input.part2.4_5.pdf contains page 4-5;

  - input.part3.6_10.pdf contains page 6-10.

  """)


if len(sys.argv) < 3:
  Usage()
  sys.exit(1)
else:
  inputFN = sys.argv[1]

  if os.path.exists(inputFN):
    try:
      cmd = f"pdftk {inputFN} dump_data | grep NumberOfPages | awk '{{ print $2 }}' | tail -n 1"
      ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      result = ps.communicate()[0]
      print(f"result was {result}")
      maxPages = int(result)
    except Exception:
      cmd = f"pdfinfo {inputFN} | grep Pages | awk '{{ print $2 }}'"
      ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
      result = ps.communicate()[0]
      maxPages = int(result)
    print('%s has %d pages' % (inputFN, maxPages))
  else:
    sys.exit(2)

  try:
    splitPageNums = list(map(int, sys.argv[2:]))
    if splitPageNums[-1] < maxPages:
      splitPageNums.append(maxPages)
    splitPageNums = [ (i, splitPageNums[i]) for i in range(0,len(splitPageNums)) ]
  except:
    print('Error: invalid split page number(s).')

  for i, splitPageNum in splitPageNums:
    if splitPageNum < 1 or splitPageNum > maxPages:
      print('Error: a split page number must be >= 1 and <= %d.' % \
            maxPages)
      sys.exit(3)
    elif i and splitPageNums[i - 1][1] >= splitPageNum:
      print('Error: split page numbers must be increasing.')
      sys.exit(4)

baseFN = os.path.splitext(os.path.basename(inputFN))[0]

startPageNum = 1
for i, splitPageNum in splitPageNums:
  outputFN = '%s.part%d.%d_%d.pdf' % \
    (baseFN, i + 1, startPageNum, splitPageNum)
  print('Writing page %d-%d to %s...' % \
        (startPageNum, splitPageNum, outputFN))

  pages = list(range(startPageNum, splitPageNum + 1))
  subprocess.run(["pdftk", inputFN, "cat" ] + [ str(x) for x in pages ] + [ "output", outputFN ], stdout=subprocess.PIPE)

  startPageNum = splitPageNum + 1

print('Done: %d file(s) generated.' % len(splitPageNums))
