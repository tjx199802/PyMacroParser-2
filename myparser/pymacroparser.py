# -*- coding:utf-8 -*-
"""PyMacroParser"""


class ConstantException(Exception):
    """Exception about constant of cpp basic type."""
    pass


class AggregateException(Exception):
    """Exception about cpp aggregate."""
    pass


class IdentifierException(Exception):
    """Exception about cpp identifier."""
    pass


class DirectiveHeaderException(Exception):
    """Exception about ilegal directive type."""
    pass


class SourceSyntaxException(Exception):
    """Exception about other cpp source syntax."""
    pass


class Util:
    @staticmethod
    def execute_directives(directives):
        """Execute directives using stack.

        Arguments:
        directives -- list
        """
        effective = True  # record current state
        ifstack = []
        macros = {}
        for d in directives:
            if effective:
                if d.startswith(u'#define'):
                    i_start, i_end = Find.find_identifier(d)  # can handle execption
                    identifier = str(d[i_start:i_end])
                    macros[identifier] = Convert.c2p(d[i_end:])
                elif d.startswith(u'#undef'):
                    # suppose character exists after '#undef' by default
                    i_start, i_end = Find.find_identifier(d)
                    identifier = str(d[i_start:i_end])
                    if identifier in macros:
                        macros.pop(identifier)
                elif d.startswith(u'#ifdef'):
                    i_start, i_end = Find.find_identifier(d)
                    identifier = str(d[i_start:i_end])
                    ifstack.append(effective)
                    effective = identifier in macros
                elif d.startswith(u'#ifndef'):
                    i_start, i_end = Find.find_identifier(d)
                    identifier = str(d[i_start:i_end])
                    ifstack.append(effective)
                    effective = identifier not in macros
                elif d.startswith(u'#else'):
                    effective = not effective
                elif d.startswith(u'#endif'):
                    effective = ifstack.pop()
            else:
                if d.startswith(u'#ifdef'):
                    ifstack.append(effective)
                elif d.startswith(u'#ifndef'):
                    ifstack.append(effective)
                elif d.startswith(u'#else'):
                    effective = ifstack[-1]
                elif d.startswith(u'#endif'):
                    effective = ifstack.pop()
        if ifstack:
            raise SourceSyntaxException('branches error')
        return macros

    @staticmethod
    def remove_comment(s):
        """Remove C/C++ comment.

        Arguments:
        s - - unicode
        """
        i = 0
        new_s = u''
        while i < len(s):
            c = s[i]
            if c == u'\"':
                string_end = Find.find_string_end(s, i)  # can handle exception
                new_s += s[i:string_end + 1]
                i = string_end + 1
            elif c == u'\'':
                char_end = Find.find_char_end(s, i)  # can handle exception
                new_s += s[i:char_end + 1]
                i = char_end + 1
            elif c == u'/':
                i += 1
                c = s[i]
                if c == u'/':
                    # line comment begins
                    newline_index = s.find(u'\n', i + 1)
                    if newline_index == -1:
                        i = len(s)
                    else:
                        i = newline_index
                elif c == u'*':
                    # block comment begins
                    block_comment_end = s.find(u'*/', i + 1)
                    if block_comment_end == -1:
                        raise SourceSyntaxException(
                            'block comment without ending')
                    new_s += u' '
                    i = block_comment_end + 2
                else:
                    raise SourceSyntaxException('alone slash')
            else:
                new_s += c
                i += 1
        return new_s

    @staticmethod
    def extract_directives(s):
        """Extract all directives into a list.

        Suppose all directives are legal.
        """
        directives = [Util.formalize_directive(d)
                      for d in s.split(u'\n') if d.strip()]
        # TODO handle exception
        return directives

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

    @staticmethod
    def deepcopy(d):
        d_cp = {}
        for k in d:
            d_cp[k] = d[k]
        return d_cp


class Find:
    @staticmethod
    def find_constant(s, start):
        """Find a constant from an aggregate."""
        while start < len(s) and s[start].isspace():
            start += 1
        i = start
        while i < len(s):
            if s[i] == u'\'':
                i = Find.find_char_end(s, i) + 1
            elif s[i] == u'\"':
                i = Find.find_string_end(s, i) + 1
            elif s[i] == u',' or s[i] == u'}':
                return start, i
            else:
                i += 1
        raise ConstantException('Can\'t find a constant.')

    @staticmethod
    def find_identifier(d):
        """Find a potential macro name identifier from str d.

        Suppose there are no identifiers with parameters

        Arguments:
        d - - unicode, a directive with header removed, without blank ends
        """
        start = d.find(u'#')
        while start < len(d) and not d[start].isspace():
            start += 1
        i_start, i_end = Find.find_word(d, start, len(d))
        if Judge.isidentifier(d[i_start:i_end]):
            return i_start, i_end
        raise IdentifierException()

    @staticmethod
    def find_word(s, start, end):
        while start < end and s[start].isspace():
            start += 1
        word_start = start
        while start < end and not s[start].isspace():
            start += 1
        word_end = start
        return [word_start, word_end]

    @staticmethod
    def find_string_end(s, i):
        """Find the end of the string.

        All characters in string constant must be on the same line.

        Arguments:
        s - - unicode
        i - - the index of the string beginning(left double quotation)
        """
        start = i + 1
        while start < len(s) and s[start] != u'\n':
            if s[start] == u'\"' and not Judge.isescaped(s, start):
                return start
            start += 1
        raise ConstantException('No string end.')

    @staticmethod
    def find_char_end(s, i):
        start = i + 1
        while start < len(s) and s[start] != u'\n':
            if s[start] == u'\'' and not Judge.isescaped(s, start):
                return start
            start += 1
        raise ConstantException('No char end.')


class Judge:
    @staticmethod
    def isidentifier(s):
        """Determine whether a string is an identifier.

        Suppose no identifier with parameters.

        Arguments:
        s - - unicode
        """
        if not s or s.isspace():
            return False
        if s[0] == u'_' or s[0].isalpha():
            s = s[1:]
            for c in s:
                if c != u'_' and not c.isalnum():
                    return False
            return True
        return False

    @staticmethod
    def isescaped(s, i):
        """Determine whether the ith character of string i is escaped.

        s - - unicode
        i - - int
        """
        num_escape = 0
        while i > 0 and s[i - 1] == u'\\':
            num_escape += 1
            i -= 1
        return bool(num_escape % 2)

    @staticmethod
    def isbool(s):
        return s == u'true' or s == u'false'

    @staticmethod
    def isint(s):
        if s[0] == u'-' or s[0] == u'+':
            s = s[1:]
        if s[0].isdigit() and s.find(u'.') == -1 and \
                s.find(u'e') == -1 and s.find(u'E') == -1:
            return True
        return False

    @staticmethod
    def ischar(s):
        if s.endswith(u'\''):
            return True
        return False

    @staticmethod
    def isfloat(s):
        if s[0] == u'-' or s[0] == u'+':
            s = s[1:]
        if s[0].isdigit() or s[0] == u'.':
            if s.find(u'.') != -1 or s.find(u'e') != -1 or s.find(u'E') != -1:
                return True
        return False

    @staticmethod
    def isstring(s):
        if (s.endswith(u'"') or s.endswith(u'"s')) and not s.startswith(u'L'):
            return True
        return False

    @staticmethod
    def iswstring(s):
        s = s.strip()
        if s[0] == u'L':
            return True
        return False

    @staticmethod
    def istuple(s):
        s = s.strip()
        if s.startswith(u'{'):
            return True
        return False


class Convert:
    ESCAPE_MAP = {
        u'\\a': u'\a',
        u'\\b': u'\b',
        u'\\f': u'\f',
        u'\\n': u'\n',
        u'\\r': u'\r',
        u'\\t': u'\t',
        u'\\v': u'\v',
        u'\\\'': u'\'',
        u'\\"': u'\"',
        u'\\\\': u'\\',
    }
    UNESCAPE_MAP = {v: k for k, v in ESCAPE_MAP.items()}

    @staticmethod
    def c2p(s):
        s = s.strip()
        if Judge.istuple(s):
            return Convert.c2p_aggregate(s)  # can handle constant exception
        else:
            return Convert.c2p_constant(s)  # can handle constant exception

    @staticmethod
    def c2p_aggregate(s):
        """Convert aggregate into Python tuple.

        Arguments:
        s - - unicode
        """
        s = s.strip()
        stack = []
        i = 0
        while i < len(s):
            c = s[i]
            if c.isspace() or c == u',':
                i += 1
            elif c == u'{':
                if not stack:
                    group = []
                    stack.append(group)
                else:
                    new_list = []
                    stack[-1].append(new_list)
                    stack.append(new_list)
                i += 1
            elif c == u'}':
                stack.pop()
                i += 1
            else:
                start, end = Find.find_constant(s, i)
                constant = s[start:end]
                stack[-1].append(Convert.c2p_constant(constant))
                i = end
        if stack:
            raise AggregateException()
        return Util.list2tuple(group)

    @staticmethod
    def c2p_constant(s):
        """Convert cpp constant of basic type to python object.

        Arguments:
        s - - unicode
        """
        s = s.strip()
        if not s:
            return None
        if Judge.isbool(s):
            return Convert.c2p_bool(s)
        if Judge.isint(s):
            return Convert.c2p_int(s)
        if Judge.ischar(s):
            return Convert.c2p_char(s)
        if Judge.isfloat(s):
            return Convert.c2p_float(s)
        if Judge.isstring(s):
            return Convert.c2p_string(s)
        if Judge.iswstring(s):
            return Convert.c2p_wstring(s)
        raise ConstantException()

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
        # Judge positive or negative.
        flag = 1
        if s[0] == u'-':
            s = s[1:]
            flag = -1
        elif s[0] == u'+':
            s = s[1:]
        # Remove suffix.
        i = len(s) - 1
        while i >= 0 and (not s[i].isdigit() and not (s[i] >= u'a' and s[i] <= u'f') and
                          not (s[i] >= u'A' and s[i] <= u'F')):
            i -= 1
        s = s[:i + 1]

        if s.startswith(u'0x') or s.startswith(u'0X'):
            return flag * int(s, 16)
        elif s.startswith(u'0'):
            return flag * int(s, 8)
        else:
            return flag * int(s)

    @staticmethod
    def c2p_char(s):
        """Only consider ascii characters."""
        if s[1] == u'\\':
            if s[2] == u'x':
                return int(u'0x' + s[3:-1], 16)
            elif s[2].isdigit():
                return int(u'0' + s[2:-1], 8)
            else:
                return ord(Convert.ESCAPE_MAP[s[1:3]])
        return ord(s[1])

    @staticmethod
    def c2p_float(s):
        flag = 1
        if s[0] == u'-':
            s = s[1:]
            flag = -1
        elif s[0] == u'+':
            s = s[1:]
        # remove suffix
        i = len(s) - 1
        while i >= 0 and (not s[i].isdigit() and s[i] != u'.'):
            i -= 1
        s = s[:i + 1]

        e_index = s.find(u'e')
        E_index = s.find(u'E')
        if e_index != -1:
            return flag * float(s[:e_index]) * (10 ** int(s[e_index + 1:]))
        if E_index != -1:
            return flag * float(s[:E_index]) * (10 ** int(s[E_index + 1:]))
        return flag * float(s)

    @staticmethod
    def c2p_string(s):
        new_s = u''
        i = 0
        while i < len(s):
            start = s.find(u'\"', i)
            if start != -1:
                end = Find.find_string_end(s, start)
                word = s[start:end + 1]
                word = word[1:-1]
                i = end + 1
                j = 0
                new_word = u''
                while j < len(word):
                    if word[j] == u'\\' and j + 1 < len(word) and \
                            word[j:j+2] in Convert.ESCAPE_MAP:
                        new_word += Convert.ESCAPE_MAP[word[j:j+2]]
                        j += 2
                    else:
                        new_word += word[j]
                        j += 1
            new_s += new_word
        return str(new_s)

    @staticmethod
    def c2p_wstring(s):
        s = s[2:-1]
        i = 0
        new_s = u''
        while i < len(s):
            if s[i] == u'\\' and i + 1 < len(s) and \
                    s[i:i+2] in Convert.ESCAPE_MAP:
                new_s += Convert.ESCAPE_MAP[s[i:i+2]]
                i += 2
            else:
                new_s += s[i]
                i += 1
        return new_s

    @staticmethod
    def p2c(o):
        s = ''
        if isinstance(o, bool):
            s = Convert.p2c_bool(o)
        elif isinstance(o, int):
            s = Convert.p2c_int(o)
        elif isinstance(o, long):
            s = Convert.p2c_long(o)
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
    def p2c_long(o):
        return str(o)

    @staticmethod
    def p2c_float(o):
        return str(o)

    @staticmethod
    def p2c_string(o):
        s = ''
        for c in o:
            if c in Convert.UNESCAPE_MAP:
                s += Convert.UNESCAPE_MAP[c]
            else:
                s += c
        return '"' + s + '"'

    @staticmethod
    def p2c_wstring(o):
        return 'L' + Convert.p2c_string(str(o))

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

    def __init__(self):
        self._directives = []  # list
        self._predefine = []  # list
        self._macros = {}  # dict

    def load(self, f):
        """Load macro definition from .cpp file.

        Arguments:
        f - - str, file path
        """
        self._directives = []
        self._predefine = []
        self._macros = {}
        self._preprocessing(f)
        self._parser()

    def preDefine(self, s):
        """Define macros.

        The preDefine function can be called repeatedly, and each call
        automatically clears out the previous predefined macro sequence.

        Arguments:
        s - - str, names of macros split by ';'
        """
        self._predefine = []
        words = s.split(';')
        for w in words:
            if Judge.isidentifier(w):
                self._predefine.append(u'#define ' + w)
        self._parser()

    def dumpDict(self):
        """Output available macros into a dictionary.

        Returns:
        macros - - dict, available macros dictionary
        """
        return Util.deepcopy(self._macros)

    def dump(self, f):
        """Output available macros into a .cpp file.

        Arguments:
        f - - str, file path
        """
        with open(f, 'w') as fw:
            for macro in self._macros:
                line = '#define ' + macro + ' ' + \
                    Convert.p2c(self._macros[macro]) + '\n'
                fw.write(line)

    def _parser(self):
        """Parse preprocessor directives."""
        directives = self._predefine + self._directives
        self._macros = Util.execute_directives(directives)

    def _preprocessing(self, f):
        """Extracting preprocessor directives from .cpp file.

        Arguments:
        f - - str, file path

        Returns:
        directives - - list, preprocessor directives
        """
        with open(f) as fr:
            content = unicode(fr.read(), 'utf-8')
        content = Util.remove_comment(content)
        self._directives = Util.extract_directives(content)
