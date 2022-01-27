import os
from os.path import *
import glob


class Formatter:
    text = ''
    lines = []
    keySymbols = {"==", "!=", "<", ">", "+", "-", "*", "/", "+=", "-=", "/=", "*=", ">=", "<=",
                  "in", "not in", "is", "is not", "and", "or", "not"}
    calSymbol = {"+", "-", "*", "/"}
    path = ''
    formatters = []
    isText = False
    @staticmethod
    def countStartSpace(s):
        i = 0
        while i < len(s):
            if s[i] == ' ':
                i += 1
            else:
                break
        return i

    def emptyLine(self, s):
        length = len(s)
        return self.countStartSpace(s) == len(s)

    @staticmethod
    # count character without space
    def countChar(s):
        return len(s) - s.count(" ")

    # get last char of string
    @staticmethod
    def lastChar(s):
        s = s.strip()
        return s[len(s) - 1]

    # get the first char of string
    @staticmethod
    def firstChar(s):
        s = s.strip()
        if len(s) > 0:
            return s[0]
        return ""

    # check if it is comment
    @staticmethod
    def isComment(s):
        s = s.strip()
        return s[0] == '#'

    # Return the index of next not empty line start from i + 1
    def nextNotEmptyLine(self, i):
        while i + 1 != len(self.lines) and self.emptyLine(self.lines[i + 1]):
            i += 1
        return i + 1

    # Return the index of next not white space char start from i + 1
    @staticmethod
    def nextNotBlankChar(s, i):
        while i + 1 < len(s) and s[i + 1] == ' ':
            i += 1
        return i + 1

    @staticmethod
    # Return the index of previous not white space char begin from i - 1
    def prevNotBlankChar(s, i):
        while i - 1 >= 0 and s[i - 1] == ' ':
            i -= 1
        if s[i - 1] == ' ':
            return -1
        return i - 1

    # remove from index start to end - 1(inclusive)
    @staticmethod
    def remove(s, start, end):
        if len(s) > end and start >= 0:
            s = s[0: start] + s[end:]
        return s

    # Check whether string only contains')' '}' ']'
    @staticmethod
    def checkBracketsOnly(s):
        s = s.strip()
        for ch in s:
            if ch != ')' and ch != '}' and ch != ']':
                return False
        return True

    # For string s, add num of spaces between index i and index j
    @staticmethod
    def spaceController(s, i, j, num):
        if i >= 0 and j < len(s):
            s = s[0: i + 1] + num * " " + s[j: len(s)]
        return s

    def read(self, obj: object, recursive=False):
        if not recursive:
            if os.path.exists(obj):
                with open(obj, 'r', encoding="utf8") as f:
                    self.text = f.read()
                    self.path = obj
            else:
                self.text = obj
                self.isText = True
            self.lines = self.text.split("\n")
        else:
            if os.path.isdir(obj):
                directory = obj
                pathname = directory + "/**/*.txt"
                paths = glob.glob(pathname, recursive=True)
                for path in paths:
                    formatter = Formatter()
                    sample = formatter.read(path)
                    self.formatters.append(sample)
            else:
                print("no such file path")
        return self

    def show(self):
        res = ""
        for i in range(len(self.lines) - 1):
            res += self.lines[i] + '\n'
        res += self.lines[len(self.lines) - 1]
        self.text = res
        print(self.text)

    def rewrite(self):
        f = open(self.path, "w")
        res: str = ""
        for i in range(len(self.lines) - 1):
            res += self.lines[i] + '\n'
        res += self.lines[len(self.lines) - 1]
        self.text = res
        f.write(self.text)
        f.close()
        print("formatted: " + self.path)
        return self

    # Format the indentation of each line:

    def _FormatIndentation(self):
        indention = 0
        usualIndention = True
        start = 0
        i = 0
        lines = self.lines
        while i < len(lines):
            # if 'def' or 'class' or 'for' or 'if' or 'else' in lines[i]:
            #     space = self.countStartSpace(lines[i])
            #
            # if ':' in lines[i]:
            #     space += 4
            #     lines[i + 1] = lines[i + 1].strip(" ")
            #     lines[i + 1] = space * " " + lines[i + 1]
            #     space = 0

            if ')' in lines[i] and '(' in lines[i] \
                    and lines[i].count('(') == lines[i].count(')'):
                i += 1
                continue

            if '(' in lines[i]:
                index = lines[i].index('(')
                indention = self.countStartSpace(lines[i])
                start = i + 1
                if index != len(lines[i]) - 1:
                    indention = index + 1
                    usualIndention = False
                else:
                    indention += 4

            if ')' in lines[i]:
                end = i
                if usualIndention:
                    if i == len(lines) - 1 or self.emptyLine(lines[i + 1]):
                        i += 1
                        continue
                    else:
                        indention += 4
                while start <= end:
                    lines[start] = lines[start].strip()
                    lines[start] = indention * " " + lines[start]
                    start += 1
                indention = 0
            i += 1
        self.lines = lines
        return self

    # Limit the length of each line, if exceed 80 chars, move to next line
    # cut by keySymbols = {"=", "!=", "<", ">", "+", "-", "in", "not in", "is", "is not", "and", "or", "*", "/"}
    # if exceed things are only close ) ] } we don't cut
    def _FormatLineLength(self):
        i = 0
        lines = self.lines
        while i < len(lines):
            charLen = self.countChar(lines[i])
            if charLen > 80 and not (self.checkBracketsOnly(lines[i].replace(" ", "")[80:])):
                end = len(lines[i])
                currStr = lines[i][0:end]
                # get the first 80 character string then break
                while self.countChar(currStr) > 79:
                    end -= 1
                    currStr = lines[i][0:end]
                # find the close to end most key symbol
                endSymbol = ""
                breakIndex = -1
                for symbol in self.keySymbols:
                    symbolIndex = currStr.rfind(symbol)  # find the start index of symbol
                    if symbolIndex > breakIndex:
                        breakIndex = symbolIndex
                        endSymbol = symbol
                if breakIndex == -1:
                    print("Can't break line" + i)
                    break
                # add the rest to next line
                spaceNum = lines[i].index('(')
                breakIndex += len(endSymbol) + 1
                nextLine = lines[i][breakIndex: len(lines[i])]
                nextLine.lstrip()
                spaceNum += 4
                nextLine = spaceNum * " " + nextLine
                lines.insert(i + 1, nextLine)
                # cut the current line
                lines[i] = lines[i][0:breakIndex] + ' \\'
            i += 1
        self.lines = lines
        return self

    # Format operator, if operator is the last thing of the line
    # move it to the first of next line
    def _FormatBinOperator(self):
        i = 0
        lines = self.lines
        while i < len(lines):
            lines[i] = lines[i].rstrip()
            length = len(lines[i])
            if length < 1:
                i += 1
                continue
            if lines[i][length - 1] in self.calSymbol:  # find last char is cal symbol
                symbol = lines[i][length - 1]
                # cut the last symbol
                lines[i] = lines[i][0: length - 1]
                # modify the next line
                spaces = self.countStartSpace(lines[i + 1])
                lines[i + 1] = spaces * " " + symbol + " " + lines[i + 1].lstrip()
            i += 1
        self.lines = lines
        return self

    # basic idea for format blank line:
    # find def then delete check the line before, if comments, keep going up,
    # if not index == 0 and indention of that line bigger than or equals to that def line we will add an empty line
    # and make sure only add one empty line
    def _FormatVerticalBlank(self):
        i = 0
        lines = self.lines
        while i < len(lines):
            if "import" in lines[i]:
                lineIndex = self.nextNotEmptyLine(i)
                if lineIndex == len(lines):
                    del lines[i + 1: len(lines)]
                    return self
                else:
                    if "import" not in lines[lineIndex]:
                        lines.insert(i + 1, "")
                        del lines[i + 2: self.nextNotEmptyLine(i)]
                    i = self.nextNotEmptyLine(i)
                    continue

            if i != 0:
                string = lines[i].strip()
                # if the line before def function is not blank add one to it
                if string.find('def') == 0:
                    index = i - 1
                    indention = self.countStartSpace(lines[i])
                    # check if comments before functions
                    while index >= 0 and self.firstChar(lines[index]) == '#':
                        if self.countStartSpace(lines[index]) != indention:
                            lines[index] = " " * indention + lines[index].strip()
                        index -= 1
                    if index > 0 and self.countChar(lines[index]) > 0 and self.countStartSpace(lines[index]) \
                            >= indention:
                        lines.insert(index + 1, "")
                        del lines[index + 2: self.nextNotEmptyLine(index)]
                        i += 1

            i += 1
        self.lines = lines
        return self

    # create 3 lists to contain 3 different import groups
    # Delete original import line
    # add them back to start
    def _FormatImports(self):
        imports1 = []
        imports2 = []
        imports3 = []
        i = 0
        lines = self.lines
        while i < len(lines):
            line = lines[i]
            if "import" in line:
                if not ("from" in line):
                    if ',' in line:
                        importList = line.split(',')
                        imports1.append(importList[0])
                        j = 1
                        while j < len(importList):
                            imports1.append("import " + importList[j])
                            j += 1
                    else:
                        imports1.append(line)
                else:
                    if self.firstChar(line) == '.' or '/' in line:
                        imports3.append(line)
                    else:
                        imports2.append(line)
                del lines[i]
                i -= 1
            i += 1
        index = 0
        if (len(imports1)) > 0:
            for newLine in imports1:
                lines.insert(index, newLine)
                index += 1
        if len(imports2) > 0:
            if index > 0:
                lines.insert(index, "")
                index += 1
            for newLine in imports2:
                lines.insert(index, newLine)
                index += 1
        if len(imports3) > 0:
            if index > 0:
                lines.insert(index, "")
                index += 1
            for newLine in imports3:
                lines.insert(index, newLine)
                index += 1
        self.lines = lines
        return self

    def _FormatWhiteSpaces(self):
        i = 0
        lines = self.lines
        while i < len(lines):
            line = lines[i]
            line = line.rstrip()
            operatorSpace = 0
            # Deal with operator two sides space
            if self.emptyLine(line):
                i += 1
                continue
            startSpace = self.countStartSpace(line)
            # if contains symbol then operatorSpace = 1
            for symbol in self.keySymbols:
                if symbol in line:
                    operatorSpace = 1
                    break
            strings = line.split(" ")
            try:
                while True:
                    strings.remove("")
            except ValueError:
                pass

            line = startSpace * " "
            for s in strings:
                line += s + " "
            j = 0
            while j < len(line):
                if line[j] == '(' or line[j] == '{' or line[j] == '[':
                    if j != len(line) - 1:
                        line = self.remove(line, j + 1, self.nextNotBlankChar(line, j))
                        if self.prevNotBlankChar(line, j) != -1:
                            line = self.remove(line, self.prevNotBlankChar(line, j) + 1, j)
                elif line[j] == ')' or line[j] == '}' or line[j] == ']' or line[j] == ',' \
                        or line[j] == ';' or (line[j] == ':' and j == len(line) - 1):
                    previndex = self.prevNotBlankChar(line, j)
                    if previndex != -1:
                        line = self.remove(line, previndex + 1, j)
                        j = previndex + 1
                elif line[j] == ':':
                    previndex = self.prevNotBlankChar(line, j)
                    line = self.remove(line, previndex + 1, j)
                    j = previndex + 1
                    nextindex = self.nextNotBlankChar(line, j)
                    line = self.remove(line, j + 1, nextindex)
                    line = line[0:j] + operatorSpace * " " + ":" + operatorSpace * " " + line[j + 1: len(line)]
                    j = j + operatorSpace
                if line[j] == ',':
                    if j != len(line) - 1:
                        nextindex = self.nextNotBlankChar(line, j)
                        if nextindex < len(line) and [nextindex] == ')':
                            line = self.remove(line, j + 1, nextindex)
                if line[j] == ';':
                    startSpace = self.countStartSpace(line)
                    newLine = startSpace * " " + line[j + 1: len(line)].lstrip()
                    lines.insert(i + 1, newLine)
                    line = line[:j + 1]
                j += 1
            lines[i] = line
            i += 1
            self.lines = lines
        return self

    def _format(self):
            self._FormatImports()
            self._FormatIndentation()
            self._FormatLineLength()
            self._FormatBinOperator()
            self._FormatVerticalBlank()
            self._FormatWhiteSpaces()
            if not self.isText:
                self.rewrite()
            else:
                self.show()

    def _Reformat(self):
        for sample in self.formatters:
            sample._format()

formatter = Formatter()
code = formatter.read("tests", recursive=True)
code._Reformat()
