### Example commands to run pwordcount:
1) ./pwordcount -m t -p 2 file.txt file2.txt
2) ./pwordcount -m u file.txt
3) ./pwordcount -m o -p 4 file.txt file2.txt file3.txt file4.txt

### Implementation limitations:
- Large files. If the file is large, it has to be separated between several processes.
- No synchronisation.

### Approach to splitting files:
- If more than one file is passed, each file is assigned to a separate process, avoiding splitting content within files.
- If only one file is passed, the content is split between the available processes, taking into account the size of the file or the number of lines where possible.

### Other relevant information:
- We use the multiprocessing module to create processes.
- More than one process = faster work.

1)./pwordcount -m t -p 2 file.txt file2.txt
2)./pwordcount -m t -p 4 file.txt file2.txt file3.txt
3)./pwordcount -m u -p 4 file.txt file2.txt file3.txt file4.txt
4)./pwordcount -m o -p 4 file.txt file2.txt
5)./pwordcount -m u -p 1 file.txt file2.txt file3.txt file4.txt
6)./pwordcount -m u -p 1 -l count.log file.txt
7)./pwordcount -m u -p 2 -l count.log file.txt file2.txt

Translated with DeepL.com (free version)
