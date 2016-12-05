import re

WORD_RE = re.compile(r'(?:[\w]+)')
def count_words(s):
    return len(WORD_RE.findall(s))

# This is based on Medium's algorithm for read time estimates:
# https://help.medium.com/hc/en-us/articles/214991667-Read-time
def calc_read_time(body, cover=None):
    word_cost = 60/275
    image_cost = 12
    image_cost_min = 3

    read_time = 0
    if cover:
        read_time += image_cost
        image_cost -= 1
    for block in body:
        if block.block_type == "markdown":
            read_time += int(count_words(block.value) * word_cost)
        elif block.block_type == "image" or block.block_type == "embed":
            read_time += image_cost
            if image_cost > image_cost_min:
                image_cost -= 1

    return read_time
