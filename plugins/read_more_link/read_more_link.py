import jinja2

from lxml.html import fragment_fromstring, fragments_fromstring, tostring
from lxml.etree import ParserError

from pelican import signals, contents
from pelican.utils import truncate_html_words
from pelican.generators import ArticlesGenerator


def insert_into_last_element(html, element):
    """
    Inserts the specified element at the end of the given html.

    :param html: Raw HTML string
    :param element: Raw HTML string to inject as the final child of html
    :return: str
    """
    item = fragment_fromstring(element)

    doc = fragments_fromstring(html)
    doc[-1].append(item)

    return ''.join(tostring(e).decode() for e in doc)

def insert_read_more_link(instance):
    """
    Insert an inline "read more" link into the last element of the summary

    :param instance: Content intance.
    :return:
    """

    if type(instance) != contents.Article:
        return

    site_url = instance.settings.get('SITEURL')
    summary_max_length = instance.settings.get('SUMMARY_MAX_LENGTH')
    link_text = instance.settings.get('READ_MORE_LINK_TEXT')
    link_html_template = instance.settings.get(
        'READ_MORE_LINK_TEMPLATE',
        '<a class="read-more" href="{{ url }}">{{ text }}</a>',
    )

    summary = (
        getattr(instance, '_summary', None)
        or truncate_html_words(
            instance.content,
            summary_max_length,
            end_text=f"…&nbsp;",
        )
    )

    if summary != instance.content:
        link_html = jinja2.Template(link_html_template).render(
            url=f'{site_url}/{instance.url}',
            text=link_text,
        )
        instance.metadata['summary'] = insert_into_last_element(
            summary, link_html,
        )


def run_plugin(generators):
    for generator in generators:
        if isinstance(generator, ArticlesGenerator):
            for article in generator.articles:
                insert_read_more_link(article)


def register():
    try:
        signals.all_generators_finalized.connect(run_plugin)
    except AttributeError:
        # NOTE: This may result in #314 so shouldn't really be relied on
        # https://github.com/getpelican/pelican-plugins/issues/314
        signals.content_object_init.connect(insert_read_more_link)
