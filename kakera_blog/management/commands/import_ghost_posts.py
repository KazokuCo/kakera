import io
import re
import argparse
import json
import html5lib
import requests
import arrow
from urllib.parse import urlparse, parse_qs
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from django.db import transaction
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.blocks import StreamValue
from wagtail.wagtailimages.models import Image
from wagtail.wagtailembeds.blocks import EmbedValue
from kakera_core.models import User
from kakera_blog.models import DefaultStreamBlock, BlogPage, StaticPage

def import_image(url, title):
    r = requests.get(src)
    image = Image(title=title, file=ImageFile(io.BytesIO(r.content)))
    image.save()
    return image

def end_text_block(text, blocks):
    text = text.strip()
    if text != "":
        blocks.append(('markdown', text))
        # print(text)
    return ""

def node_to_text(node):
    if len(node.childNodes) == 1 and node.firstChild.nodeType == node.TEXT_NODE:
        return node.firstChild.data
    return node.toxml()

def handle_node(node, current_text_block, blocks):
    if node.nodeType == node.TEXT_NODE:
        current_text_block += node.data
    else:
        if node.tagName in ('center', 'p', 'div'):
            for child in node.childNodes:
                current_text_block = handle_node(child, current_text_block, blocks)
        elif node.tagName in ('h1', 'h2', 'h3', 'h4', 'h5', 'small', 'big', 'span', 'ul', 's', 'del', 'style', 'table'):
            current_text_block += node.toprettyxml()
        elif node.tagName == 'br':
            current_text_block += '<br />'
        elif node.tagName == 'a':
            text = node_to_text(node)
            href = node.getAttribute('href')
            # print((text, href))
            current_text_block += "[{text}]({href})".format(text=text, href=href)
        elif node.tagName == 'img':
            src = node.getAttribute('src')
            src = "https:" + src if src.startswith('//') else src
            filename = src.split('/')[-1]
            title = node.getAttribute('title') or node.getAttribute('alt') or filename

            print("    --> Image: " + src)
            # img = import_image(src, title)

            # if not node.getAttribute('class'):
            #     current_text_block = end_text_block(current_text_block, blocks)
            #     blocks.append(('image', img))
            # else:
            #     node.setAttribute('src', img.usage_url)
            #     print(node.toxml())

        elif node.tagName in ('em', 'i'):
            current_text_block += "*{0}*".format(node_to_text(node))
        elif node.tagName in ('strong', 'b'):
            current_text_block += "*{0}*".format(node_to_text(node))
        elif node.tagName == 'iframe':
            current_text_block = end_text_block(current_text_block, blocks)

            src = node.getAttribute('src')
            url = urlparse(src)
            if "youtube.com" in url.netloc:
                video_url = "https://youtube.com/" + url.path.rstrip('/').split('/')[-1]
                # print("Youtube Embed: " + video_url)
                blocks.append(('embed', EmbedValue(video_url)))
            elif "facebook.com/plugins/post.php" in url.netloc:
                post_url = parse_qs(url.query)['href']
                blocks.append(('embed', EmbedValue(post_url)))
            elif "store.steampowered.com" in url.netloc:
                steam_id = int(url.path.rstrip('/').split('/')[-1])
                # print("Steam Widget: https://store.steampowered.com/app/" + str(steam_id))
                blocks.append(('steam_widget', steam_id))
            else:
                current_text_block += node.toxml()
                print(node.toxml())
        elif node.tagName == 'blockquote':
            if node.getAttribute('class') == 'twitter-tweet':
                current_text_block = end_text_block(current_text_block, blocks)
                for link in node.getElementsByTagName('a')[::-1]:
                    href = link.getAttribute('href')
                    if "twitter.com/" in href and "/status/" in href:
                        # print("Twitter Embed: " + href)
                        blocks.append(('embed', EmbedValue(href)))
            else:
                current_text_block += node.toxml()
                # print(node.toxml())
        elif node.tagName == 'script':
            src = node.getAttribute('src')
            if src == "//platform.twitter.com/widgets.js":
                pass
            else:
                current_text_block += node.toxml()
                print(node.toxml())
        else:
            # current_text_block = end_text_block(current_text_block, blocks)
            current_text_block += node.toxml()
            print(node.toxml())
    return current_text_block

def get_users(data):
    users = {}
    for userdata in data['db'][0]['data']['users']:
        username = userdata['name'] if ' ' not in userdata['name'] else userdata['slug']
        users[userdata['id']] = User.objects.get(username=username)
    return users

class Command(BaseCommand):
    help = "Imports blog posts from a Ghost database dump"

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r', encoding='utf-8'), help="JSON file to load.")
        parser.add_argument('root_id', type=int, help="Page to place imported content under.")

    def handle(self, *args, **options):
        root = Page.objects.get(pk=options['root_id'])
        data = json.load(options['file'])
        posts = data['db'][0]['data']['posts']

        users = get_users(data)

        with transaction.atomic():
            for post in posts:
                title = post['title']
                slug = post['slug']
                published = arrow.get(post['published_at']).datetime
                user = users[post['author_id']]
                is_page = bool(post['page'])
                is_live = post['status'] == 'published'

                markdown = post['markdown']
                markdown = re.sub(r'!\[[^\]]*\]\(([^\)]+)\)', '<img src="\\1" />', markdown)
                tree = html5lib.parse(markdown, treebuilder="dom")

                current_text_block = ""
                blocks = []

                print("--> https://kazamatsuri.org/{0}".format(slug))
                for child in tree.getElementsByTagName('body')[0].childNodes:
                    current_text_block = handle_node(child, current_text_block, blocks)
                current_text_block = end_text_block(current_text_block, blocks)
                # print(blocks)

                body = StreamValue(DefaultStreamBlock(), blocks)
                if is_page:
                    page = StaticPage(title=title, slug=slug, body=body)
                else:
                    page = BlogPage(title=title, slug=slug, published=published, author=user, body=body)
                root.add_child(instance=page)

                if not is_live:
                    page.live = False
                    page.save()
