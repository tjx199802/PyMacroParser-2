# -*- coding:utf-8 -*-


import pytest
from myparser.pymacroparser import Util, PyMacroParser


class TestUtil:

    @pytest.fixture(scope='class')
    def unicode_str(self):
        f = 'test/b.cpp'
        with open(f) as fr:
            unicode_str = unicode(fr.read(), 'utf-8')
        print(unicode_str)
        return unicode_str

    def test_find_all(self):
        pass

    def test_extract_directives(self, unicode_str):
        unicode_str = Util.remove_line_comment(unicode_str)
        unicode_str = Util.remove_block_comment(unicode_str)
        directives = Util.extract_directives(unicode_str)
        for d in directives:
            print(d)

    def test_findword(self):
        ss = [u' ', u'\tk \t', u' kkk', u'dd kk', u'kk ', u'k " kk']
        for s in ss:
            print(s, ' --> ', Util.findword(s, 0, len(s)))

    def test_is_legal_identifier(self):
        # ss = ['data1', '_data', '7data', 'da_dk7']
        ss = ['MC_TEST']
        for s in ss:
            print(s, ' --> ', Util.is_legal_identifier(s))

    @pytest.mark.parametrize('src, dst',
                             [('test/case/comment.cpp', 'test/case/comment_.cpp'),
                             ('test/case/overall.cpp', 'test/case/overall_.cpp')])
    def test_remove_comment(self, src, dst):
        with open(src) as fr:
            s = unicode(fr.read(), 'utf8')
        new_s = Util.remove_comment(s)
        with open(dst, 'w') as fw:
            fw.write(new_s)

class TestFind:
    @staticmethod
    def test_find_char_end(s, i):
        pass
class TestPyMacroParser:
    pass


class TestConvert:
    pass


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


def test_case1():
    f = 'test/a.cpp'
    a1 = PyMacroParser()
    a2 = PyMacroParser()
    a1.load(f)
    filename = 'test/b.cpp'
    a1.dump(filename)
    a2.load(filename)
    print(a2.dumpDict())
    a1.preDefine("MC1;MC2")
    print(a1.dumpDict())
    a1.dump("test/c.cpp")


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
