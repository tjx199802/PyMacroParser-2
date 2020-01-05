# -*- coding:utf-8 -*-


import pytest
from myparser.log import logger
from myparser.pymacroparser import Util, PyMacroParser, Convert, Find, Judge


@pytest.fixture
def a_parser():
    return PyMacroParser()


class TestUtil:

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

    def test_list2tuple(self):
        group = [[2.0, u'"abc"'], [
            1.5, [11, [u'"kkk', 8]], u'"def"'], [5.6, u'"7.2"']]
        group = Util.list2tuple(group)
        print(group)


class TestFind:
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
    def test_c2p_aggregate(self, src):
        with open(src) as fr:
            ss = unicode(fr.read(), 'utf8').split(u'\n')
        m = {}
        for s in ss:
            m[s] = Convert.c2p_aggregate(s)
        print(m)

    @pytest.mark.parametrize('src', [('test/case/overall.data'),
                                     ('test/case/string.cpp')])
    def test_c2p_constant(self, src):
        with open(src) as fr:
            s = unicode(fr.read(), 'utf8')
        ds = s.split(u'\n')
        m = {}
        for i, d in enumerate(ds):
            d = d[1:].strip()
            if not d.startswith(u'{'):
                m[d] = Convert.c2p_constant(d)
        logger.info(m)


class TestJudge:
    pass


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


@pytest.mark.parametrize(('src'), [
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
    pass
    # test_case1()
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
