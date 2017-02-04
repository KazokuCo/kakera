from django.test import TestCase
from wagtail.wagtailcore.blocks import StreamValue
from kakera_core.models import CustomImage
from kakera_blog.models import DefaultStreamBlock
from kakera_blog.util import count_words, calc_read_time

class TestCountWords(TestCase):
    def test_empty_string(self):
        self.assertEqual(count_words(""), 0)

    def test_gibberish(self):
        self.assertEqual(count_words("$!#(/"), 0)

    def test_one_word(self):
        self.assertEqual(count_words("lorem"), 1)

    def test_two_words(self):
        self.assertEqual(count_words("lorem ipsum"), 2)

    def test_three_words(self):
        self.assertEqual(count_words("lorem ipsum dolor"), 3)

    def test_parenthesis(self):
        self.assertEqual(count_words("lorem (ipsum) dolor"), 3)

    def test_slash(self):
        self.assertEqual(count_words("lorem ipsum/dolor"), 3)

class TestCalcReadTime(TestCase):
    TEXT_1MIN = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam turpis orci, pretium a luctus vel, rutrum vel metus. Duis eu mi ac dui consectetur volutpat. Praesent convallis bibendum eros, id maximus augue finibus vel. Donec nulla elit, ullamcorper nec mattis at, aliquet ac lacus. Ut consequat quam ut tortor consectetur dignissim. Aenean quis mi nec lorem bibendum aliquet et nec velit. Nulla condimentum, quam at porttitor convallis, justo purus tincidunt augue, sed varius urna est at erat. Donec sodales felis et mi consectetur euismod. Mauris at auctor mauris. Suspendisse dictum pharetra massa, eget tincidunt ipsum dignissim vel. Quisque suscipit elementum imperdiet. In lacinia faucibus turpis, nec malesuada felis facilisis id. Praesent ut dictum nulla, vel sodales dui. Donec interdum non ipsum vitae eleifend. Nam semper ex eu purus euismod, in mollis metus pharetra. Duis malesuada leo sit amet est bibendum aliquet.

Donec sem dolor, vestibulum quis rhoncus ac, ornare et sem. Mauris diam mi, faucibus et eros et, aliquam suscipit nisl. Fusce vel mauris lectus. Vestibulum sed diam eget lectus pharetra sodales vitae non nulla. Vestibulum et odio et libero vulputate finibus. Curabitur semper lobortis odio, at dapibus felis dapibus in. Nulla sed dolor eu eros fermentum sagittis. Pellentesque sed pellentesque nisl. Vestibulum vulputate quam sit amet diam fringilla, sed scelerisque nunc suscipit. Duis a nunc sed tellus vestibulum aliquet in sit amet enim. Morbi rhoncus posuere sem, ullamcorper placerat risus elementum quis. Nunc gravida lorem in enim imperdiet lacinia.

Integer venenatis semper nisi non varius. Mauris luctus felis lacus, a rhoncus lorem feugiat ut. Vestibulum sed dictum lacus. Curabitur vitae ligula sollicitudin, hendrerit erat vitae, commodo augue. Cras eu augue nibh. Pellentesque eros velit.'''

    def test_blank_article(self):
        self.assertEqual(calc_read_time(StreamValue(DefaultStreamBlock(), [])), 0)

    def test_one_minute(self):
        self.assertEqual(calc_read_time(StreamValue(DefaultStreamBlock(), [
            ('markdown', self.TEXT_1MIN),
        ])), 60)

    def test_two_minutes(self):
        self.assertEqual(calc_read_time(StreamValue(DefaultStreamBlock(), [
            ('markdown', self.TEXT_1MIN),
            ('markdown', self.TEXT_1MIN),
        ])), 120)

    def test_one_minute_plus_cover(self):
        self.assertEqual(calc_read_time(StreamValue(DefaultStreamBlock(), [
            ('markdown', self.TEXT_1MIN),
        ]), CustomImage()), 72)

    def test_image(self):
        self.assertEqual(calc_read_time(StreamValue(DefaultStreamBlock(), [
            ('image', CustomImage()),
        ])), 12)

    def test_image_with_cover(self):
        self.assertEqual(calc_read_time(StreamValue(DefaultStreamBlock(), [
            ('image', CustomImage()),
        ]), CustomImage()), 23)

    def test_images(self):
        times = {
             0: 0,
             1: 12,
             2: 12+11,
             3: 12+11+10,
             4: 12+11+10+9,
             5: 12+11+10+9+8,
             6: 12+11+10+9+8+7,
             7: 12+11+10+9+8+7+6,
             8: 12+11+10+9+8+7+6+5,
             9: 12+11+10+9+8+7+6+5+4,
            10: 12+11+10+9+8+7+6+5+4+3,
            11: 12+11+10+9+8+7+6+5+4+3+3,
            12: 12+11+10+9+8+7+6+5+4+3+3+3,
            13: 12+11+10+9+8+7+6+5+4+3+3+3+3,
            14: 12+11+10+9+8+7+6+5+4+3+3+3+3+3,
            15: 12+11+10+9+8+7+6+5+4+3+3+3+3+3+3,
        }
        for n, t in times.items():
            blocks = [('image', CustomImage()) for _ in range(n)]
            self.assertEqual(calc_read_time(StreamValue(DefaultStreamBlock(), blocks)), t)

    def test_images_with_cover(self):
        times = {
             0: 12,
             1: 12+11,
             2: 12+11+10,
             3: 12+11+10+9,
             4: 12+11+10+9+8,
             5: 12+11+10+9+8+7,
             6: 12+11+10+9+8+7+6,
             7: 12+11+10+9+8+7+6+5,
             8: 12+11+10+9+8+7+6+5+4,
             9: 12+11+10+9+8+7+6+5+4+3,
            10: 12+11+10+9+8+7+6+5+4+3+3,
            11: 12+11+10+9+8+7+6+5+4+3+3+3,
            12: 12+11+10+9+8+7+6+5+4+3+3+3+3,
            13: 12+11+10+9+8+7+6+5+4+3+3+3+3+3,
            14: 12+11+10+9+8+7+6+5+4+3+3+3+3+3+3,
            15: 12+11+10+9+8+7+6+5+4+3+3+3+3+3+3+3,
        }
        for n, t in times.items():
            blocks = [('image', CustomImage()) for _ in range(n)]
            self.assertEqual(calc_read_time(StreamValue(DefaultStreamBlock(), blocks), CustomImage()), t)
