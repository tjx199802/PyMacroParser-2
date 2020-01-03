import pytest

from myparser import util

@pytest.mark.parametrize('src, dst',
                          [('test/case/comment.cpp', 'test/case/comment_.cpp')])
def test_DelComment(src, dst):
    util.DelComment(src, dst)
