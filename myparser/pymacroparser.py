# -*- coding:utf-8 -*-
"""PyMacroParser"""
from myparser.log import logger


class ConstantException(Exception):
    pass


class PreprocessorSytaxException(Exception):
    pass


class Ctype:
    ILLEGAL = 0
    SPACE = 1
    BOOL = 2
    INT = 3
    CHAR = 4
    FLOAT = 5
    STRING = 6
    WSTRING = 7
    TUPLE = 8


class StringType:
    NORMAL_STRING = 0
    RAW_STRING = 1


class PreprocessorType:
    ILLEGAL = 0
    IFDEF = 1
    IFNDEF = 2
    ELSE = 3
    ENDIF = 4
    DEFINE = 5
    UNDEF = 6


class Find:
    @staticmethod
    def find_string_end(s, i):
        """Find the end of the string.

        Arguments:
        s -- unicode
        i -- the index of the string beginning(left double quotation)

        Returns:
        string_end -- int, return the index of string end, return -1 if no
                    string end is found.
        """
        # Determine the type of string: normal string or raw string
        string_type = Judge.string_type(s, i)
        if string_type == StringType.NORMAL_STRING:
            return Find.find_normal_string_end(s, i)
        return Find.find_raw_string_end(s, i)

    @staticmethod
    def find_normal_string_end(s, i):
        while True:
            dq_index = s.find(u'"', i + 1)
            if not Judge.is_escaped(s, dq_index):
                return dq_index
            i = dq_index

    @staticmethod
    def find_raw_string_end(s, i):
        newline_index = s.find(u'\n', i + 1)
        if newline_index == -1:
            return s.rfind(u'"', i + 1)
        else:
            return s.rfind(u'"', i + 1, newline_index)

    @staticmethod
    def find_char_end(s, i):
        while True:
            q_index = s.find(u'\'', i + 1)
            if not Judge.is_escaped(s, q_index):
                return q_index
            i = q_index

class Judge:
    @staticmethod
    def string_type(s, i):
        """Determine the type of string that starts from index i in s.

        Arguments:
        s -- unicode
        i -- the index of the string beginning(left double quotation)
        """
        if i > 1 and s[i-1] == u'R':
            return StringType.RAW_STRING
        return StringType.NORMAL_STRING

    @staticmethod
    def is_escaped(s, i):
        """Determine whether the ith character of string i is escaped.
        
        s -- unicode
        i -- int
        """
        num_escape = 0
        while i > 0 and s[i - 1] == u'\\':
            num_escape += 1
            i -= 1
        return bool(num_escape % 2)

class Util:

    @staticmethod
    def find_all(s, sub):
        sub_indexes = []
        index = s.find(sub)
        while index != -1:
            sub_indexes.append(index)
            index = s.find(sub, index + 1)
        return sub_indexes

    @staticmethod
    def find_identifier(d):
        """Find a potential macro name identifier from str d."""
        word_start, word_end = Util.findword(d, 0, len(d))
        if not word_start < word_end:
            raise PreprocessorSytaxException()
        left_bracket_index = d.find(u'(', word_start, word_end)
        if left_bracket_index == -1:
            if Util.is_legal_single_identifier(d[word_start:word_end]):
                return word_start, word_end
            else:
                raise PreprocessorSytaxException()
        if left_bracket_index != -1:
            if not Util.is_legal_single_identifier(d[word_start:left_bracket_index]):
                raise PreprocessorSytaxException()
            right_bracket_index = d.find(u')', left_bracket_index)
            if right_bracket_index == -1:
                raise PreprocessorSytaxException()
            else:
                arguments = d[left_bracket_index,
                              right_bracket_index].split(u',')
                for argument in arguments:
                    if not Util.is_legal_single_identifier(argument.strip()):
                        return PreprocessorSytaxException()
                return word_start, right_bracket_index

    @staticmethod
    def remove_comment(s):
        """Remove C/C++ comment.

        Arguments:
        s -- unicode
        """
        STATE_NORMAL = 0
        STATE_SLASH = 1

        state = STATE_NORMAL
        i = 0
        new_s = u''
        while i < len(s):
            c = s[i]
            if state == STATE_NORMAL:
                if c == u'"':
                    logger.info("This is the beginning of the string.")
                    string_end = Find.find_string_end(s, i)
                    logger.info('string: ' + str(i) + str(string_end))
                    assert string_end != -1, 'incomplete string'
                    if string_end == len(s) - 1:
                        new_s += s[i:]
                    else:
                        new_s += s[i:string_end + 1]
                    i = string_end + 1
                elif c == u'\'':
                    logger.info("This is the beginning of the char.")
                    char_end = Find.find_char_end(s, i)
                    assert char_end != -1, 'incomplete char'
                    if char_end == len(s) - 1:
                        new_s += s[i:]
                    else:
                        new_s += s[i:char_end + 1]
                    i = char_end + 1
                elif c == u'/':
                    i += 1
                    state = STATE_SLASH
                else:
                    new_s += c
                    i += 1
            elif state == STATE_SLASH:
                if c == u'/':
                    logger.info("This is the beginning of a line comment.")
                    newline_index = s.find(u'\n', i)
                    if newline_index == -1:
                        break
                    i = newline_index
                    state = STATE_NORMAL
                elif c == u'*':
                    logger.info("This is the beginning of a block comment.")
                    block_comment_end = s.find(u'*/', i + 1)
                    assert block_comment_end != -1, 'incomplete block comment'
                    i = block_comment_end + 2
                    state = STATE_NORMAL
                else:
                    raise Exception('alone slash')
        return new_s

    @staticmethod
    def extract_directives(s):
        directives = [Util.formalize_directive(d)
                      for d in s.split(u'\n') if d.strip()]
        if Check.check_directives(directives):
            return directives
        else:
            raise PreprocessorSytaxException()

    @staticmethod
    def formalize_directive(d):
        """If d(unicode) starts with '#', remove the spaces following it."""
        d = d.strip()
        if d.startswith(u'#'):
            start = 1
            while start < len(d) and d[start].isspace():
                start += 1
            d = u'#' + d[start:]
        return d

    @staticmethod
    def directives_skeleton(directives):
        skeleton = {}
        stack = []
        for i, d in enumerate(directives):
            if d.startswith(u'#if'):
                stack.append(i)
                skeleton[i] = {}
            if d.startswith(u'#else'):
                skeleton[stack[-1]]['else'] = i
            if d.startswith(u'#endif'):
                skeleton[stack.pop()]['end'] = i
        if stack:
            raise PreprocessorSytaxException()
        return skeleton

    @staticmethod
    def isfloat(s):
        ret = False
        if not s.isspace():
            dot_index = s.find(u'.')
            if dot_index != -1:
                part1 = s[:dot_index]
                part2 = u''
                if dot_index != len(s) - 1:
                    part2 = s[dot_index + 1:]
                if part2.endswith(u'f'):
                    part2 = part2[:-1]
                if part1 and not part2:
                    ret = part1.isalnum()
                if part1 and part2:
                    ret = part1.isalnum() and part2.isalnum()
                if not part1 and part2:
                    ret = part2.isalnum()
        return ret

    @staticmethod
    def list2tuple(group):
        def recursion_l2t(group):
            # group = tuple(group)
            for i in range(len(group)):
                if isinstance(group[i], list):
                    recursion_l2t(group[i])
                    group[i] = tuple(group[i])
            # return group
        recursion_l2t(group)
        return tuple(group)
        # return group

    @staticmethod
    def c2p_judge_Ctype(s):
        # logger.info('s --> ' + s)
        if not s:
            return Ctype.SPACE
        if s == u'true' or s == u'false':
            return Ctype.BOOL
        if s.isalnum():
            return Ctype.INT
        if s.startswith(u"'") and s.endswith(u"'") and len(s) == 3:
            return Ctype.CHAR
        if Util.isfloat(s):
            return Ctype.FLOAT
        if s.startswith(u'"') and s.endswith(u'"'):
            return Ctype.STRING
        if s.startswith(u'L"') and s.endswith(u'"'):
            return Ctype.WSTRING
        if s.startswith(u'{') and s.endswith(u'}'):
            return Ctype.TUPLE
        else:
            return Ctype.ILLEGAL

    @staticmethod
    def p2c_judge_type(s):
        pass

    @staticmethod
    def deepcopy(d):
        d_cp = {}
        for k in d:
            d_cp[k] = d[k]
        return d_cp

    @staticmethod
    def findword(s, start, end):
        while start < end and s[start].isspace():
            start += 1
        word_start = start
        while start < end and not s[start].isspace():
            start += 1
        word_end = start
        return [word_start, word_end]

    @staticmethod
    def is_legal_identifier(s):
        """Determine if a string is a legal identifier or parameterized identifier.

        Arguments:
        s -- str, string without blank ends
        """
        return Util.is_legal_single_identifier(s) or Util.is_legal_parameterized_identifier

    @staticmethod
    def is_legal_single_identifier(s):
        """Determine if a string is a legal identifier.

        Arguments:
        s -- str, string without blank ends, non-empty
        """
        if s[0] == u'_' or s[0].isalpha():
            s = s[1:]
            for c in s:
                if c != u'_' and not c.isalnum():
                    return False
            return True
        return False

    @staticmethod
    def is_legal_parameterized_identifier(s):
        """Determine if a string is a legal parameterized identifier.

        Arguments:
        s -- str, string without blank ends
        """
        left_bracket_index = s.find(u'(')
        if left_bracket_index == -1:
            return False
        right_bracket_index = s.find(u')', left_bracket_index)
        if right_bracket_index == -1:
            return False
        arguments = s[left_bracket_index + 1:right_bracket_index].split(u',')
        for argument in arguments:
            if not Util.is_legal_single_identifier(argument):
                return False
        return True


class Execute:
    @staticmethod
    def execute_directives(directives):
        directives_skeleton = Util.directives_skeleton(directives)

        macros = Execute._execute_directives(directives, directives_skeleton)
        return macros

    @staticmethod
    def _execute_directives(directives, directives_skeleton):
        macros = {}
        Execute.__execute_directives(directives, 0, len(directives),
                                     directives_skeleton, macros)
        return macros

    @staticmethod
    def __execute_directives(directives, start, end, directives_skeleton, macros):
        while start < end:
            d = directives[start]
            if d.startswith(u'#define'):
                Execute.execute_define(d, macros)
                start += 1
            if d.startswith(u'#undef'):
                Execute.execute_undef(d, macros)
                start += 1
            if d.startswith(u'#ifdef'):
                Execute.execute_ifdef(
                    directives, start, directives_skeleton, macros)
                start = directives_skeleton[start]['end'] + 1
            if d.startswith(u'#ifndef'):
                Execute.execute_ifndef(
                    directives, start, directives_skeleton, macros)
                start = directives_skeleton[start]['end'] + 1

    @staticmethod
    def execute_define(d, macros):
        d = d[7:]
        macro_name_start, macro_name_end = Util.find_identifier(d)
        macro_name = d[macro_name_start:macro_name_end]
        macros[macro_name] = Convert.c2p(d[macro_name_end:])

    @staticmethod
    def execute_undef(d, macros):
        d = d[6:]
        macro_name_start, macro_name_end = Util.find_identifier(d)
        macro_name = d[macro_name_start:macro_name_end]
        if macro_name in macros:
            macros.pop(macro_name)

    @staticmethod
    def execute_ifdef(directives, start, directives_skeleton, macros):
        d = directives[start][6:]
        macro_name_start, macro_name_end = Util.find_identifier(d)
        macro_name = d[macro_name_start:macro_name_end]
        if macro_name in macros:
            if 'else' in directives_skeleton[start]:
                Execute.__execute_directives(directives, start + 1,
                                             directives_skeleton[start]['else'],
                                             directives_skeleton, macros)
            else:
                Execute.__execute_directives(directives, start + 1,
                                             directives_skeleton[start]['end'],
                                             directives_skeleton, macros)
        else:
            if 'else' in directives_skeleton[start]:
                Execute.__execute_directives(directives,
                                             directives_skeleton[start]['else'] + 1,
                                             directives_skeleton[start]['end'],
                                             directives_skeleton, macros)

    @staticmethod
    def execute_ifndef(directives, start, directives_skeleton, macros):
        d = directives[start][7:]
        macro_name_start, macro_name_end = Util.find_identifier(d)
        macro_name = d[macro_name_start:macro_name_end]
        if macro_name not in macros:
            if 'else' in directives_skeleton[start]:
                Execute.__execute_directives(directives, start + 1,
                                             directives_skeleton[start]['else'],
                                             directives_skeleton, macros)
            else:
                Execute.__execute_directives(directives, start + 1,
                                             directives_skeleton[start]['end'],
                                             directives_skeleton, macros)
        else:
            if 'else' in directives_skeleton[start]:
                Execute.__execute_directives(directives,
                                             directives_skeleton[start]['else'] + 1,
                                             directives_skeleton[start]['end'],
                                             directives_skeleton, macros)


class Check:
    @staticmethod
    def check_directives(directives):
        """Check if the directives are legal."""
        for d in directives:
            if not Check.check_directive(d):
                return False
        return True

    @staticmethod
    def check_directive(d):
        d = d.strip()
        # logger.info('check directive --> ' + d)
        if d.startswith(u'#ifdef'):
            return Check.check_ifdef(d)
        if d.startswith(u'#ifndef'):
            return Check.check_ifndef(d)
        if d.startswith(u'#else'):
            return True
        if d.startswith(u'#endif'):
            return True
        if d.startswith(u'#define'):
            return Check.check_define(d)
        if d.startswith(u'#undef'):
            return Check.check_undef(d)
        raise PreprocessorSytaxException()

    @staticmethod
    def check_ifdef(d):
        """The char following'#ifdef ' must be a space.

        Arguments:
        d -- str, starts with u'#ifdef'
        """
        d = d[6:]
        if d and d[0].isspace():
            return True
        return False

    @staticmethod
    def check_ifndef(d):
        """The char following'#ifndef ' must be a space.

        Arguments:
        d -- str, starts with u'#ifndef'
        """
        d = d[7:]
        if d and d[0].isspace():
            return True
        return False

    @staticmethod
    def check_define(d):
        """The char following'#define ' must be a space.

        Arguments:
        d -- str, starts with u'#ifndef'
        """
        d = d[7:]
        if d and d[0].isspace():
            return True
        return False

    @staticmethod
    def check_undef(d):
        """The char following'#undef ' must be a space.

        Arguments:
        d -- str, starts with u'#undef'
        """
        d = d[6:]
        if d and d[0].isspace():
            return True
        return False


class Convert:
    @staticmethod
    def c2p(s):
        s = s.strip()
        ctype = Util.c2p_judge_Ctype(s)
        if ctype == Ctype.ILLEGAL:
            raise ConstantException()
        elif ctype == Ctype.TUPLE:
            return Convert.c2p_tuple(s)
        else:
            return Convert.c2p_word(s)

    @staticmethod
    def c2p_space(s):
        pass

    @staticmethod
    def c2p_bool(s):
        if s == u'false':
            return False
        else:
            return True

    @staticmethod
    def c2p_int(s):
        if s.startswith(u'0x'):
            return int(s, 16)
        else:
            return int(s)

    @staticmethod
    def c2p_char(s):
        return ord(s[1])

    @staticmethod
    def c2p_float(s):
        if s.endswith(u'f'):
            s = s[:-1]
        return float(s)

    @staticmethod
    def c2p_string(s):
        return str(s[1:-1])

    @staticmethod
    def c2p_wstring(s):
        return s[2:-1]

    @staticmethod
    def c2p_tuple(s):
        def recursion_c2p_tuple(s, start, end, braces_indexes, group):
            while start < end:
                c = s[start]
                if not c.isspace() and not c == u',':
                    if c == u'{':
                        group.append([])
                        recursion_c2p_tuple(s, start + 1, braces_indexes[start],
                                            braces_indexes, group[-1])
                        start = braces_indexes[start] + 1
                    else:
                        word = None
                        comma_index = s.find(u',', start + 1, end)
                        if comma_index == -1:
                            word = s[start:end].strip()
                            start = end
                        else:
                            word = s[start:comma_index].strip()
                            start = comma_index + 1
                        obj = Convert.c2p_word(word)
                        group.append(obj)
                else:
                    start += 1

        braces_indexes = {}
        stack = []
        for i, c in enumerate(s):
            if c == u'{':
                stack.append(i)
            elif c == u'}':
                braces_indexes[stack.pop()] = i

        # logger.info(braces_indexes)
        group = []
        recursion_c2p_tuple(s, 1, len(s) - 1, braces_indexes, group)

        # logger.info(group)

        return Util.list2tuple(group)

    @staticmethod
    def c2p_word(s):
        ctype = Util.c2p_judge_Ctype(s)
        obj = None
        if ctype == Ctype.SPACE:
            Convert.c2p_space(s)
        if ctype == Ctype.BOOL:
            obj = Convert.c2p_bool(s)
        elif ctype == Ctype.INT:
            obj = Convert.c2p_int(s)
        elif ctype == Ctype.CHAR:
            obj = Convert.c2p_char(s)
        elif ctype == Ctype.FLOAT:
            obj = Convert.c2p_float(s)
        elif ctype == Ctype.STRING:
            obj = Convert.c2p_string(s)
        elif ctype == Ctype.WSTRING:
            obj = Convert.c2p_wstring(s)
        return obj

    @staticmethod
    def p2c(o):
        s = ''
        if isinstance(o, bool):
            s = Convert.p2c_bool(o)
        elif isinstance(o, int):
            s = Convert.p2c_int(o)
        elif isinstance(o, float):
            s = Convert.p2c_float(o)
        elif isinstance(o, str):
            s = Convert.p2c_string(o)
        elif isinstance(o, unicode):
            s = Convert.p2c_wstring(o)
        elif isinstance(o, tuple):
            s = Convert.p2c_tuple(o)
        return s

    @staticmethod
    def p2c_bool(o):
        return str(o).lower()

    @staticmethod
    def p2c_int(o):
        return str(o)

    @staticmethod
    def p2c_float(o):
        return str(o)

    @staticmethod
    def p2c_string(o):
        return '"' + o + '"'

    @staticmethod
    def p2c_wstring(o):
        return 'L"' + str(o) + '"'

    @staticmethod
    def p2c_tuple(o):
        def recursin_p2c_tuple(t):
            s = '{'
            for i in range(len(t)):
                s += Convert.p2c(t[i])
                if i == len(t) - 1:
                    continue
                s += ', '
            s += '}'
            return s

        return recursin_p2c_tuple(o)


class PyMacroParser:
    """PyMacroParser"""
    available_directives = ('#ifdef', '#ifndef', '#else',
                            '#endif', '#define', '#undef')

    def __init__(self):
        self._directives = []
        self._predefine = []
        self._macros = {}

    def load(self, f):
        """Load macro definition from .cpp file.

        Arguments:
        f -- str, file path
        """
        self._preprocessing(f)
        self._parser()

    def preDefine(self, s):
        """Define macros.

        The preDefine function can be called repeatedly, and each call
        automatically clears out the previous predefined macro sequence.

        Arguments:
        s -- str, names of macros split by ';'
        """
        self._predefine = []
        macros = s.split(';')
        for macro in macros:
            self._predefine.append('#define ' + macro)
        self._parser()

    def dumpDict(self):
        """Output available macros into a dictionary.

        Returns:
        macros -- dict, available macros dictionary
        """
        return Util.deepcopy(self._macros)

    def dump(self, f):
        """Output available macros into a .cpp file.

        Arguments:
        f -- str, file path
        """
        with open(f, 'w') as fw:
            for macro in self._macros:
                line = '#define ' + macro + ' ' + \
                    Convert.p2c(self._macros[macro]) + '\n'
                fw.write(line)

    def _parser(self):
        """Parse preprocessor directives."""
        directives = self._predefine + self._directives
        self._macros = Execute.execute_directives(directives)

    def _preprocessing(self, f):
        """Extracting preprocessor directives from .cpp file.

        Arguments:
        f -- str, file path

        Returns:
        directives -- list, preprocessor directives
        """
        with open(f) as fr:
            content = unicode(fr.read(), 'utf-8')
        content = Util.remove_comment(content)
        self._directives = Util.extract_directives(content)
