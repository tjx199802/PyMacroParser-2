# -*- coding:utf-8 -*-


import pytest
from myparser.pymacroparser import Util, PyMacroParser, Convert, Find, Judge
from myparser.log import logger


class TestUtil:

    @pytest.mark.parametrize(('src'), [('test/case/tuple.data')])
    def test_tuple_skeleton(self, src):
        with open(src) as fr:
            ss = unicode(fr.read(), 'utf8').split(u'\n')
        for s in ss:
            print(Util.tuple_skeleton(s))

    @pytest.fixture(scope='class')
    def unicode_str(self):
        f = 'test/b.cpp'
        with open(f) as fr:
            unicode_str = unicode(fr.read(), 'utf-8')
        print(unicode_str)
        return unicode_str

    def test_find_all(self):
        pass

    @pytest.mark.parametrize('src, dst',
                             [('test/case/comment_.cpp', 'test/case/comment_e.cpp'),
                              ('test/case/overall_.cpp',
                               'test/case/overall_e.cpp'),
                              ('test/case/a_.cpp', 'test/case/a_e.cpp')])
    def test_extract_directives(self, src, dst):
        with open(src) as fr:
            s = unicode(fr.read(), 'utf8')
        ds = Util.extract_directives(s)
        with open(dst, 'w') as fw:
            for d in ds:
                fw.write(d + u'\n')

    def test_findword(self):
        pass

    def test_is_legal_identifier(self):
        # ss = ['data1', '_data', '7data', 'da_dk7']
        ss = ['MC_TEST']
        for s in ss:
            print(s, ' --> ', Util.is_legal_identifier(s))

    @pytest.mark.parametrize('src, dst', [
        ('test/case/comment.cpp', 'test/case/comment_.cpp'),
        ('test/case/overall.cpp', 'test/case/overall_.cpp'),
        ('test/case/a.cpp', 'test/case/a_.cpp'),
        ('test/case/case2.cpp', 'test/case/case2_.cpp'),
        ('test/case/case3.cpp', 'test/case/case3_.cpp')])
    def test_remove_comment(self, src, dst):
        with open(src) as fr:
            s = unicode(fr.read(), 'utf8')
        new_s = Util.remove_comment(s)
        with open(dst, 'w') as fw:
            fw.write(new_s)


class TestFind:
    @pytest.mark.parametrize(('src'), [('test/case/tuple.cpp')])
    def test_find_comma(self, src):
        with open(src) as fr:
            ss = unicode(fr.read(), 'utf8').split(u'\n')
        for s in ss:
            c = 0
            i = Find.find_comma(s, 0, len(s))
            while i != -1:
                # print(str(i) + u'\t' + s[i-1:i+2])
                i = Find.find_comma(s, i + 1, len(s))
                c += 1
            print(c)

    def test_find_char_end(self, s, i):
        pass

    def test_find_identifier(self, d):
        pass


class TestPyMacroParser:
    pass


class TestConvert:
    def test_c2p_int(self):
        pass

    def test_c2p_char(self):
        pass

    def test_c2p_float(self):
        pass

    def test_c2p_string(self):
        pass

    def test_c2p_wstring(self):
        pass

    @pytest.mark.parametrize(('src'), [('test/case/tuple.data')])
    def test_c2p_tuple(self, src):
        with open(src) as fr:
            ss = unicode(fr.read(), 'utf8').split(u'\n')
        m = {}
        for s in ss:
            m[s] = Convert.c2p_tuple(s)
        print(m)

    @pytest.mark.parametrize('src', [('test/case/overall.data'),
                                     ('test/case/string.cpp')])
    def test_c2p_word(self, src):
        with open(src) as fr:
            s = unicode(fr.read(), 'utf8')
        ds = s.split(u'\n')
        m = {}
        for i, d in enumerate(ds):
            d = d[1:].strip()
            if not d.startswith(u'{'):
                m[d] = Convert.c2p_word(d)
        logger.info(m)


class TestJudge:
    @pytest.mark.parametrize('src, dst',
                             [('test/case/overall_e.cpp', 'test/case/overall.data'),
                              ('test/case/tuple.cpp', 'test/case/tuple.data')])
    def test_judge_Ctype(self, src, dst):
        with open(src) as fr:
            s = unicode(fr.read(), 'utf8')
        ds = s.split(u'\n')
        fw = open(dst, 'w')
        for d in ds:
            if d.startswith(u'#define'):
                d = d[7:].strip()
                i_s, i_e = Find.find_identifier(d)
                # identifier = d[i_s:i_e]
                ctype = Judge.judge_Ctype(d[i_e:])
                # fw.write(str(ctype))
                # fw.write('\t')
                # fw.write(identifier)
                # fw.write('\t')
                fw.write(d[i_e:])
                fw.write('\n')
        fw.close()


def test_find_all(content):
    line_coment_indexes = Util.find_all(content, u'//')
    block_coment_start_indexes = Util.find_all(content, u'/*')
    block_coment_end_indexes = Util.find_all(content, u'*/')
    print(line_coment_indexes)
    print(block_coment_start_indexes)
    print(block_coment_end_indexes)
    return [line_coment_indexes, block_coment_start_indexes,
            block_coment_end_indexes]


def test_util_group_c2p():
    s = u'{ {2.0, "abc"}, {1.5, "def"}, {5.6f, "7.2"}}'
    # group = Util.group_c2p(s)
    # print(group)


def test_list2tuple():
    group = [[2.0, u'"abc"'], [
        1.5, [11, [u'"kkk', 8]], u'"def"'], [5.6, u'"7.2"']]
    group = Util.list2tuple(group)
    print(group)


def test_isfloat():
    ss = [u'0.5', u'7.2', u'8f', u'.5f', u'5.f', u'kk', u'"7.2"']
    for s in ss:
        print(s, Util.isfloat(s))


def test_str():
    s = 'k'

    print(s)


@pytest.fixture
def a_parser():
    return PyMacroParser()


@pytest.mark.parametrize(('src, dst'), [
    ('test/case/a.cpp', 'test/case/a_o.cpp'),
    ('test/case/b.cpp', 'test/case/b_o.cpp'),
    ('test/case/overall.cpp', 'test/case/overall_o.cpp'),
    ('test/case/overall_o.cpp', 'test/case/overall_o_o.cpp'),
    ('test/case/process1.cpp', 'test/case/process1_o.cpp'),
    ('test/case/process2.cpp', 'test/case/process2_o.cpp'),
    ('test/case/case1.cpp', 'test/case/case1.o.cpp'),
    ('test/case/case2.cpp', 'test/case/case2.o.cpp'),
    ('test/case/case3.cpp', 'test/case/case3.o.cpp'),
])
def test_case(a_parser, src, dst):
    a_parser.load(src)
    a_parser.dump(dst)

@pytest.mark.parametrize(('src'),[
    ('test/case/case1.o.cpp')
])
def test_load_dump(a_parser, src):
    a_parser.load(src)
    d1 = a_parser.dumpDict()
    a_parser.dump(src)
    
    a_parser.load(src)
    d2 = a_parser.dumpDict()
    a_parser.dump(src)
    
    a_parser.load(src)
    d3 = a_parser.dumpDict()

    assert d1 == d2 and d2 == d3    

if __name__ == "__main__":
    test_case1()
    # test_str()
    # test_isfloat()
    # test_list2tuple()

    # test_util_group_c2p()
    # test_find_all()
    # f = 'test/a.cpp'

    # p = PyMacroParser()
    # p.load(f)
    # print(p.dumpDict())
    # p.dump('test/b.cpp')
    # p.preDefine("MC1;MC2")
    # print(p.dumpDict())
    # p.dump('test/b.cpp')
    # print('Done!')
    # with open(f) as fr:
    #     content = unicode(fr.read(), 'utf-8')

    # line_coment_indexes = Util.find_all(content, u'//')
    # content1 = Util.remove_line_comment(content, line_coment_indexes)
    # # print(content1)
    # block_coment_start_indexes = Util.find_all(content1, u'/*')
    # block_coment_end_indexes = Util.find_all(content1, u'*/')
    # content2 = Util.remove_block_comment(content1, block_coment_start_indexes,
    #                                      block_coment_end_indexes)
    # # print(content2)
    # directives = Util.extract_directives(content2)
    # # for d in directives:
    # #     print(d)
    # # # print(directives)
