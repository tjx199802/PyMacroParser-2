# -*- coding:utf-8 -*-
"""PyMacroParser"""


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


class PreprocessorType:
    ILLEGAL = 0
    IFDEF = 1
    IFNDEF = 2
    ELSE = 3
    ENDIF = 4
    DEFINE = 5
    UNDEF = 6


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
    def remove_comment(s):
        s = Util.remove_line_comment(s)
        s = Util.remove_block_comment(s)
        return s

    @staticmethod
    def remove_line_comment(s):
        new_s = u''
        start, end = 0, len(s)
        while start < end:
            line_comment_index = s.find(u'//', start)
            if line_comment_index == -1:
                new_s += s[start:]
                break
            else:
                new_s += s[start:line_comment_index]
                new_line_index = s.find(u'\n', line_comment_index + 2)
                if new_line_index == -1:
                    break
                else:
                    start = new_line_index
        return new_s

    @staticmethod
    def remove_block_comment(s):
        new_s = u''
        start, end = 0, len(s)
        while start < end:
            block_comment_start_index = s.find(u'/*', start)
            if block_comment_start_index == -1:
                new_s += s[start:]
                break
            else:
                new_s += s[start:block_comment_start_index]
                block_comment_end_index = s.find(u'*/',
                                                 block_comment_start_index + 2)
                if block_comment_end_index == -1:
                    break
                else:
                    start = block_comment_end_index + 2
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
        if s[0] == u'_' or s[0].isalpha():
            s = s[1:]
            for c in s:
                if c != u'_' and not c.isalpha() and not c.isalnum():
                    return False
            return True
        return False


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
        macro_name_start, macro_name_end = Util.findword(d, 8, len(d))
        macro_name = d[macro_name_start:macro_name_end]
        macros[macro_name] = Convert.c2p(d[macro_name_end:])

    @staticmethod
    def execute_undef(d, macros):
        macro_name_start, macro_name_end = Util.findword(d, 7, len(d))
        macro_name = d[macro_name_start:macro_name_end]
        if macro_name in macros:
            macros.pop(macro_name)

    @staticmethod
    def execute_ifdef(directives, start, directives_skeleton, macros):
        d = directives[start]
        macro_name_start, macro_name_end = Util.findword(d, 7, len(d))
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
        d = directives[start]
        macro_name_start, macro_name_end = Util.findword(d, 7, len(d))
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
        for d in directives:
            if not Check.check_directive(d):
                return False
        return True

    @staticmethod
    def check_directive(d):
        d = d.strip()
        # logger.info('check directive --> ' + d)
        if d.startswith('#ifdef'):
            return Check.check_ifdef(d)
        if d.startswith('#ifndef'):
            return Check.check_ifndef(d)
        if d.startswith('#else'):
            return True
        if d.startswith('#endif'):
            return True
        if d.startswith(u'#define'):
            return Check.check_define(d)
        if d.startswith(u'#undef'):
            return Check.check_undef(d)
        raise PreprocessorSytaxException()

    @staticmethod
    def check_ifdef(d):
        """The first word following'#ifdef ' must be a legal identifier."""
        word_start, word_end = Util.findword(d, 7, len(d))
        if word_start < word_end:
            word = d[word_start:word_end]
            return Util.is_legal_identifier(word)
        return False

    @staticmethod
    def check_ifndef(d):
        word_start, word_end = Util.findword(d, 8, len(d))
        if word_start < word_end:
            word = d[word_start:word_end]
            return Util.is_legal_identifier(word)
        return False

    @staticmethod
    def check_define(d):
        word_start, word_end = Util.findword(d, 8, len(d))
        if word_start < word_end:
            word = d[word_start:word_end]
            return Util.is_legal_identifier(word)
        return False

    @staticmethod
    def check_undef(d):
        """The first word following'#undef ' must be a legal identifier."""
        word_start, word_end = Util.findword(d, 7, len(d))
        if word_start < word_end:
            word = d[word_start:word_end]
            return Util.is_legal_identifier(word)
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
